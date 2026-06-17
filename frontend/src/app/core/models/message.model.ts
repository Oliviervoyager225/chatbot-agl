export type MessageRole = 'user' | 'assistant';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

// ── Angular-side models (camelCase) ──────────────────────────────────────────
export interface ChatRequest {
  message: string;
  sessionId?: string;
}

export interface ChatResponse {
  id?: string;
  content: string;
  sessionId?: string;
  timestamp?: string;
}

// ── Backend API models (snake_case — FastAPI) ─────────────────────────────────
export interface ApiChatRequest {
  question: string;      // champ attendu par le backend
  session_id?: string;
}

export interface ApiHealthResponse {
  status: string;
}

export interface HistoryItem {
  id: string;
  title: string;
  preview: string;
  date: Date;
  active: boolean;
}
