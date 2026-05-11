import { ProfileMenu } from "./ProfileMenu";
import { Zap } from "lucide-react";

interface Props {
  user: any;
  onSignOut: () => void;
}

export function Header({ user, onSignOut }: Props) {
  return (
    <header className="flex items-center justify-between border-b border-border px-4 py-3 md:px-6">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Zap className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="font-display text-lg font-bold tracking-tight">PingGenius</span>
      </div>

      <p className="hidden text-sm text-muted-foreground md:block">
        Turn a LinkedIn profile into outreach in &lt;60s.
      </p>

      <div className="flex items-center gap-2">
        <ProfileMenu user={user} onSignOut={onSignOut} />
      </div>
    </header>
  );
}
