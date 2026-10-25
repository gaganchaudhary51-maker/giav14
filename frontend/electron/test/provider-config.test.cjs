const assert = require("node:assert/strict");
const test = require("node:test");
const { validateProviderInput, LOCAL_OLLAMA_DEFAULTS } = require("../provider-config.cjs");

test("provides a local-only Ollama profile that needs no real API key", () => {
  assert.deepEqual(LOCAL_OLLAMA_DEFAULTS, {
    baseUrl: "http://127.0.0.1:11434/v1",
    model: "qwen3:1.7b",
    apiKey: "ollama",
  });
  assert.equal(validateProviderInput(LOCAL_OLLAMA_DEFAULTS).apiKey, "ollama");
});

test("normalizes HTTPS provider settings and keeps the key outside public status", () => {
  const settings = validateProviderInput({
    baseUrl: "https://api.example.test/v1/", model: "gia-model", apiKey: "secret-value",
  });
  assert.deepEqual(settings, {
    baseUrl: "https://api.example.test/v1", model: "gia-model", apiKey: "secret-value",
  });
});

test("allows HTTP only for loopback provider development", () => {
  assert.equal(validateProviderInput({ baseUrl: "http://127.0.0.1:9000/v1", model: "local", apiKey: "k" }).baseUrl,
    "http://127.0.0.1:9000/v1");
  assert.throws(() => validateProviderInput({ baseUrl: "http://remote.example/v1", model: "m", apiKey: "k" }), /HTTPS/);
});

test("rejects embedded URL credentials, query parameters, missing model, and empty key", () => {
  for (const baseUrl of ["https://user:pass@api.example/v1", "https://api.example/v1?key=secret", "https://api.example/v1#token"]) {
    assert.throws(() => validateProviderInput({ baseUrl, model: "m", apiKey: "k" }));
  }
  assert.throws(() => validateProviderInput({ baseUrl: "https://api.example/v1", model: "", apiKey: "k" }), /model name/);
  assert.throws(() => validateProviderInput({ baseUrl: "https://api.example/v1", model: "m", apiKey: "" }), /API key/);
});

test("blank key keeps an existing encrypted credential during URL/model edits", () => {
  assert.equal(validateProviderInput({ baseUrl: "https://api.example/v1", model: "new-model", apiKey: "" }, "old-key").apiKey,
    "old-key");
});
