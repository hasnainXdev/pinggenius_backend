import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Sequence } from "@/lib/demo-data";

interface Props {
  sequences: Sequence[];
  unlocked: boolean;
}

export function AnalyticsPanel({ sequences, unlocked }: Props) {
  const count = sequences.length;
  const avgScore =
    count > 0
      ? Math.round(
          (sequences.reduce((sum, s) => sum + s.predicted_reply_score, 0) / count) * 100
        )
      : 0;

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Your outreach performance{" "}
        <span className="text-xs">(unlocks as you generate)</span>
      </p>
      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="rounded-xl border border-border bg-card p-4 shadow-sm"
        >
          <div className="mb-2 flex items-center gap-2 text-muted-foreground">
            <BarChart3 className="h-4 w-4" />
            <span className="text-xs font-medium">Generated DMs</span>
          </div>
          <p className="font-display text-3xl font-bold">{count}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="rounded-xl border border-border bg-card p-4 shadow-sm"
        >
          <div className="mb-2 flex items-center gap-2 text-muted-foreground">
            <TrendingUp className="h-4 w-4" />
            <span className="text-xs font-medium">Avg Reply Likelihood</span>
          </div>
          <p className="font-display text-3xl font-bold">{avgScore}%</p>
        </motion.div>
      </div>

      {/* Table area */}
      <div className="relative rounded-xl border border-border bg-card shadow-sm">
        {!unlocked && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center rounded-xl bg-card/80 backdrop-blur-sm">
            <Sparkles className="mb-2 h-8 w-8 text-primary animate-pulse-soft" />
            <p className="px-6 text-center text-sm font-medium text-foreground">
              Unlock analytics
            </p>
            <p className="mt-1 px-6 text-center text-xs text-muted-foreground">
              Generate your first outreach to see the table.
            </p>
          </div>
        )}

        <div className={cn(!unlocked && "blur-analytics")}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Time</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Profile</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Tone</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Reply %</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {unlocked && sequences.length > 0 ? (
                  sequences.map((seq) => {
                    const date = new Date(seq.generatedAt);
                    const profileName = seq.profile.split("/in/")[1]?.replace(/-/g, " ") || seq.profile;
                    return (
                      <motion.tr
                        key={seq.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="border-b border-border last:border-0"
                      >
                        <td className="whitespace-nowrap px-4 py-3 text-xs text-muted-foreground">
                          {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </td>
                        <td className="max-w-[120px] truncate px-4 py-3 text-xs font-medium capitalize">
                          {profileName}
                        </td>
                        <td className="px-4 py-3 text-xs capitalize">{seq.tone}</td>
                        <td className="px-4 py-3 text-xs">
                          {Math.round(seq.predicted_reply_score * 100)}%
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={cn(
                              "rounded-full px-2 py-0.5 text-xs font-medium",
                              seq.sent
                                ? "bg-success/10 text-success"
                                : seq.copied
                                ? "bg-primary/10 text-primary"
                                : "bg-secondary text-muted-foreground"
                            )}
                          >
                            {seq.sent ? "Sent" : seq.copied ? "Copied" : "Draft"}
                          </span>
                        </td>
                      </motion.tr>
                    );
                  })
                ) : (
                  <>
                    {[1, 2, 3].map((i) => (
                      <tr key={i} className="border-b border-border last:border-0">
                        <td className="px-4 py-3">
                          <div className="h-3 w-12 rounded bg-muted" />
                        </td>
                        <td className="px-4 py-3">
                          <div className="h-3 w-20 rounded bg-muted" />
                        </td>
                        <td className="px-4 py-3">
                          <div className="h-3 w-14 rounded bg-muted" />
                        </td>
                        <td className="px-4 py-3">
                          <div className="h-3 w-8 rounded bg-muted" />
                        </td>
                        <td className="px-4 py-3">
                          <div className="h-3 w-12 rounded bg-muted" />
                        </td>
                      </tr>
                    ))}
                  </>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
