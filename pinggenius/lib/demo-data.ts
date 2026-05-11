export interface DemoUser {
  email: string;
  username: string;
}

export interface DmMessage {
  role: "connection" | "cold" | "followup1" | "followup2";
  text: string;
}

export interface OutreachContext {
  url: string;
  role: string;
  company?: string;
  industry?: string;
  recent_activity?: string;
  tone: "friendly" | "direct" | "authority" | "casual";
}

export interface Sequence {
  id: string;
  profile: string;
  tone: "friendly" | "direct" | "authority" | "casual";
  generatedAt: string;
  predicted_reply_score: number;
  messages: DmMessage[];
  copied: boolean;
  sent: boolean;
  time_ms: number;
  context?: OutreachContext;
}

export function getDemoUser(): DemoUser | null {
  const raw = localStorage.getItem("pinggenius_demo_user");
  return raw ? JSON.parse(raw) : null;
}

export function setDemoUser(user: DemoUser) {
  localStorage.setItem("pinggenius_demo_user", JSON.stringify(user));
}

export function clearDemoSession() {
  localStorage.removeItem("pinggenius_demo_user");
}

// Note: Sequences are now handled through backend API only, not localStorage
export function getSequences(): Sequence[] {
  // This function is kept for compatibility but returns empty array
  // since sequences are now stored on the backend
  return [];
}

// Note: Sequences are now handled through backend API only, not localStorage
export function saveSequences(seqs: Sequence[]) {
  // This function is kept for compatibility but does nothing
  // since sequences are now stored on the backend
}

export function initDemoUser(): DemoUser {
  const existing = getDemoUser();
  if (existing) return existing;
  const user: DemoUser = { email: "hasnain@demo.local", username: "@hasnain.dev" };
  setDemoUser(user);
  return user;
}
