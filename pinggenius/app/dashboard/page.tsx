"use client";

import { useState, useCallback, useEffect } from "react";
import { useSession } from "next-auth/react";
import { signOut } from "next-auth/react";
import { Header } from "@/components/Header";
import { GenerateBox } from "@/components/GenerateBox";
import { AnalyticsPanel } from "@/components/AnalyticsPanel";
import { DashboardFooter } from "@/components/DashboardFooter";
import {
  type Sequence,
  type DemoUser,
  initDemoUser,
} from "@/lib/demo-data";
import { getSequenceById, getAllSequences } from "@/lib/api";

const Index = () => {
  const [user, setUser] = useState<any>(null);
  const [sequences, setSequences] = useState<Sequence[]>([]);
  const [unlocked, setUnlocked] = useState(false);
  const [loading, setLoading] = useState(true);

  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "loading") {
      // Still loading the session, don't initialize yet
      return;
    }

    const initializeApp = async () => {
      const u = session?.user
      setUser(u);

      try {
        // Only fetch from backend if we have a valid user ID
        let backendSequences: Sequence[] = [];
        if (session?.user?.id) {
          const userId = session.user.id;
          backendSequences = await getAllSequences(userId);
        }

        setSequences(backendSequences);
        if (backendSequences.length > 0) setUnlocked(true);
      } catch (error) {
        console.error('Error initializing sequences:', error);
        // Set empty sequences if backend fetch fails
        setSequences([]);
        setUnlocked(false);
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, [session, status]);

  const handleGenerated = useCallback((seq: Sequence) => {
    setSequences((prev) => {
      // Check if sequence already exists to avoid duplicates
      const exists = prev.some(s => s.id === seq.id);
      const next = exists
        ? prev.map(s => s.id === seq.id ? seq : s)  // Update existing
        : [seq, ...prev];  // Add new sequence

      return next;
    });
    setUnlocked(true);
  }, []);

  const handleUpdateSequence = useCallback((id: string, updates: Partial<Sequence>) => {
    setSequences((prev) => {
      const next = prev.map((s) => (s.id === id ? { ...s, ...updates } : s));
      return next;
    });
  }, []);

  const handleSignOut = async () => {
    try {
      setSequences([]);
      setUnlocked(false);

      // Sign out from NextAuth
      await signOut({ callbackUrl: '/' });
    } catch (error) {
      console.error('Error signing out:', error);
      // Fallback to clearing state
      setUser(null);
      setSequences([]);
      setUnlocked(false);
    }
  };

  if (!session?.user) {
    if (status === "loading") {
      return (
        <div className="flex min-h-screen flex-col bg-background">
          <div className="flex items-center justify-between border-b px-4 py-3 md:px-6 lg:px-8">
            <div className="flex items-center gap-2">
              <span className="font-display text-lg font-bold tracking-tight">PingGenius</span>
            </div>
          </div>
          <main className="flex-1 px-4 py-6 md:px-6 lg:py-8 flex items-center justify-center">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
              <p className="mt-2 text-muted-foreground">Loading your account...</p>
            </div>
          </main>
          <DashboardFooter />
        </div>
      );
    }
  }

  const latestSequence = sequences.length > 0 ? sequences[0] : null;

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-background">
        <Header user={session?.user} onSignOut={handleSignOut} />
        <main className="flex-1 px-4 py-6 md:px-6 lg:py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
            <p className="mt-2 text-muted-foreground">Loading your sequences...</p>
          </div>
        </main>
        <DashboardFooter />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header user={session?.user} onSignOut={handleSignOut} />

      <main className="flex-1 px-4 py-6 md:px-6 lg:py-8">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1fr_380px]">
          {/* Left: Generate Box */}
          <div>
            <GenerateBox
              onGenerated={handleGenerated}
              latestSequence={latestSequence}
              onUpdateSequence={handleUpdateSequence}
              userId={session?.user?.id}  // Use actual user ID if available, fallback to email
            />
          </div>

          {/* Right: Analytics */}
          <div>
            <AnalyticsPanel sequences={sequences} unlocked={unlocked} />
          </div>
        </div>
      </main>

      <DashboardFooter />
    </div>
  );
};

export default Index;
