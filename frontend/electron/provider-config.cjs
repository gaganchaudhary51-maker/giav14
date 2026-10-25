const { URL } = require("node:url");

const LOCAL_OLLAMA_DEFAULTS = Object.freeze({
  baseUrl: "http://127.0.0.1:11434/v1",
  model: "qwen3:1.7b",
  apiKey: "ollama",
});

function validateProviderInput(input, existingApiKey = "") {
  if (!input || typeof input !== "object") throw new Error("Provider settings are required.");
  const baseUrl = String(input.baseUrl || "").trim().replace(/\/+$/, "");
  const model = String(input.model || "").trim();
  const apiKey = String(input.apiKey || existingApiKey || "").trim();
  let parsed;
  try { parsed = new URL(baseUrl); }
  catch { throw new Error("Enter a valid provider URL."); }
  const loopback = ["127.0.0.1", "localhost", "[::1]"].includes(parsed.hostname.toLowerCase());
  if (parsed.protocol !== "https:" && !(parsed.protocol === "http:" && loopback)) {
    throw new Error("Use HTTPS, or HTTP only for a provider running on this PC.");
  }
  if (parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new Error("Keep credentials and query parameters out of the provider URL.");
  }
  if (!model || model.length > 200) throw new Error("Enter a model name up to 200 characters.");
  if (!apiKey || apiKey.length > 4096) throw new Error("Enter an API key up to 4096 characters.");
  return { baseUrl, model, apiKey };
}

module.exports = { validateProviderInput, LOCAL_OLLAMA_DEFAULTS };
