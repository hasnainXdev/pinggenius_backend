import { Shield } from "lucide-react";

export function DashboardFooter() {
  return (
    <footer className="border-t border-border px-4 py-4 md:px-6">
      <div className="flex flex-col items-center gap-2 text-center text-xs text-muted-foreground sm:flex-row sm:justify-between sm:text-left">
        <div className="flex items-center gap-1.5">
          <Shield className="h-3.5 w-3.5" />
          <span>Manual copy-paste only — no LinkedIn automation. Your data stays in your browser.</span>
        </div>
      </div>
    </footer>
  );
}
