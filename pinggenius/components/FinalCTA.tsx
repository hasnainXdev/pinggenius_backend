"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { Button } from "./ui/button";

export default function FinalCTA() {
  const { data: session } = useSession();

  return (
    <section className="py-28 bg-black relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.15),transparent_60%)]" />

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-4xl lg:text-5xl font-semibold text-white mb-6 tracking-tight leading-tight">
          Turn Profiles Into Conversations.
          <br />
          <span className="text-blue-400">Automatically.</span>

        </h2>
        <p className="text-lg text-white/70 mb-10 max-w-2xl mx-auto">
          PingGenius analyzes LinkedIn profiles and generates complete, 
          personalized outreach sequences that sound human and earn replies - 
          all while keeping your account safe.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          {/* {session?.user ? (
            <Link href="/dashboard">
              <Button className="cursor-pointer bg-blue-600 hover:shadow-lg hover:shadow-blue-600/30 text-white font-medium px-6 py-3 rounded-md transition-all hover:scale-105">
                Open Dashboard
              </Button>
            </Link>
          ) : ( */}
            <Link href="/join-waitlist">
              <Button className="cursor-pointer bg-blue-600 hover:shadow-lg hover:shadow-blue-600/30 text-white font-medium px-6 py-3 rounded-md transition-all hover:scale-105 flex items-center gap-2">
                Join Private Beta
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          {/* )} */}
        </div>

        <p className="mt-4 text-sm text-white/50">
          Limited beta spots • Early users get lifetime discounted pricing
        </p>
      </div>
    </section>
  );
}
