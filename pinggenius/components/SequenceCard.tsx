import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import type { DmMessage } from "@/lib/demo-data";

interface Props {
  message: DmMessage;
  replyScore: number;
  index: number;
  copied?: boolean;
  isBest?: boolean;
}

export function SequenceCard({ message, replyScore, index, copied: propCopied, isBest }: Props) {
  const [localCopied, setLocalCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.text);
    setLocalCopied(true);
    toast.success("Copied!", { duration: 2000 });
    setTimeout(() => setLocalCopied(false), 2000);
  };

  const label = 
    message.role === "connection" ? "Connection Request" :
    message.role === "cold" ? "DM 1 — Cold" :
    message.role === "followup1" ? "Follow-up 1 — 2 days later" :
    "Follow-up 2 — 3 days later"; // followup2
  const scorePercent = Math.round(replyScore * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.15, duration: 0.35 }}
      className={cn(
        "rounded-xl border bg-card p-4 shadow-sm",
        isBest ? "border-primary/40 ring-1 ring-primary/20" : "border-border"
      )}
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-display text-sm font-semibold">{label}</span>
          {isBest && (
            <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
              Best performing
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <span>Predicted reply: {scorePercent}%</span>
          <div className="ml-1 h-1.5 w-16 overflow-hidden rounded-full bg-secondary">
            <motion.div
              className={cn("h-full rounded-full", isBest ? "bg-primary" : "bg-primary/70")}
              initial={{ width: 0 }}
              animate={{ width: `${scorePercent}%` }}
              transition={{ delay: index * 0.15 + 0.3, duration: 0.5 }}
            />
          </div>
        </div>
      </div>

      <p className="mb-1 text-xs text-muted-foreground/70">
        Based on tone, and profile signals
      </p>

      <p className="mb-4 text-sm leading-relaxed text-foreground/90">
        {message.text}
      </p>

      <div className="flex gap-2">
        <button
          onClick={handleCopy}
          className={cn(
            "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all duration-200 cursor-pointer",
            localCopied || propCopied
              ? "bg-success/10 text-success"
              : "bg-secondary text-foreground hover:bg-muted"
          )}
          aria-label={(localCopied || propCopied) ? "Copied" : "Copy message"}
        >
          {(localCopied || propCopied) ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          {(localCopied || propCopied) ? "Copied!" : "Copy"}
        </button>
        {/* <button
          className="flex items-center gap-1.5 rounded-lg bg-secondary px-3 py-1.5 text-xs font-medium text-foreground transition-all duration-200 hover:bg-muted cursor-pointer"
          aria-label="Save as template"
        >
          <Bookmark className="h-3.5 w-3.5" />
          Save
        </button> */}
      </div>
    </motion.div>
  );
}
