"use client";

import { ReactNode, useEffect } from "react";

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  useEffect(() => {
    // Force dark theme for dashboard
    document.documentElement.classList.add("dark");

    // Prevent theme switching by removing any light theme classes
    document.documentElement.classList.remove("light");

    // Store the user's preference to dark for dashboard
    localStorage.setItem("pinggenius_theme", "dark");
  }, []);

  return (
    <div className="dark bg-background text-foreground">
      {children}
    </div>
  );
}