import { useEffect, useState } from "react";

type ProviderStatus = {
  configured: boolean;
  setupComplete: boolean;
  baseUrl: string;
  model: string;
  hasApiKey: boolean;
};

type ProviderSettingsDialogProps = { autoOpen?: boolean };

export function ProviderSettingsDialog({ autoOpen = false }: ProviderSettingsDialogProps) {
  const [status, setStatus] = useState<ProviderStatus>();
  const [open, setOpen] = useState(false);
  const [baseUrl, setBaseUrl] = useState("");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const desktop = Boolean(window.giaDesktop);
  const localOllamaSelected = baseUrl === "http://127.0.0.1:11434/v1";

  async function refresh() {
    if (!window.giaDesktop) return;
    const next = await window.giaDesktop.getProviderSettings();
    setStatus(next);
    setBaseUrl(next.baseUrl || "");
    setModel(next.model || "");
    return next;
  }

  useEffect(() => {
    if (!window.giaDesktop) return;
    void refresh().then((next) => {
      if (autoOpen && !next?.setupComplete) setOpen(true);
    }).catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Could not read local provider settings."));
  }, [autoOpen]);

  async function save(event: React.FormEvent) {
    event.preventDefault();
    if (!window.giaDesktop) return;
    setBusy(true); setError(""); setNotice("");
    try {
      const next = await window.giaDesktop.saveProviderSettings({ baseUrl, model, apiKey });
      setStatus(next); setApiKey(""); setNotice("Saved securely. GIA contacts this provider only when you send a chat or agent request.");
      setOpen(false);
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Could not save provider settings.");
    } finally { setBusy(false); }
  }

  async function skip() {
    if (!window.giaDesktop) return;
    setBusy(true); setError("");
    try { setStatus(await window.giaDesktop.skipProviderSetup()); setOpen(false); }
    catch (caught: unknown) { setError(caught instanceof Error ? caught.message : "Could not save setup state."); }
    finally { setBusy(false); }
  }

  function useLocalOllama() {
    setBaseUrl("http://127.0.0.1:11434/v1");
    setModel("qwen3:1.7b");
    setApiKey("ollama");
    setError("");
    setNotice("Local preset selected. Start Ollama and run `ollama pull qwen3:1.7b`, then save this setup.");
  }

  if (!desktop) return null;
  return <>
    <div className="provider-settings-summary">
      <div><b>GIA model provider</b><small>{localOllamaSelected ? `Local Ollama preset · ${model} · Ollama must be running` : status?.configured ? `Configured · ${status.model}` : "Not configured · choose a compatible provider"}</small></div>
      <button className="secondary" type="button" onClick={() => { setError(""); setNotice(""); setOpen(true); }}>Configure provider</button>
    </div>
    {notice && <div className="success" role="status">{notice}</div>}
    {open && <div className="provider-backdrop" role="presentation">
      <form className="provider-dialog" role="dialog" aria-modal="true" aria-labelledby="provider-dialog-title" onSubmit={save}>
        <div className="eyebrow">LOCAL DESKTOP SETUP</div>
        <h2 id="provider-dialog-title">Connect GIA to a model</h2>
        <p>Connect a compatible model API. This is separate from your ChatGPT sign-in. Cloud API keys are encrypted for this Windows account and never sent to GitHub.</p>
        <button className="secondary" type="button" disabled={busy} onClick={useLocalOllama}>Use local Ollama · Qwen3 1.7B</button>
        <p>Local setup: install/start Ollama and run <code>ollama pull qwen3:1.7b</code> (about 1.4 GB). GIA then sends chat prompts to this PC's loopback API. The local API key value is only a compatibility placeholder.</p>
        <label>Compatible API URL<input autoComplete="url" inputMode="url" placeholder="https://provider.example/v1" value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} required /></label>
        <label>Model name<input autoComplete="off" placeholder="model-name" value={model} onChange={(event) => setModel(event.target.value)} required /></label>
        <label>API key<input autoComplete="new-password" type="password" placeholder={baseUrl === "http://127.0.0.1:11434/v1" ? "Local Ollama placeholder · ollama" : status?.hasApiKey ? "Stored securely · leave blank to keep current key" : "Enter your provider API key"} value={apiKey} onChange={(event) => setApiKey(event.target.value)} required={!status?.hasApiKey} /></label>
        {error && <div className="error" role="alert">{error}</div>}
        <div className="button-row"><button className="secondary" type="button" disabled={busy} onClick={() => setOpen(false)}>Cancel</button><button className="secondary" type="button" disabled={busy} onClick={() => void skip()}>Continue without chat</button><button className="primary" disabled={busy}>{busy ? "Saving…" : "Save securely"}</button></div>
      </form>
    </div>}
  </>;
}
