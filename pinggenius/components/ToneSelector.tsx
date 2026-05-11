import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const TONES = [
  { value: "friendly" as const, label: "Friendly", emoji: "😊" },
  { value: "direct" as const, label: "Direct", emoji: "🎯" },
  { value: "authority" as const, label: "Authority", emoji: "👔" },
  { value: "casual" as const, label: "Casual", emoji: "😎" },
];

interface Props {
  value: "friendly" | "direct" | "authority" | "casual";
  onChange: (v: "friendly" | "direct" | "authority" | "casual") => void;
}

export function ToneSelector({ value, onChange }: Props) {
  return (
    <div className="flex rounded-lg bg-secondary p-1" role="radiogroup" aria-label="Tone selector">
      {TONES.map((tone) => (
        <button
          key={tone.value}
          role="radio"
          aria-checked={value === tone.value}
          onClick={() => onChange(tone.value)}
          className={cn(
            "relative flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200 cursor-pointer",
            value !== tone.value && "text-muted-foreground hover:text-foreground"
          )}
        >
          {value === tone.value && (
            <motion.div
              layoutId="tone-bg"
              className="absolute inset-0 rounded-md bg-card shadow-sm"
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          )}
          <span className="relative z-10">
            {tone.emoji} {tone.label}
          </span>
        </button>
      ))}
    </div>
  );
}
