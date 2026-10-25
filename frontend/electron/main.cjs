const { app, BrowserWindow, dialog, ipcMain, safeStorage, session, shell } = require("electron");
const { spawn, spawnSync } = require("node:child_process");
const crypto = require("node:crypto");
const fs = require("node:fs");
const net = require("node:net");
const path = require("node:path");
const { validateProviderInput } = require("./provider-config.cjs");

const APP_NAME = "GIA Universal AI";
const HOST = "127.0.0.1";
app.setName(APP_NAME);
app.setPath("userData", path.join(app.getPath("appData"), APP_NAME));

const userData = app.getPath("userData");
const configPath = path.join(userData, "provider-config.json");
const authSecretPath = path.join(userData, "auth-secret.bin");
const logPath = path.join(userData, "logs", "backend.log");
let mainWindow;
let backendProcess;
let backendLog;
let appOrigin = "";
let backendPort;
let providerConfig = { baseUrl: "", model: "", apiKey: "", setupComplete: false };
let authSecret = "";
let quitting = false;

function statusView() {
  return {
    configured: Boolean(providerConfig.baseUrl && providerConfig.model && providerConfig.apiKey),
    setupComplete: Boolean(providerConfig.setupComplete),
    baseUrl: providerConfig.baseUrl,
    model: providerConfig.model,
    hasApiKey: Boolean(providerConfig.apiKey),
  };
}

function writeJsonAtomically(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const tempPath = `${filePath}.${process.pid}.tmp`;
  fs.writeFileSync(tempPath, JSON.stringify(value), { mode: 0o600 });
  fs.renameSync(tempPath, filePath);
}

async function loadProviderConfig() {
  if (!fs.existsSync(configPath)) return;
  try {
    const saved = JSON.parse(fs.readFileSync(configPath, "utf8"));
    const encrypted = Buffer.from(String(saved.encryptedApiKey || ""), "base64");
    const decrypted = encrypted.length ? await safeStorage.decryptStringAsync(encrypted) : null;
    const apiKey = typeof decrypted === "string" ? decrypted : String(decrypted?.result || "");
    providerConfig = {
      baseUrl: String(saved.baseUrl || ""),
      model: String(saved.model || ""),
      apiKey,
      setupComplete: Boolean(saved.setupComplete),
    };
  } catch {
    providerConfig = { baseUrl: "", model: "", apiKey: "", setupComplete: false };
  }
}

async function persistProviderConfig(next) {
  const encrypted = next.apiKey ? await safeStorage.encryptStringAsync(next.apiKey) : Buffer.alloc(0);
  writeJsonAtomically(configPath, {
    baseUrl: next.baseUrl,
    model: next.model,
    encryptedApiKey: encrypted.toString("base64"),
    setupComplete: true,
  });
}

async function loadOrCreateAuthSecret() {
  if (fs.existsSync(authSecretPath)) {
    const encrypted = fs.readFileSync(authSecretPath);
    const decrypted = await safeStorage.decryptStringAsync(encrypted);
    return typeof decrypted === "string" ? decrypted : String(decrypted?.result || "");
  }
  const secret = crypto.randomBytes(48).toString("base64url");
  const encrypted = await safeStorage.encryptStringAsync(secret);
  fs.mkdirSync(userData, { recursive: true });
  fs.writeFileSync(authSecretPath, encrypted, { mode: 0o600 });
  return secret;
}

function allocateLoopbackPort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, HOST, () => {
      const address = server.address();
      const port = address && typeof address === "object" ? address.port : 0;
      server.close((error) => error ? reject(error) : resolve(port));
    });
  });
}

function backendExecutable() {
  const override = process.env.GIA_DESKTOP_BACKEND_EXE;
  if (override) return override;
  if (app.isPackaged) return path.join(process.resourcesPath, "gia-backend.exe");
  return path.resolve(__dirname, "../../backend/dist/gia-backend.exe");
}

function stopBackend() {
  if (!backendProcess) return Promise.resolve();
  const child = backendProcess;
  backendProcess = null;
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      if (process.platform === "win32" && child.pid) {
        spawnSync("taskkill", ["/pid", String(child.pid), "/t", "/f"], { windowsHide: true });
      } else child.kill("SIGKILL");
      resolve();
    }, 2500);
    child.once("exit", () => { clearTimeout(timeout); resolve(); });
    child.kill();
  });
}

async function waitForBackend(child, url, timeoutMs = 45000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (child.exitCode !== null) throw new Error("GIA backend stopped during startup. See the local backend log.");
    try {
      const response = await fetch(`${url}/api/health`, { signal: AbortSignal.timeout(1800) });
      if (response.ok && (await response.json()).status === "healthy") return;
    } catch { /* Keep waiting while the bundled backend initializes. */ }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("GIA backend did not become ready within 45 seconds. See the local backend log.");
}

async function startBackend() {
  const executable = backendExecutable();
  if (!fs.existsSync(executable)) throw new Error(`Bundled backend was not found: ${executable}`);
  backendPort = await allocateLoopbackPort();
  appOrigin = `http://${HOST}:${backendPort}`;
  fs.mkdirSync(path.dirname(logPath), { recursive: true });
  if (backendLog !== undefined) fs.closeSync(backendLog);
  backendLog = fs.openSync(logPath, "a");
  const env = { ...process.env };
  for (const key of ["GIA_AGENT_PROVIDER_ENABLED", "GIA_AGENT_BASE_URL", "GIA_AGENT_MODEL", "GIA_AGENT_API_KEY"]) delete env[key];
  Object.assign(env, {
    GIA_ENV: "production",
    GIA_AUTH_SECRET: authSecret,
    GIA_DATA_DIR: path.join(userData, "data"),
    GIA_AUDIT_LOG: path.join(userData, "audit.jsonl"),
    GIA_WORKSPACE_ROOT: path.join(userData, "workspace"),
    GIA_FRONTEND_DIST: path.join(process.resourcesPath, "frontend"),
    GIA_DESKTOP_PORT: String(backendPort),
    GIA_AGENT_PROVIDER_ENABLED: providerConfig.apiKey ? "true" : "false",
    GIA_AGENT_BASE_URL: providerConfig.baseUrl,
    GIA_AGENT_MODEL: providerConfig.model,
    GIA_AGENT_API_KEY: providerConfig.apiKey,
  });
  backendProcess = spawn(executable, [], {
    cwd: path.dirname(executable), env, windowsHide: true,
    stdio: ["ignore", backendLog, backendLog],
  });
  const child = backendProcess;
  child.once("error", (error) => { fs.appendFileSync(logPath, `\nBackend process error: ${error.message}\n`); });
  await waitForBackend(child, appOrigin);
}

async function restartBackend() {
  await stopBackend();
  await startBackend();
}

function trustedSender(event) {
  return Boolean(mainWindow && event.sender === mainWindow.webContents &&
    event.senderFrame && isAppUrl(event.senderFrame.url));
}

function isAppUrl(value) {
  try { return new URL(value).origin === appOrigin; }
  catch { return false; }
}

function registerIpc() {
  ipcMain.handle("gia:provider-status", (event) => {
    if (!trustedSender(event)) throw new Error("Untrusted desktop settings request.");
    return statusView();
  });
  ipcMain.handle("gia:provider-skip", async (event) => {
    if (!trustedSender(event)) throw new Error("Untrusted desktop settings request.");
    providerConfig.setupComplete = true;
    await persistProviderConfig(providerConfig);
    return statusView();
  });
  ipcMain.handle("gia:provider-save", async (event, input) => {
    if (!trustedSender(event)) throw new Error("Untrusted desktop settings request.");
    if (!(await safeStorage.isAsyncEncryptionAvailable())) throw new Error("Windows secure credential storage is unavailable; the API key was not saved.");
    const previous = providerConfig;
    const previousFile = fs.existsSync(configPath) ? fs.readFileSync(configPath) : null;
    const next = { ...validateProviderInput(input, providerConfig.apiKey), setupComplete: true };
    await persistProviderConfig(next);
    providerConfig = next;
    try {
      await restartBackend();
    } catch (error) {
      providerConfig = previous;
      if (previousFile) fs.writeFileSync(configPath, previousFile);
      else fs.rmSync(configPath, { force: true });
      try { await restartBackend(); } catch { /* Keep the original startup error for the user. */ }
      throw error;
    }
    fs.appendFileSync(path.join(userData, "desktop-events.jsonl"),
      `${JSON.stringify({ at: new Date().toISOString(), event: "provider_settings_saved", model: next.model, baseUrl: next.baseUrl })}\n`);
    return statusView();
  });
}

function createMainWindow(smokeTest = false) {
  mainWindow = new BrowserWindow({
    width: 1440, height: 940, minWidth: 900, minHeight: 640,
    show: !smokeTest, autoHideMenuBar: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true, nodeIntegration: false, sandbox: true,
    },
  });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    try {
      const target = new URL(url);
      if (target.protocol === "https:" && target.hostname === "aistudio.google.com") {
        void shell.openExternal(url);
      }
    } catch { /* Invalid or untrusted destinations stay inside the app. */ }
    return { action: "deny" };
  });
  mainWindow.webContents.on("will-navigate", (event, url) => {
    if (!isAppUrl(url)) event.preventDefault();
  });
  return mainWindow.loadURL(appOrigin).then(() => mainWindow);
}

function installCsp() {
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    const headers = { ...details.responseHeaders };
    if (isAppUrl(details.url)) {
      headers["Content-Security-Policy"] = [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; " +
        "img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; " +
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
      ];
    }
    callback({ responseHeaders: headers });
  });
}

app.on("second-instance", () => { if (mainWindow) { if (mainWindow.isMinimized()) mainWindow.restore(); mainWindow.focus(); } });
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on("before-quit", (event) => {
    if (quitting) return;
    quitting = true;
    if (backendProcess) {
      event.preventDefault();
      void stopBackend().finally(() => app.quit());
    }
  });
  app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
  app.whenReady().then(async () => {
    if (!(await safeStorage.isAsyncEncryptionAvailable())) throw new Error("Windows secure storage is unavailable.");
    authSecret = await loadOrCreateAuthSecret();
    await loadProviderConfig();
    registerIpc();
    await startBackend();
    installCsp();
    const smokeTest = process.argv.includes("--smoke-test");
    await createMainWindow(smokeTest);
    if (smokeTest) { app.exit(0); return; }
  }).catch(async (error) => {
    await stopBackend();
    if (!quitting) dialog.showErrorBox("GIA could not start", `${error.message}\n\nLog: ${logPath}`);
    app.exit(1);
  });
}

app.on("will-quit", () => {
  if (backendLog !== undefined) { try { fs.closeSync(backendLog); } catch { /* Already closed. */ } }
});
