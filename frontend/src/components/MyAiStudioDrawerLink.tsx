import { Bot, ExternalLink } from "lucide-react";

const AI_STUDIO_URL = "https://aistudio.google.com/apps/30683f48-898a-4d54-8e50-0a195b832199?showPreview=true&showAssistant=true";

export function MyAiStudioDrawerLink() {
  return (
    <a
      className="external-nav"
      href={AI_STUDIO_URL}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Open My AI Studio with 12 Agents in a new tab"
    >
      <Bot size={18} strokeWidth={1.8} aria-hidden="true" />
      <span>My AI Studio — 12 Agents</span>
      <ExternalLink size={14} aria-hidden="true" />
    </a>
  );
}
