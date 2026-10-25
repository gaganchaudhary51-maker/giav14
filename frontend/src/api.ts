const API = import.meta.env.VITE_API_URL || "/api";

async function request(path: string, init: RequestInit = {}) {
  const token = localStorage.getItem("gia_token");
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...init, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const payload = body.detail;
    const detail = typeof payload === "string" ? payload
      : payload && typeof payload.message === "string" ? payload.message
      : payload ? JSON.stringify(payload) : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return body;
}

export const api = {
  health: () => request("/health"),
  persistence: () => request("/system/persistence"),
  agentsRuntime: () => request("/agents/runtime"),
  signup: (name: string, email: string, password: string) =>
    request("/auth/signup", { method: "POST", body: JSON.stringify({ name, email, password }) }),
  login: (email: string, password: string) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request("/auth/me"),
  projects: async () => {
    const result = await request("/projects");
    return result.projects || result.items || [];
  },
  createProject: (name: string, description: string) =>
    request("/projects", { method: "POST", body: JSON.stringify({ name, description }) }),
  plan: (text: string, project_id?: string) =>
    request("/conversation/plan", { method: "POST", body: JSON.stringify({ text, project_id }) }),
  chat: (project_id: string, text: string, conversation_id?: string) =>
    request("/conversation/chat", { method: "POST", body: JSON.stringify({ project_id, text, conversation_id }) }),
  conversationThreads: (project_id?: string) =>
    request(`/conversation/threads${project_id ? `?project_id=${encodeURIComponent(project_id)}` : ""}`),
  conversationThread: (id: string) => request(`/conversation/threads/${encodeURIComponent(id)}`),
  createTask: (text: string) =>
    request("/tasks", { method: "POST", body: JSON.stringify({ text }) }),
  updateTaskStatus: (taskId: string, status: string) =>
    request(`/tasks/${encodeURIComponent(taskId)}/status?status=${encodeURIComponent(status)}`, { method: "POST" }),
  runAgentTeam: (task_id: string, agent_ids: string[], prompt: string) =>
    request("/agents/run", { method: "POST", body: JSON.stringify({ task_id, agent_ids, prompt }) }),
  agents: () => request("/agents"),
  ragIndex: (project_id: string, source: string, text: string, tags: string[] = []) =>
    request("/rag/index", { method: "POST", body: JSON.stringify({ project_id, source, text, tags }) }),
  ragDocuments: (project_id: string) =>
    request(`/rag/documents?project_id=${encodeURIComponent(project_id)}`),
  ragHistory: (project_id: string, source: string) =>
    request(`/rag/history?project_id=${encodeURIComponent(project_id)}&source=${encodeURIComponent(source)}`),
  ragSearch: (project_id: string, query: string, limit = 5) =>
    request("/rag/search", { method: "POST", body: JSON.stringify({ project_id, query, limit }) }),
  memoryAdd: (project_id: string, kind: string, text: string, tags: string[] = [], importance = 1) =>
    request("/memory", { method: "POST", body: JSON.stringify({ project_id, kind, text, tags, importance }) }),
  memorySearch: (project_id: string, query: string, limit = 5, tags: string[] = []) =>
    request("/memory/search", { method: "POST", body: JSON.stringify({ project_id, query, limit, tags }) }),
  events: () => request("/events/recent?limit=30"),
  voiceStart: (project_id?: string) =>
    request("/voice/sessions", { method: "POST", body: JSON.stringify({ project_id, provider: "browser", mode: "hands-free" }) }),
  voiceState: (id: string, state: string) =>
    request(`/voice/sessions/${id}/state`, { method: "POST", body: JSON.stringify({ state }) }),
  voiceTranscript: (id: string, text: string) =>
    request(`/voice/sessions/${id}/transcript`, { method: "POST", body: JSON.stringify({ text }) }),
  studioPods: () => request("/studio/pods"),
  studioUpdatePod: (podId: string, payload: { prompt: string; model: string; channels: string[]; enabled: boolean }) =>
    request(`/studio/pods/${encodeURIComponent(podId)}`, { method: "PUT", body: JSON.stringify(payload) }),
  studioEvolve: (payload: unknown) => request("/studio/agent/evolve", { method: "POST", body: JSON.stringify(payload) }),
  studioReviewEvolution: (proposalId: string, approve: boolean) =>
    request(`/studio/agent/evolve/${encodeURIComponent(proposalId)}/review`, { method: "POST", body: JSON.stringify({ approve }) }),
  studioCallCenterDemo: () => request("/studio/call-center/demo"),
};

// Universal Agent Pods & Multi-Channel Studio (tenant-scoped; independent of legacy RAG/memory).

export const studioApi = {
  pods: () => request("/studio/pods"),
  updatePod: (podId: string, payload: { prompt: string; model: string; channels: string[]; enabled: boolean }) =>
    request(`/studio/pods/${encodeURIComponent(podId)}`, { method: "PUT", body: JSON.stringify(payload) }),
  evolve: (payload: unknown) => request("/studio/agent/evolve", { method: "POST", body: JSON.stringify(payload) }),
  reviewEvolution: (proposalId: string, approve: boolean) =>
    request(`/studio/agent/evolve/${encodeURIComponent(proposalId)}/review`, { method: "POST", body: JSON.stringify({ approve }) }),
  callCenterDemo: () => request("/studio/call-center/demo"),
};
