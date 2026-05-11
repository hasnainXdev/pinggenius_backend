import { ReactNode } from "react";

interface UseCaseCardProps {
  icon: ReactNode;
  title: string;
  subtitle: string;
  message: string;
  result: string | ReactNode;
}

export default function UseCaseCard({
  icon,
  title,
  subtitle,
  message,
  result,
}: UseCaseCardProps) {
  return (
    <div className="group bg-neutral-900/60 backdrop-blur border border-white/10 rounded-xl p-8 transition-all duration-300 hover:border-white/20">
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        <div
          className={`w-11 h-11 rounded-lg flex items-center justify-center bg-blue-600/20 text-blue-400`}
        >
          {icon}
        </div>

        <div>
          <h3 className="text-lg font-semibold text-white leading-tight">
            {title}
          </h3>
          <p className="text-sm text-white/60">
            {subtitle}
          </p>
        </div>
      </div>

      {/* Message preview */}
      <div className="relative bg-black/40 border border-white/10 rounded-lg p-4 mb-4">
        <div className={`absolute left-0 top-0 h-full w-0.5 bg-blue-500`} />
        <p className="text-sm text-white/80 italic leading-relaxed">
          “{message}”
        </p>
      </div>

      {/* Result */}
      <div className="text-sm text-white/70">
        {typeof result === "string" ? (
          <span className={`text-blue-400`}>{result}</span>
        ) : (
          result
        )}
      </div>
    </div>
  );
}
