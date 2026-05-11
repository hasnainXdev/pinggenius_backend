import { useState, useCallback, useRef } from "react";
import { Loader2, Sparkles, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { ToneSelector } from "./ToneSelector";
import { SequenceCard } from "./SequenceCard";
import { generateCompleteSequence } from "@/lib/api";
import { handleNetworkError } from "@/lib/network-utils";
import type { Sequence, OutreachContext } from "@/lib/demo-data";

interface Props {
  onGenerated: (seq: Sequence) => void;
  latestSequence: Sequence | null;
  onUpdateSequence: (id: string, updates: Partial<Sequence>) => void;
  userId: string | null | undefined;  // ID of the current user
}

const LINKEDIN_REGEX = /^https?:\/\/(www\.)?linkedin\.com\/in\/[\w-]+\/?$/i;

function FieldError({ message }: { message: string | null }) {
  return (
    <AnimatePresence>
      {message && (
        <motion.p
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="mt-1 flex items-center gap-1 text-xs text-destructive"
        >
          <AlertCircle className="h-3 w-3 shrink-0" />
          {message}
        </motion.p>
      )}
    </AnimatePresence>
  );
}

export function GenerateBox({ onGenerated, latestSequence, onUpdateSequence, userId }: Props) {
  const [url, setUrl] = useState("");
  const [role, setRole] = useState("");
  const [company, setCompany] = useState("");
  const [industry, setIndustry] = useState("");
  const [recentActivity, setRecentActivity] = useState("");
  const [showOptional, setShowOptional] = useState(false);
  const [tone, setTone] = useState<"friendly" | "direct" | "authority" | "casual">("friendly");
  const [length, setLength] = useState<"short" | "medium">("short");
  const [loading, setLoading] = useState(false);
  const [timeTaken, setTimeTaken] = useState<number | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ url?: string; role?: string; context?: string }>({});
  const [cooldownUntil, setCooldownUntil] = useState<number | null>(null);
  const generateTimestamps = useRef<number[]>([]);
  const isFirstGeneration = useRef(!latestSequence);

  const cooldownRemaining = cooldownUntil ? Math.max(0, Math.ceil((cooldownUntil - Date.now()) / 1000)) : 0;

  // Keep cooldown timer ticking
  const [, setTick] = useState(0);
  const tickRef = useRef<ReturnType<typeof setInterval>>(null);
  const startCooldownTimer = useCallback((until: number) => {
    setCooldownUntil(until);
    if (tickRef.current) clearInterval(tickRef.current);
    tickRef.current = setInterval(() => {
      if (Date.now() >= until) {
        setCooldownUntil(null);
        clearInterval(tickRef.current!);
      }
      setTick((t) => t + 1);
    }, 1000);
  }, []);

  const handleGenerate = useCallback(async () => {
    // Validate fields
    const errors: { url?: string; role?: string; context?: string } = {};

    if (!url.trim()) {
      errors.url = "Oops   drop a LinkedIn URL so we know who to write to 🔗";
    } else if (!LINKEDIN_REGEX.test(url.trim())) {
      errors.url = "Hmm, that doesn't look like a LinkedIn profile URL double-check? 🤔";
    }

    if (!role.trim()) {
      errors.role = "We need their role to write a killer opener what do they do? 💼";
    } else if (role.trim().length < 2) {
      errors.role = "That's a bit short give us a real role like 'Founder' or 'Head of Growth' ✍️";
    }

    if (!company.trim() && !industry.trim()) {
      errors.context = "Add at least a company or industry it makes the hook way more personal 🎯";
      if (!showOptional) setShowOptional(true);
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      const firstError = errors.url || errors.role || errors.context || "";
      toast.error(firstError, { duration: 3000 });
      return;
    }

    setFieldErrors({});

    // Throttle: max 3 in 20s
    const now = Date.now();
    generateTimestamps.current = generateTimestamps.current.filter((t) => now - t < 20000);
    if (generateTimestamps.current.length >= 3) {
      const oldestInWindow = Math.min(...generateTimestamps.current);
      const waitUntil = oldestInWindow + 20000;
      startCooldownTimer(waitUntil);
      toast("Easy tiger 🐯 you're generating too fast. Grab a coffee, back in a few seconds.", {
        duration: 5000,
      });
      return;
    }
    generateTimestamps.current.push(now);

    setLoading(true);
    setTimeTaken(null);

    const ctx: OutreachContext = {
      url,
      role: role.trim(),
      company: company.trim() || undefined,
      industry: industry.trim() || undefined,
      recent_activity: recentActivity.trim() || undefined,
      tone,
    };

    try {
      // Start measuring time for the API call
      const startTime = Date.now();

      const result = await generateCompleteSequence(ctx, userId!);

      const endTime = Date.now();
      const timeTakenMs = endTime - startTime;

      const seq: Sequence = {
        ...result,
        id: result.id || crypto.randomUUID(), // Use backend ID if available, otherwise generate one
        copied: result.copied ?? false,
        sent: result.sent ?? false,
      };

      setTimeTaken(timeTakenMs);
      onGenerated(seq);
      setUrl("");
      setRole("");
      setCompany("");
      setIndustry("");
      setRecentActivity("");
      if (isFirstGeneration.current) {
        toast.success("Nice your first outreach is ready. Copy & send 🚀");
        isFirstGeneration.current = false;
      } else {
        toast.success("DM generated check your analytics 🎉");
      }
    } catch (error: any) {
      console.error("Error generating sequence:", error);

      // Check if it's a network error
      if (handleNetworkError(error)) {
        return; // Early return since network error is already handled
      }

      // Display user-friendly error message
      let errorMessage = error.message || "Yikes something broke on our end 😅 Give it another shot?";

      // If the error message contains actionable tips, format them nicely
      if (error.message && error.message.includes(" - ")) {
        const [mainMsg, tip] = error.message.split(" - ");
        errorMessage = `${mainMsg} 💡 Tip: ${tip}`;
      }

      toast.error(errorMessage, { duration: 4000 });
    } finally {
      setLoading(false);
    }
  }, [url, role, company, industry, recentActivity, tone, length, onGenerated, startCooldownTimer]);

  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
        <h2 className="mb-4 font-display text-lg font-bold">Generate Outreach</h2>

        <div className="space-y-4">
          <div>
            <label htmlFor="profile-url" className="mb-1.5 block text-sm font-medium">
              LinkedIn Profile URL
            </label>
            <input
              id="profile-url"
              type="url"
              placeholder="https://www.linkedin.com/in/jane-doe"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className={`w-full rounded-lg border bg-background px-3 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring ${fieldErrors.url ? "border-destructive" : "border-input"}`}
              disabled={loading}
            />
            <FieldError message={fieldErrors.url || null} />
          </div>

          <div>
            <label htmlFor="role-input" className="mb-1.5 block text-sm font-medium">
              Their Role <span className="text-destructive">*</span>
            </label>
            <input
              id="role-input"
              type="text"
              placeholder="e.g. Founder, Head of Growth, CTO"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className={`w-full rounded-lg border bg-background px-3 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring ${fieldErrors.role ? "border-destructive" : "border-input"}`}
              disabled={loading}
            />
            <FieldError message={fieldErrors.role || null} />
          </div>

          {/* Optional context fields */}
          <button
            type="button"
            onClick={() => setShowOptional(!showOptional)}
            className="flex items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground cursor-pointer"
          >
            {showOptional ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            {showOptional ? "Hide" : "Add"} context for a better hook
          </button>

          <AnimatePresence>
            {showOptional && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-3 overflow-hidden"
              >
                <div>
                  <label htmlFor="company-input" className="mb-1 block text-xs font-medium text-muted-foreground">
                    Company
                  </label>
                  <input
                    id="company-input"
                    type="text"
                    placeholder="e.g. Stripe, Notion, their startup name"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label htmlFor="industry-input" className="mb-1 block text-xs font-medium text-muted-foreground">
                    Industry
                  </label>
                  <input
                    id="industry-input"
                    type="text"
                    placeholder="e.g. fintech, developer tools, health tech"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label htmlFor="activity-input" className="mb-1 block text-xs font-medium text-muted-foreground">
                    Recent Activity
                  </label>
                  <input
                    id="activity-input"
                    type="text"
                    placeholder="e.g. launched v2, spoke at Config, wrote about AI"
                    value={recentActivity}
                    onChange={(e) => setRecentActivity(e.target.value)}
                    className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    disabled={loading}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <FieldError message={fieldErrors.context || null} />

          <div>
            <label className="mb-1.5 block text-sm font-medium">Tone</label>
            <ToneSelector value={tone} onChange={setTone} />
          </div>


          <motion.button
            onClick={handleGenerate}
            disabled={loading || cooldownRemaining > 0}
            whileTap={{ scale: 0.97 }}
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 font-display text-sm font-semibold text-primary-foreground shadow-md transition-shadow duration-200 hover:shadow-lg disabled:opacity-70 cursor-pointer"
            aria-label={`Generate DM for ${url || "profile"}`}
          >
            {cooldownRemaining > 0 ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Hold on… {cooldownRemaining}s
              </>
            ) : loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span aria-live="polite" role="progressbar">Generating…</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate DM
              </>
            )}
          </motion.button>

          <AnimatePresence>
            {timeTaken !== null && !loading && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-xs text-muted-foreground"
              >
                Generated in {(timeTaken / 1000).toFixed(1)}s
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      </div>

      <AnimatePresence>
        {latestSequence && (
          <div className="space-y-3">
            {[...latestSequence.messages]
              .sort((a, b) => {
                // Define the order of message types
                const order = { connection: 0, cold: 1, followup1: 2, followup2: 3 };
                return (order[a.role] || 99) - (order[b.role] || 99);
              })
              .map((msg, i) => (
                <SequenceCard
                  key={`${latestSequence.id}-${msg.role}`}
                  message={msg}
                  replyScore={latestSequence.predicted_reply_score}
                  index={i}
                  copied={latestSequence.copied}
                  isBest={i === 0}
                />
              ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
