import type { Sequence, OutreachContext } from "./demo-data";

// --- Cold DM templates keyed by tone ---
// Placeholders: {firstName}, {hook}, {cta}

const COLD_TEMPLATES: Record<OutreachContext["tone"], string[]> = {
  friendly: [
    "Hey {firstName}! 👋 {hook} Your perspective is refreshing — would be great to chat sometime!",
    "Hi {firstName}! {hook} Thought we might have some fun ideas to exchange — no agenda, just good conversation.",
  ],
  direct: [
    "{firstName} — {hook} I have a tool that could save you 10+ hours/week on this. Worth a quick look?",
    "{firstName} — {hook} I think you'd get value from what we've built. Can I share a 2-min demo?",
  ],
  authority: [
    "{firstName} — {hook} I have a tool that could save you 10+ hours/week on this. Worth a quick look?",
    "{firstName} — {hook} I think you'd get value from what we've built. Can I share a 2-min demo?",
  ],
  casual: [
    "Hey {firstName} — {hook} I'm working on something in a similar space and would love to swap notes. No pitch, just curious about your approach.",
    "Hi {firstName} — {hook} It resonated with what I've been building. Would love to connect and trade ideas if you're open to it.",
  ],
};

const FOLLOWUP_TEMPLATES = [
  "Quick follow-up, {firstName} — didn't want my last message to get lost in the noise. Totally understand if the timing's off. Happy to share more context if you're open to it.",
  "Hey {firstName}, circling back on my earlier note. No pressure at all — just thought our paths might cross well. Let me know if you'd like to connect.",
];

// --- Hook generation from context ---

function buildHook(ctx: OutreachContext, firstName: string): string {
  // Priority: recent_activity > company+role > industry+role > role only
  if (ctx.recent_activity) {
    return `Saw your recent work on ${ctx.recent_activity} — really interesting stuff.`;
  }
  if (ctx.company && ctx.industry) {
    return `Noticed you're a ${ctx.role} at ${ctx.company} in the ${ctx.industry} space — that caught my eye.`;
  }
  if (ctx.company) {
    return `Saw you're a ${ctx.role} at ${ctx.company} — really cool what you're building there.`;
  }
  if (ctx.industry) {
    return `Your work as a ${ctx.role} in ${ctx.industry} caught my attention.`;
  }
  return `Your background as a ${ctx.role} stood out — I'm curious about what you're working on.`;
}

function extractFirstName(url: string): string {
  const match = url.match(/\/in\/([a-zA-Z0-9-]+)/);
  if (match) {
    return match[1].split("-")[0].charAt(0).toUpperCase() + match[1].split("-")[0].slice(1);
  }
  return "there";
}

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

// --- Reply likelihood from context completeness + tone modifier ---
// Range: 55–95%, clustering 70–80%

function computeScore(ctx: OutreachContext): number {
  // Context completeness score (0–4 points)
  let completeness = 1; // role is always present
  if (ctx.company) completeness += 1;
  if (ctx.industry) completeness += 1;
  if (ctx.recent_activity) completeness += 1;

  // Tone modifier
  const toneBoost: Record<OutreachContext["tone"], number> = {
    friendly: 0.06,
    direct: 0.01,
    authority: 0.03,
    casual: 0.05,
  };

  // Base: completeness maps to 0.60–0.82 range
  const base = 0.60 + (completeness / 4) * 0.22 + toneBoost[ctx.tone];

  // Add small deterministic jitter from URL length
  const urlLen = ctx.url.replace(/[^a-zA-Z]/g, "").length;
  const jitter = ((urlLen % 17) / 17) * 0.08 - 0.04; // ±4%

  return Math.max(0.55, Math.min(0.95, Math.round((base + jitter) * 100) / 100));
}

export async function generateSequence(
  ctx: OutreachContext,
  _previewLength: "short" | "medium"
): Promise<Omit<Sequence, "id" | "copied" | "sent">> {
  const firstName = extractFirstName(ctx.url);
  const hook = buildHook(ctx, firstName);

  const coldTemplate = pick(COLD_TEMPLATES[ctx.tone]);
  const coldText = coldTemplate
    .replace(/{firstName}/g, firstName)
    .replace(/{hook}/g, hook);

  const followupTemplate = pick(FOLLOWUP_TEMPLATES);
  const followupText = followupTemplate.replace(/{firstName}/g, firstName);

  const score = computeScore(ctx);

  // Simulate generation time (1.5–3s)
  const delay = 1500 + Math.random() * 1500;
  await new Promise((r) => setTimeout(r, delay));

  return {
    profile: ctx.url,
    tone: ctx.tone,
    generatedAt: new Date().toISOString(),
    predicted_reply_score: score,
    time_ms: Math.round(delay),
    context: ctx,
    messages: [
      { role: "connection", text: `Hi ${firstName}, I noticed your profile and thought we might have some common interests in this field.` }, // Connection request
      { role: "cold", text: coldText }, // First DM
      { role: "followup1", text: followupText }, // First follow-up
      { role: "followup2", text: `Hi ${firstName}, hope you're doing well! No pressure at all, but I'd still love to connect if you're open to it.` }, // Second follow-up
    ],
  };
}
