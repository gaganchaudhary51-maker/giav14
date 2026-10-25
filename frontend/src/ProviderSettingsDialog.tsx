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

  if (!desktop) return null;
  return <>
    <div className="provider-settings-summary">
      <div><b>GIA model provider</b><small>{status?.configured ? `Configured · ${status.model}` : "Not configured · chat needs a compatible API key"}</small></div>
      <button className="secondary" type="button" onClick={() => { setError(""); setNotice(""); setOpen(true); }}>Configure provider</button>
    </div>
    {notice && <div className="success" role="status">{notice}</div>}
    {open && <div className="provider-backdrop" role="presentation">
      <form className="provider-dialog" role="dialog" aria-modal="true" aria-labelledby="provider-dialog-title" onSubmit={save}>
        <div className="eyebrow">LOCAL DESKTOP SETUP</div>
        <h2 id="provider-dialog-title">Connect GIA to a model</h2>
        <p>GIA uses its own account and a compatible model API. This is separate from your ChatGPT sign-in. The key is encrypted for this Windows account and never sent to GitHub.</p>
        <label>Compatible API URL<input autoComplete="url" inputMode="url" placeholder="https://provider.example/v1" value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} required /></label>
        <label>Model name<input autoComplete="off" placeholder="model-name" value={model} onChange={(event) => setModel(event.target.value)} required /></label>
        <label>API key<input autoComplete="new-password" type="password" placeholder={status?.hasApiKey ? "Stored securely · leave blank to keep current key" : "Enter your provider API key"} value={apiKey} onChange={(event) => setApiKey(event.target.value)} required={!status?.hasApiKey} /></label>
        {error && <div className="error" role="alert">{error}</div>}
        <div className="button-row"><button className="secondary" type="button" disabled={busy} onClick={() => setOpen(false)}>Cancel</button><button className="secondary" type="button" disabled={busy} onClick={() => void skip()}>Continue without chat</button><button className="primary" disabled={busy}>{busy ? "Saving…" : "Save securely"}</button></div>
      </form>
    </div>}
  </>;
}
