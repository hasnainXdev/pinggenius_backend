"use client"

import { SessionProvider, SessionProviderProps } from "next-auth/react"
import { ReactNode } from "react"
import Navbar from "./Navbar"
import { usePathname } from "next/navigation"

export default function Providers({ children }: { children: ReactNode }) {

  const pathname = usePathname()
  const isProtectedRoute = pathname.startsWith("/dashboard");

  return (
    <SessionProvider>
      {!isProtectedRoute && <Navbar />}
      {children}
    </SessionProvider>
  );
}
