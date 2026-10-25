import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, BookOpen, Bot, BrainCircuit, FolderKanban, House, Menu, MessageSquarePlus, Plus, Send, Settings2, Sparkles, X, type LucideIcon } from "lucide-react";
import { api } from "./api";
import { MyAiStudioDrawerLink } from "./components/MyAiStudioDrawerLink";
import { ProviderSettingsDialog } from "./ProviderSettingsDialog";
import "./styles.css";

type Project = { id: string; name: string; description?: string; status?: string };
type Agent = { id?: string; name?: string; role?: string; description?: string; capabilities?: string[] };
type StudioPod = { id: string; name: string; role: string; description: string; prompt: string; model: string; models: string[]; channels: string[]; enabled: boolean; updated_at?: string };
type ChatThread = { id: string; project_id: string; title: string; updated_at: string };
type ChatMessage = { role: "user" | "assistant"; content: string; created_at?: string };
type Section = "Home" | "Projects" | "Agents" | "Studio" | "Knowledge" | "Memory" | "Settings";
type SpeechRecognitionLike = any;

const nav: { icon: LucideIcon; label: Section }[] = [
  { icon: House, label: "Home" },
  { icon: FolderKanban, label: "Projects" },
  { icon: Bot, label: "Agents" },
  { icon: Sparkles, label: "Studio" },
  { icon: BookOpen, label: "Knowledge" },
  { icon: BrainCircuit, label: "Memory" },
  { icon: Settings2, label: "Settings" },
];

function App() {
  const reduceMotion = useReducedMotion();
  const [user, setUser] = useState<any>();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState("");
  const [input, setInput] = useState("");
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [conversationId, setConversationId] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [mode, setMode] = useState<"login" | "signup">(() => window.giaDesktop ? "signup" : "login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [section, setSection] = useState<Section>(() => window.location.pathname === "/studio" ? "Studio" : "Home");
  const [menu, setMenu] = useState(false);
  const [createProjectOpen, setCreateProjectOpen] = useState(false);
  const [projectNameDraft, setProjectNameDraft] = useState("");
  const [voice, setVoice] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const [voiceSession, setVoiceSession] = useState("");
  const [agents, setAgents] = useState<Agent[]>([]);
  const [studioPods, setStudioPods] = useState<StudioPod[]>([]);
  const [studioPodId, setStudioPodId] = useState("");
  const [studioModel, setStudioModel] = useState("Puck");
  const [studioPrompt, setStudioPrompt] = useState("");
  const [studioChannels, setStudioChannels] = useState<string[]>(["Web Chat"]);
  const [studioEnabled, setStudioEnabled] = useState(true);
  const [studioEvolution, setStudioEvolution] = useState<any>();
  const [studioMetrics, setStudioMetrics] = useState({ failure: "", missed: "", bottleneck: "", aht: "0" });
  const [studioTranscript, setStudioTranscript] = useState<any[]>([]);
  const [studioRunPrompt, setStudioRunPrompt] = useState("");
  const [studioRunResult, setStudioRunResult] = useState<any>();
  const [studioRunBusy, setStudioRunBusy] = useState(false);
  const [studioDemoNote, setStudioDemoNote] = useState("Demo mode · no live telephony or customer records connected");
  const [systemStatus, setSystemStatus] = useState<any>();
  const [ragSource, setRagSource] = useState("");
  const [ragText, setRagText] = useState("");
  const [ragTags, setRagTags] = useState("");
  const [ragQuery, setRagQuery] = useState("");
  const [ragResults, setRagResults] = useState<any[]>([]);
  const [ragDocuments, setRagDocuments] = useState<any[]>([]);
  const [ragHistory, setRagHistory] = useState<any[]>([]);
  const [memoryText, setMemoryText] = useState("");
  const [memoryTags, setMemoryTags] = useState("");
  const [memoryImportance, setMemoryImportance] = useState(3);
  const [memoryQuery, setMemoryQuery] = useState("");
  const [memoryResults, setMemoryResults] = useState<any[]>([]);
  const recognitionRef = useRef<SpeechRecognitionLike>(null);
  const sideRef = useRef<HTMLElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const projectNameRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const activeProject = projects.find((project) => project.id === selected);

  async function refresh() {
    try {
      const current = await api.me();
      setUser(current);
      const [projectList, threadData] = await Promise.all([api.projects(), api.conversationThreads()]);
      setProjects(projectList);
      setThreads(threadData.threads || []);
    } catch {
      localStorage.removeItem("gia_token");
      setUser(undefined);
    }
  }

  useEffect(() => { void refresh(); }, []);
  useEffect(() => {
    const onPopState = () => setSection(window.location.pathname === "/studio" ? "Studio" : "Home");
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);
  useEffect(() => {
    if (!menu || !window.matchMedia("(max-width: 760px)").matches) return;
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusables = () => Array.from(sideRef.current?.querySelectorAll<HTMLElement>(
      'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ) || []);
    requestAnimationFrame(() => focusables()[0]?.focus());
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { setMenu(false); return; }
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) return;
      if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items[items.length - 1].focus(); }
      else if (!event.shiftKey && document.activeElement === items[items.length - 1]) { event.preventDefault(); items[0].focus(); }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
      if (previouslyFocused?.isConnected) previouslyFocused.focus();
      else menuButtonRef.current?.focus();
    };
  }, [menu]);
  useEffect(() => {
    if (createProjectOpen) requestAnimationFrame(() => projectNameRef.current?.focus());
  }, [createProjectOpen]);
  useEffect(() => {
    if (section === "Studio" && user) void loadStudio();
  }, [section, user]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "end" }); }, [chatMessages, busy, reduceMotion]);
  useEffect(() => {
    if (!user || !selected) { setRagDocuments([]); return; }
    void api.ragDocuments(selected).then((result) => setRagDocuments(result.documents || [])).catch(() => setRagDocuments([]));
  }, [user, selected]);


  async function auth(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = mode === "login"
        ? await api.login(email, password)
        : await api.signup(name, email, password);
      localStorage.setItem("gia_token", result.token);
      await refresh();
    } catch (caught: any) {
      setError(caught.message || "Sign-in failed. Check the API server and your details.");
    }
  }

  function navigate(nextSection: Section) {
    setSection(nextSection);
    window.history.pushState({}, "", nextSection === "Studio" ? "/studio" : "/");
    setMenu(false);
    setError("");
    setNotice("");
    if (nextSection === "Agents") void loadAgents();
    if (nextSection === "Settings") void loadSystemStatus();
  }

  function startNewChat() {
    setConversationId("");
    setChatMessages([]);
    setInput("");
    setSection("Home");
    window.history.pushState({}, "", "/");
    setMenu(false);
    setError("");
    setNotice("");
  }

  async function openConversation(id: string) {
    setBusy(true); setError("");
    try {
      const thread = await api.conversationThread(id);
      setConversationId(thread.id);
      setChatMessages(thread.messages || []);
      setSelected(thread.project_id);
      setSection("Home");
      window.history.pushState({}, "", "/");
      setMenu(false);
    } catch (caught: any) { setError(caught.message || "Could not load conversation."); }
    finally { setBusy(false); }
  }

  function createProject() {
    setProjectNameDraft("");
    setCreateProjectOpen(true);
  }

  async function saveProject(event: React.FormEvent) {
    event.preventDefault();
    const projectName = projectNameDraft.trim();
    if (!projectName) return;
    setBusy(true);
    setError("");
    try {
      const project = await api.createProject(projectName, "");
      setProjects((items) => [project, ...items]);
      setSelected(project.id);
      setCreateProjectOpen(false);
      setSection("Projects");
      window.history.pushState({}, "", "/");
      setNotice("Project created.");
    } catch (caught: any) {
      setError(caught.message);
    } finally { setBusy(false); }
  }

  async function submitChat(override?: string) {
    const text = (override ?? input).trim();
    if (!text || busy) return;
    if (!selected) {
      setError("Create or select a project first so the work has a clear home.");
      setSection("Projects");
      return;
    }
    setInput("");
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await api.chat(selected, text, conversationId || undefined);
      setConversationId(result.conversation_id);
      setChatMessages(result.messages || []);
      setThreads((items) => {
        const next: ChatThread = { id: result.conversation_id, project_id: result.project_id, title: result.title, updated_at: new Date().toISOString() };
        return [next, ...items.filter((item) => item.id !== next.id)].slice(0, 40);
      });
      setInput("");
      if (voice) speak(result.answer || "Done.");
    } catch (caught: any) {
      setError(caught.message);
    } finally { setBusy(false); }
  }

  function speak(text: string) {
    if (!("speechSynthesis" in window) || !text) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text.slice(0, 1200));
    utterance.lang = "en-IN";
    utterance.onstart = () => { if (voiceSession) void api.voiceState(voiceSession, "SPEAKING").catch(() => {}); };
    utterance.onend = () => { if (voiceSession) void api.voiceState(voiceSession, "IDLE").catch(() => {}); };
    window.speechSynthesis.speak(utterance);
  }

  async function stopVoice() {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch { /* already stopped */ }
      recognitionRef.current = null;
    }
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    if (voiceSession) await api.voiceState(voiceSession, "IDLE").catch(() => {});
    setVoice(false);
    setVoiceSession("");
  }

  async function startVoice() {
    setVoiceError("");
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError("Speech recognition is not supported by this browser. You can type your request instead.");
      return;
    }
    try {
      const session = await api.voiceStart(selected || undefined);
      setVoiceSession(session.id);
      await api.voiceState(session.id, "LISTENING");
      const recognition = new SpeechRecognition();
      recognition.lang = "en-IN";
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.onresult = async (event: any) => {
        const transcript = Array.from(event.results).map((item: any) => item[0]?.transcript || "").join(" ").trim();
        if (!transcript) return;
        setInput(transcript);
        try { await api.voiceTranscript(session.id, transcript); await submitChat(transcript); }
        catch (caught: any) { setVoiceError(caught.message); }
      };
      recognition.onerror = (event: any) => { setVoiceError(event.error || "Speech recognition failed"); setVoice(false); };
      recognition.onend = () => { recognitionRef.current = null; setVoice(false); };
      recognitionRef.current = recognition;
      recognition.start();
      setVoice(true);
    } catch (caught: any) {
      setVoiceError(caught.message || "Could not start voice session");
      setVoice(false);
    }
  }

  async function loadStudio() {
    setBusy(true); setError("");
    try {
      const result = await api.studioPods();
      const pods = result.pods || [];
      setStudioPods(pods);
      const chosen = pods.find((pod: StudioPod) => pod.id === studioPodId) || pods[0];
      if (chosen) {
        setStudioPodId(chosen.id); setStudioPrompt(chosen.prompt); setStudioModel(chosen.model);
        setStudioChannels(chosen.channels || []); setStudioEnabled(Boolean(chosen.enabled));
      }
      const demo = await api.studioCallCenterDemo();
      setStudioTranscript(demo.transcript || []); setStudioDemoNote(demo.note || "Demo mode");
    } catch (caught: any) { setError(caught.message || "Could not load Studio configuration."); }
    finally { setBusy(false); }
  }

  function selectStudioPod(id: string) {
    const pod = studioPods.find((item) => item.id === id);
    if (!pod) return;
    setStudioPodId(id); setStudioPrompt(pod.prompt); setStudioModel(pod.model);
    setStudioChannels(pod.channels || []); setStudioEnabled(Boolean(pod.enabled)); setStudioEvolution(undefined);
  }

  async function saveStudioPod(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      const result = await api.studioUpdatePod(studioPodId, { prompt: studioPrompt, model: studioModel, channels: studioChannels, enabled: studioEnabled });
      setStudioPods((items) => items.map((pod) => pod.id === studioPodId ? result.pod : pod));
      setNotice("Studio pod configuration saved for this signed-in tenant. No live call was initiated.");
    } catch (caught: any) { setError(caught.message || "Could not save pod configuration."); }
    finally { setBusy(false); }
  }

  async function proposeStudioEvolution(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setStudioEvolution(undefined);
    try {
      const result = await api.studioEvolve({ pod_id: studioPodId,
        failure_logs: studioMetrics.failure ? [studioMetrics.failure] : [],
        missed_prompts: studioMetrics.missed ? [studioMetrics.missed] : [],
        bottlenecks: studioMetrics.bottleneck ? [studioMetrics.bottleneck] : [],
        aht_seconds: Number(studioMetrics.aht || 0) });
      setStudioEvolution(result);
      setNotice("Evolution proposal generated. Active prompt remains unchanged until you approve it.");
    } catch (caught: any) { setError(caught.message || "Evolution provider is not configured."); }
    finally { setBusy(false); }
  }

  async function reviewStudioEvolution(approve: boolean) {
    if (!studioEvolution?.proposal_id) return;
    setBusy(true); setError("");
    try {
      const result = await api.studioReviewEvolution(studioEvolution.proposal_id, approve);
      setNotice(approve ? "Reviewed prompt proposal applied." : "Prompt proposal rejected; active prompt unchanged.");
      setStudioEvolution(undefined);
      if (approve) await loadStudio();
    } catch (caught: any) { setError(caught.message || "Could not review evolution proposal."); }
    finally { setBusy(false); }
  }

  async function loadAgents() {
    setBusy(true); setError("");
    try { setAgents((await api.agents()).agents || []); }
    catch (caught: any) { setError(caught.message); }
    finally { setBusy(false); }
  }

  async function runSelectedStudioPod(event: React.FormEvent) {
    event.preventDefault();
    const taskText = studioRunPrompt.trim();
    const pod = studioPods.find((item) => item.id === studioPodId);
    if (!taskText || !pod || !selected) {
      setError(!selected ? "Select a project before running an agent." : "Choose a pod and enter a task.");
      return;
    }
    if (!pod.enabled) { setError("This pod is paused. Enable it before running."); return; }
    setStudioRunBusy(true); setError(""); setNotice(""); setStudioRunResult(undefined);
    let task: any;
    try {
      task = await api.createTask(taskText);
      if (task.status === "APPROVAL_REQUIRED") {
        setStudioRunResult({ status: "APPROVAL_REQUIRED", task_id: task.id, requested_count: 0, completed_count: 0, results: [] });
        setNotice("This task requires approval before execution. It has not been run.");
        return;
      }
      await api.updateTaskStatus(task.id, "EXECUTING");
      const podToAgent: Record<string, string> = {
        "ritu-reception": "voice", "rahul-sales": "planner", "sophia-whatsapp": "backend",
        "lucas-growth": "research", "swarn-auditor": "analytics", "boat-commerce": "backend",
        "social-marketing": "research", "google-web": "research", "branding-agent": "ui",
        "graphic-designer": "ui"
      };
      const result = await api.runAgentTeam(task.id, [podToAgent[pod.id] || "planner"], `${pod.prompt}\n\nUSER TASK:\n${taskText}`);
      setStudioRunResult(result);
      await api.updateTaskStatus(task.id, result.completed_count > 0 ? "EXECUTED" : "FAILED");
      setNotice(result.status === "COMPLETED" ? "Agent execution completed and task status updated." : `Agent execution status: ${result.status}. Check the result details.`);
    } catch (caught: any) {
      setError(caught.message || "Agent run failed. Check provider configuration and task status.");
      if (task?.id) {
        try { await api.updateTaskStatus(task.id, "FAILED"); } catch { /* preserve original error */ }
      }
    } finally { setStudioRunBusy(false); }
  }

  async function loadSystemStatus() {
    setBusy(true); setError("");
    try {
      const [health, persistence, provider] = await Promise.all([api.health(), api.persistence(), api.agentsRuntime()]);
      setSystemStatus({ health, persistence, provider });
    } catch (caught: any) { setError(caught.message); }
    finally { setBusy(false); }
  }

  async function indexKnowledge(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) { setError("Select a project before indexing knowledge."); return; }
    setBusy(true); setError(""); setNotice("");
    try {
      const tags = ragTags.split(",").map((tag) => tag.trim()).filter(Boolean).slice(0, 20);
      const result = await api.ragIndex(selected, ragSource.trim(), ragText.trim(), tags);
      setNotice(`Indexed ${result.indexed} chunks from ${result.source}. Previous versions are retained.`);
      setRagText("");
      setRagDocuments((await api.ragDocuments(selected)).documents || []);
    } catch (caught: any) { setError(caught.message); }
    finally { setBusy(false); }
  }

  async function loadRagHistory(source: string) {
    if (!selected) return;
    try { setRagHistory((await api.ragHistory(selected, source)).versions || []); }
    catch (caught: any) { setError(caught.message); }
  }

  async function searchKnowledge(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) { setError("Select a project before searching knowledge."); return; }
    setBusy(true); setError("");
    try { setRagResults((await api.ragSearch(selected, ragQuery.trim())).items || []); }
    catch (caught: any) { setError(caught.message); }
    finally { setBusy(false); }
  }

  async function saveMemory(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) { setError("Select a project before saving a memory."); return; }
    setBusy(true); setError(""); setNotice("");
    try {
      const tags = memoryTags.split(",").map((tag) => tag.trim()).filter(Boolean).slice(0, 20);
      await api.memoryAdd(selected, "personal-note", memoryText.trim(), tags, memoryImportance);
      setNotice("Memory saved to durable project storage.");
      setMemoryText("");
    } catch (caught: any) { setError(caught.message); }
    finally { setBusy(false); }
  }

  async function searchMemory(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) { setError("Select a project before searching memory."); return; }
    setBusy(true); setError("");
    try { setMemoryResults((await api.memorySearch(selected, memoryQuery.trim())).items || []); }
    catch (caught: any) { setError(caught.message); }
    finally { setBusy(false); }
  }

  if (!user) {
    return <div className="auth">
      <form onSubmit={auth}>
        <div className="brand auth-brand"><div className="orb">G</div><div><b>GIA</b></div></div>
        <h1>{mode === "login" ? "Sign in" : "Create account"}</h1>
        {mode === "signup" && <label>Name<input autoComplete="name" placeholder="Your name" value={name} onChange={(event) => setName(event.target.value)} required /></label>}
        <label>Email<input autoComplete="email" placeholder="you@example.com" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
        <label>Password<input autoComplete={mode === "login" ? "current-password" : "new-password"} placeholder="At least 8 characters" type="password" minLength={mode === "signup" ? 8 : 1} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        <button className="primary wide" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? "Sign in to GIA" : "Create account"}</button>
        {error && <div className="error" role="alert">{error}</div>}
        <button type="button" className="link" onClick={() => { setError(""); setMode(mode === "login" ? "signup" : "login"); }}>{mode === "login" ? "New to GIA? Create an account" : "Already have an account? Sign in"}</button>
      </form>
      <ProviderSettingsDialog autoOpen />
    </div>;
  }

  return <div className="app">
    <aside id="workspace-navigation" ref={sideRef} className={`side ${menu ? "open" : ""}`} role={menu ? "dialog" : undefined} aria-modal={menu || undefined} aria-label="Workspace navigation">
      <div className="drawer-brand-row">
      <div className="brand"><div className="orb">G</div><div><b>GIA</b></div></div>
        <button className="drawer-close" onClick={() => setMenu(false)} aria-label="Close navigation"><X size={19} /></button>
      </div>
      <button className="new-chat-button" type="button" onClick={startNewChat}><MessageSquarePlus size={18} aria-hidden="true" />New chat</button>
      <div className="workspace-label">WORKSPACE</div>
      <nav aria-label="Main navigation">
        {nav.map((item) => { const Icon = item.icon; const label = item.label === "Projects" ? "Workspaces" : item.label === "Home" ? "Chat" : item.label; return <button className={section === item.label ? "sel" : ""} onClick={() => navigate(item.label)} aria-current={section === item.label ? "page" : undefined} key={item.label}><Icon size={18} strokeWidth={1.8} aria-hidden="true" />{label}</button>; })}
        <MyAiStudioDrawerLink />
      </nav>
      <div className="sidebar-workspaces">
        <div className="sidebar-group-title"><small>WORKSPACES</small><button type="button" onClick={() => void createProject()} aria-label="Create workspace"><Plus size={16} /></button></div>
        {projects.map((project) => <button type="button" key={project.id} className={selected === project.id ? "active" : ""} onClick={() => { setSelected(project.id); setConversationId(""); setChatMessages([]); setSection("Home"); setMenu(false); }} title={project.name}><FolderKanban size={15} aria-hidden="true" /><span>{project.name}</span></button>)}
        {!projects.length && <small className="sidebar-empty">No workspaces</small>}
      </div>
      <div className="recent-chats">
        <small>RECENT</small>
        {threads.filter((thread) => !selected || thread.project_id === selected).slice(0, 12).map((thread) => <button type="button" key={thread.id} className={conversationId === thread.id ? "active" : ""} onClick={() => void openConversation(thread.id)} title={thread.title}><span>{thread.title}</span></button>)}
      </div>
      <div className="bottom"><button className="profile" onClick={() => { localStorage.removeItem("gia_token"); setUser(undefined); }}>{user.name} <span>Sign out</span></button></div>
    </aside>
    <AnimatePresence>{menu && <motion.button className="drawer-scrim" aria-label="Close navigation" onClick={() => setMenu(false)} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />}</AnimatePresence>

    <main className="main-area">
      <header className="topbar">
        <button ref={menuButtonRef} className="hamb" onClick={() => setMenu(!menu)} aria-label="Toggle navigation" aria-controls="workspace-navigation" aria-expanded={menu}><Menu size={19} /></button>
        <div><b>{activeProject?.name || "GIA"}</b><span className="crumb"> / {section === "Home" ? "Chat" : section === "Projects" ? "Workspaces" : section}</span></div>
        {section === "Home" && <button type="button" className="topbar-new-chat" onClick={startNewChat} aria-label="Start a new chat"><Plus size={18} /><span>New chat</span></button>}
      </header>

      {error && <div className="global-message error-message" role="alert"><span>!</span>{error}<button onClick={() => setError("")} aria-label="Dismiss error">×</button></div>}
      {notice && <div className="global-message success-message" role="status"><span>✓</span>{notice}<button onClick={() => setNotice("")} aria-label="Dismiss notice">×</button></div>}

      {section === "Home" && <section className="chat-page" aria-label="Conversation">
        <div className={`chat-transcript ${chatMessages.length ? "has-messages" : "empty-state"}`} aria-live="polite">
          {!chatMessages.length && <div className="chat-welcome"><div className="chat-mark">G</div><h1>What can I help with?</h1>{!selected && <button type="button" onClick={() => { navigate("Projects"); }}>Choose a workspace</button>}</div>}
          {chatMessages.map((message, index) => <article className={`chat-message ${message.role}`} key={`${message.created_at || "turn"}-${index}`}><div className="chat-avatar">{message.role === "assistant" ? "G" : (user.name || "U").slice(0, 1).toUpperCase()}</div><div className="chat-message-content">{message.content}</div></article>)}
          {busy && <div className="chat-message assistant"><div className="chat-avatar">G</div><div className="chat-thinking"><i /><i /><i /></div></div>}
          <div ref={chatEndRef} />
        </div>
        <div className={`chat-composer ${voice ? "listen" : ""}`}>
          <textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void submitChat(); } }} placeholder={selected ? "Message GIA…" : "Choose a workspace to start"} aria-label="Message GIA" disabled={!selected} />
          <div className="chat-composer-actions">
            <button type="button" className={voice ? "voice on" : "voice"} onClick={() => voice ? void stopVoice() : void startVoice()} aria-label={voice ? "Stop voice input" : "Start voice input"}>{voice ? "◉" : "◌"}</button>
            <button type="button" className="chat-send" disabled={busy || !selected || !input.trim()} onClick={() => void submitChat()} aria-label="Send message"><Send size={17} /></button>
          </div>
          {voiceError && <div className="inline-warning">{voiceError}</div>}
        </div>
      </section>}

      {section === "Projects" && <section className="page">
        <div className="eyebrow">WORKSPACES</div><h1 className="page-title">Projects</h1><p className="page-lede">Keep related goals, knowledge and memories together. Select one project to scope your next action.</p>
        <button className="primary" onClick={() => void createProject()}>＋ Create project</button>
        <div className="project-grid full-grid">{projects.map((project) => <button className={`project-card ${selected === project.id ? "selected" : ""}`} onClick={() => setSelected(project.id)} key={project.id}><span className="project-icon">◈</span><span className="project-copy"><b>{project.name}</b><small>{project.description || "Project workspace"}</small><em>{selected === project.id ? "SELECTED" : project.status || "ACTIVE"}</em></span><span className="arrow">↗</span></button>)}</div>
      </section>}

      {section === "Agents" && <section className="page">
        <div className="eyebrow">ORCHESTRATION</div><h1 className="page-title">Agents</h1><p className="page-lede">Inspect the agent registry exposed by the current GIA API. Registry presence does not mean a live tool run has happened.</p>
        <div className="toolbar"><button className="secondary" disabled={busy} onClick={() => void loadAgents()}>↻ Refresh agents</button><span className="muted">{agents.length} registered</span></div>
        <div className="agent-grid">{agents.map((agent, index) => <div className="agent-card" key={agent.id || agent.name || index}><span className="agent-avatar">◈</span><div><b>{agent.name || agent.role || agent.id || `Agent ${index + 1}`}</b><p>{agent.description || "Registered agent in the current GIA backend."}</p>{agent.capabilities?.length ? <div className="tag-list">{agent.capabilities.map((capability) => <span className="tag" key={capability}>{capability}</span>)}</div> : null}</div></div>)}{!agents.length && <div className="empty-card"><b>No agent data loaded</b><p>Refresh to query the authenticated backend registry.</p><button className="secondary" onClick={() => void loadAgents()}>Load agents</button></div>}</div>
      </section>}

      {section === "Studio" && <section className="studio-page">
        <div className="studio-heading"><div><div className="eyebrow">UNIVERSAL AGENT PODS · MULTI-CHANNEL</div><h1>Agent Studio</h1><p>Configure the ten requested pods, prompts, audio engine selection and channel availability. This controls configuration only; external telephony and messaging are not connected yet.</p></div><button className="studio-primary" disabled={busy} onClick={() => void loadStudio()}>Refresh pods</button></div>
        <form className="studio-execution-panel" onSubmit={runSelectedStudioPod}>
          <div><span className="studio-kicker">REAL AGENT EXECUTION</span><h2>Run selected pod</h2><p>Uses the signed-in account, selected project, task ownership checks and configured model provider. Provider-offline is shown as an error, never as a fake success.</p></div>
          <label>Task for this pod<textarea value={studioRunPrompt} onChange={(e) => setStudioRunPrompt(e.target.value)} placeholder="Describe the work this agent should perform…" rows={3} required /></label>
          <button className="studio-primary" disabled={studioRunBusy || busy || !selected || !studioPodId || !studioRunPrompt.trim()}>{studioRunBusy ? "Running agent…" : "▶ Run agent"}</button>
          {!selected && <small>Select a project from the sidebar before running.</small>}
          {studioRunResult && <div className="studio-run-result"><b>Run status: {studioRunResult.status}</b><small>Task: {studioRunResult.task_id} · Completed: {studioRunResult.completed_count}/{studioRunResult.requested_count}</small>{(studioRunResult.results || []).map((r: any, i: number) => <div key={`${r.agent_id}-${i}`}><b>{r.agent_id} — {r.status}</b><p>{r.output || r.error || "No output returned."}</p>{r.provider && <small>Provider: {r.provider} · Model: {r.model}</small>}</div>)}</div>}
        </form>
        <div className="studio-summary"><div><small>REGISTERED PODS</small><b>{studioPods.length || 10}</b><span>10 requested profiles</span></div><div><small>CHANNELS</small><b>3</b><span>Voice Call · WhatsApp · Web Chat</span></div><div><small>CONFIGURATION</small><b>Tenant scoped</b><span>Saved in local SQLite</span></div><div><small>TELEPHONY</small><b>Demo</b><span>Provider setup pending</span></div></div>
        <div className="studio-layout">
          <div className="studio-pod-list"><h2>Agent pods</h2>{studioPods.map((pod) => <button type="button" key={pod.id} className={`studio-pod-choice ${studioPodId === pod.id ? "active" : ""}`} onClick={() => selectStudioPod(pod.id)}><span className="studio-pod-avatar">{pod.name.split(" ").map((x) => x[0]).slice(0,2).join("")}</span><span><b>{pod.name}</b><small>{pod.role}</small><em>{pod.enabled ? "Active" : "Paused"} · {pod.model} · {(pod.channels || []).join(", ") || "No channels"}</em></span></button>)}</div>
          <form className="studio-editor" onSubmit={saveStudioPod}>
            {(() => { const pod = studioPods.find((item) => item.id === studioPodId); return <><div className="studio-editor-head"><div><span className="studio-kicker">POD CONFIGURATION</span><h2>{pod?.name || "Select an agent pod"}</h2><p>{pod?.description || "Choose a profile to edit its configuration."}</p></div><label className="studio-toggle"><input type="checkbox" checked={studioEnabled} onChange={(e) => setStudioEnabled(e.target.checked)} /> Enabled</label></div>
            <label>System prompt<textarea value={studioPrompt} onChange={(e) => setStudioPrompt(e.target.value)} rows={7} required maxLength={12000} /></label>
            <div className="studio-form-grid"><label>Audio engine<select value={studioModel} onChange={(e) => setStudioModel(e.target.value)}>{["Kore","Fenrir","Zephyr","Puck"].map((m) => <option key={m}>{m}</option>)}</select><small>Selection stored; engine runtime adapter not yet wired.</small></label><div><label>Available channels</label><div className="studio-channel-options">{["Voice Call","WhatsApp","Web Chat"].map((channel) => <label key={channel}><input type="checkbox" checked={studioChannels.includes(channel)} onChange={(e) => setStudioChannels((xs) => e.target.checked ? [...xs, channel] : xs.filter((x) => x !== channel))} /> {channel}</label>)}</div></div></div>
            <div className="studio-footer"><span>Tenant-scoped config · Existing personal RAG/memory untouched</span><button className="studio-primary" disabled={busy || !studioPodId}>Save configuration</button></div></>; })()}
          </form>
        </div>
        <div className="studio-call-center"><div className="studio-call-title"><div><span className="studio-kicker">CALL CENTER</span><h2>Real-time operations HUD</h2></div><span className="studio-demo-status">Demo data · not a live call</span></div>
          <div className="studio-split"><div className="studio-pane"><h3>Live transcript feed</h3><div className="studio-transcript">{studioTranscript.map((line: any, i: number) => <div key={i} className="studio-transcript-line"><time>{line.time}</time><div><b>{line.speaker}</b><p>{line.text}</p></div></div>)}<p className="studio-demo-note">{studioDemoNote}</p></div></div>
          <div className="studio-pane"><h3>Customer context & next actions</h3><div className="studio-context-card"><small>CUSTOMER HISTORY</small><p>No customer records connected. Tenant-safe lookup placeholder.</p></div><div className="studio-context-card"><small>RECOMMENDED SCRIPTS</small><ul><li>Confirm preferred date and time</li><li>Verify calendar availability before confirming</li><li>Offer manager handover if requested</li></ul></div><div className="studio-queue"><div><small>WAITING QUEUE</small><b>3</b></div><div><small>OLDEST WAIT</small><b>01:14</b></div><span>Demo metrics</span></div></div></div>
        </div>
        <form className="studio-evolution" onSubmit={proposeStudioEvolution}><div><span className="studio-kicker">PROMPT EVOLUTION</span><h2>Performance-based prompt proposal</h2><p>Uses Gemini only when configured. New prompts remain pending review; no automatic live rewrite.</p></div><div className="studio-evolution-fields"><label>Failure log<input value={studioMetrics.failure} onChange={(e) => setStudioMetrics({...studioMetrics, failure:e.target.value})} placeholder="Observed failure (optional)" /></label><label>Missed prompt<input value={studioMetrics.missed} onChange={(e) => setStudioMetrics({...studioMetrics, missed:e.target.value})} placeholder="Missed customer intent (optional)" /></label><label>Bottleneck<input value={studioMetrics.bottleneck} onChange={(e) => setStudioMetrics({...studioMetrics, bottleneck:e.target.value})} placeholder="Conversation bottleneck (optional)" /></label><label>AHT seconds<input type="number" min="0" max="86400" value={studioMetrics.aht} onChange={(e) => setStudioMetrics({...studioMetrics, aht:e.target.value})} /></label></div><button className="studio-primary" disabled={busy || !studioPodId}>Generate proposal</button>
          {studioEvolution && <div className="studio-proposal"><div><b>Proposal · {studioEvolution.status}</b><p>{studioEvolution.proposed_prompt}</p><small>Active prompt changed: {String(studioEvolution.active_prompt_changed)}</small></div><div className="studio-proposal-actions"><button type="button" className="studio-primary" disabled={busy} onClick={() => void reviewStudioEvolution(true)}>Approve & apply</button><button type="button" className="studio-secondary" disabled={busy} onClick={() => void reviewStudioEvolution(false)}>Reject</button></div></div>}
        </form>
        <div className="studio-compliance"><b>Operational-only policy</b><p>This studio is for bookings, scheduling, logistics and business operations. It excludes medical LIMS accession codes, tube/vial processing, sample tracking, lab-record interpretation, symptom interpretation and clinical advice.</p></div>
      </section>}

      {section === "Knowledge" && <section className="page">
        <div className="eyebrow">RETRIEVAL-AUGMENTED GENERATION</div><h1 className="page-title">Knowledge</h1><p className="page-lede">Index text into the selected project’s current RAG store, then test retrieval. Use a project with data you are comfortable storing locally.</p>
        {!selected && <div className="inline-warning">Select a project from the left sidebar before indexing or searching. RAG is stored in SQLite with per-user/project isolation and source version history. Configure backups before production use.</div>}
        <div className="two-column">
          <form className="surface-card form-card" onSubmit={indexKnowledge}><div className="card-heading"><span className="project-icon">＋</span><div><b>Index knowledge</b><small>Add a text source to this project's RAG index.</small></div></div><label>Source name<input value={ragSource} onChange={(event) => setRagSource(event.target.value)} placeholder="e.g. project-notes.txt" required /></label><label>Tags (comma separated)<input value={ragTags} onChange={(event) => setRagTags(event.target.value)} placeholder="e.g. product, security, requirements" /></label><label>Text content<textarea value={ragText} onChange={(event) => setRagText(event.target.value)} placeholder="Paste the knowledge you want GIA to retrieve…" rows={7} required /></label><button className="primary" disabled={busy || !selected}>Index text</button><div className="card-heading"><div><b>Indexed sources</b><small>Re-indexing a source preserves the previous version.</small></div></div><div className="result-list">{ragDocuments.map((doc) => <div className="retrieval-item" key={doc.id}><b>{doc.source}</b><p>Version {doc.version} · {doc.character_count} characters · {(doc.tags || []).join(", ") || "No tags"}</p><button className="secondary" type="button" onClick={() => void loadRagHistory(doc.source)}>View version history</button></div>)}{!ragDocuments.length && <div className="muted">No sources indexed for this project yet.</div>}{ragHistory.length > 0 && <div className="retrieval-item"><b>Version history</b>{ragHistory.map((version) => <p key={version.version}>v{version.version} · {version.character_count} characters {version.current ? "· current" : ""}</p>)}</div>}</div></form>
          <form className="surface-card form-card" onSubmit={searchKnowledge}><div className="card-heading"><span className="project-icon">⌕</span><div><b>Test retrieval</b><small>Search indexed chunks in the selected project.</small></div></div><label>Search query<input value={ragQuery} onChange={(event) => setRagQuery(event.target.value)} placeholder="What should the system recall?" required /></label><button className="secondary" disabled={busy || !selected}>Search knowledge</button><div className="result-list">{ragResults.map((item, index) => <div className="retrieval-item" key={item.id || index}><b>{item.source || item.title || `Result ${index + 1}`}</b><p>{item.text || item.content || JSON.stringify(item)}</p><small>Relevance: {item.score ?? item.similarity ?? "not provided"}</small></div>)}{!ragResults.length && <div className="muted">Search results will appear here.</div>}</div></form>
        </div>
      </section>}

      {section === "Memory" && <section className="page">
        <div className="eyebrow">PERSONAL CONTEXT</div><h1 className="page-title">Memory</h1><p className="page-lede">Save and search project-scoped notes. This interface uses the current GIA memory API; it does not automatically import old memories from another installation.</p>
        {!selected && <div className="inline-warning">Select a project from the left sidebar before saving or searching memory. Memory is stored in SQLite with per-user/project isolation, tags, summaries and importance-aware recall. Configure backups before production use.</div>}
        <div className="two-column">
          <form className="surface-card form-card" onSubmit={saveMemory}><div className="card-heading"><span className="project-icon">✧</span><div><b>Save a memory</b><small>Store a note in the selected project's current memory store.</small></div></div><label>Memory text<textarea value={memoryText} onChange={(event) => setMemoryText(event.target.value)} placeholder="Write a preference, project decision or useful fact…" rows={6} required /></label><label>Tags (comma separated)<input value={memoryTags} onChange={(event) => setMemoryTags(event.target.value)} placeholder="e.g. decision, product, safety" /></label><label>Importance<select value={memoryImportance} onChange={(event) => setMemoryImportance(Number(event.target.value))}><option value={1}>1 · Low</option><option value={2}>2</option><option value={3}>3 · Normal</option><option value={4}>4</option><option value={5}>5 · Critical</option></select></label><button className="primary" disabled={busy || !selected}>Save memory</button></form>
          <form className="surface-card form-card" onSubmit={searchMemory}><div className="card-heading"><span className="project-icon">⌕</span><div><b>Recall memory</b><small>Search saved memories and related RAG context.</small></div></div><label>What should GIA remember?<input value={memoryQuery} onChange={(event) => setMemoryQuery(event.target.value)} placeholder="Search a saved fact or decision…" required /></label><button className="secondary" disabled={busy || !selected}>Search memory</button><div className="result-list">{memoryResults.map((item, index) => <div className="retrieval-item" key={item.id || index}><b>{item.kind || item.source || `Memory ${index + 1}`}</b><p>{item.text || item.content || JSON.stringify(item)}</p><small>Importance {item.importance ?? 1} · {(item.tags || []).join(", ") || "No tags"}</small></div>)}{!memoryResults.length && <div className="muted">Memory search results will appear here.</div>}</div></form>
        </div>
      </section>}

      {section === "Settings" && <section className="page">
        <div className="eyebrow">SYSTEM CONFIGURATION</div><h1 className="page-title">Settings & health</h1><p className="page-lede">Check the current API and persistence mode. This page reports what the backend says; it does not infer production readiness from a running server alone.</p>
        <ProviderSettingsDialog />
        <div className="button-row"><button className="secondary" disabled={busy} onClick={() => void loadSystemStatus()}>↻ Check system status</button></div>
        <div className="settings-grid">{systemStatus ? <>
          <div className="surface-card status-card"><small>API HEALTH</small><b className={systemStatus.health?.status === "healthy" ? "green" : "warning"}>{systemStatus.health?.status || "Unknown"}</b><p>Response from the FastAPI health endpoint.</p></div>
          <div className="surface-card status-card"><small>PROJECT STORAGE</small><b>{systemStatus.persistence?.backend || "Unknown"}</b><p>SQLite also stores users, tasks, approvals, execution records, RAG chunks and project memories. Check the configured database path and test backups before production use.</p></div>
          <div className="surface-card status-card"><small>MODEL PROVIDER</small><b className={systemStatus.provider?.configured ? "green" : "warning"}>{systemStatus.provider?.configured ? "Configured" : "Not configured"}</b><p>{systemStatus.provider?.configured ? `${systemStatus.provider.provider} · ${systemStatus.provider.model}` : "Set a compatible API URL, model and key in the desktop app. No provider request is made by this status check."}</p></div>
        </> : <div className="empty-card"><b>Status not checked yet</b><p>Run a health and persistence check to see the backend's current report.</p><button className="secondary" onClick={() => void loadSystemStatus()}>Check status</button></div>}
        </div>
      </section>}
    </main>


    <AnimatePresence>
      {createProjectOpen && <motion.div className="project-dialog-backdrop" role="presentation" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(event) => { if (event.target === event.currentTarget) setCreateProjectOpen(false); }}>
        <motion.form className="project-dialog" role="dialog" aria-modal="true" aria-labelledby="create-project-title" onSubmit={saveProject} onKeyDown={(event) => {
          if (event.key === "Escape") { event.preventDefault(); setCreateProjectOpen(false); return; }
          if (event.key !== "Tab") return;
          const focusable = Array.from(event.currentTarget.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled])'));
          if (!focusable.length) return;
          if (event.shiftKey && document.activeElement === focusable[0]) { event.preventDefault(); focusable[focusable.length - 1].focus(); }
          else if (!event.shiftKey && document.activeElement === focusable[focusable.length - 1]) { event.preventDefault(); focusable[0].focus(); }
        }} initial={reduceMotion ? false : { opacity: 0, y: 16, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 8, scale: 0.98 }} transition={{ duration: 0.2 }}>
          <div className="dialog-heading"><div><small>WORKSPACE</small><h2 id="create-project-title">Create a project</h2></div><button type="button" className="dialog-close" aria-label="Close dialog" onClick={() => setCreateProjectOpen(false)}><X size={19} /></button></div>
          <label htmlFor="new-project-name">Project name</label>
          <input ref={projectNameRef} id="new-project-name" value={projectNameDraft} onChange={(event) => setProjectNameDraft(event.target.value)} placeholder="e.g. Product launch" maxLength={100} required />
          <p>Tasks, knowledge, and memory will be scoped to this project.</p>
          <div className="dialog-actions"><button type="button" className="secondary" onClick={() => setCreateProjectOpen(false)}>Cancel</button><button className="primary" disabled={busy || !projectNameDraft.trim()}>{busy ? "Creating…" : "Create project"}<ArrowRight size={16} /></button></div>
        </motion.form>
      </motion.div>}
    </AnimatePresence>
  </div>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
