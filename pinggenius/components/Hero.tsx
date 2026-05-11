"use client";
import { ArrowRight, CheckCircle } from "lucide-react";
import { Button } from "./ui/button";
import Link from "next/link";
import { useSession } from "next-auth/react";

export default function Hero() {
  const { data: session } = useSession();

  return (
    <section className="relative bg-black py-32 overflow-hidden">
      {/* subtle background glow */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 via-transparent to-transparent" />

      <div className="relative max-w-6xl mx-auto px-4 text-center">
        {/* Headline */}
        <h1 className="text-5xl lg:text-7xl font-semibold text-white mb-6 leading-tight tracking-tight">
          Double Your LinkedIn Replies<br />
          <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
            Safely.
          </span>
        </h1>

        {/* Subheadline */}
        <p className="text-xl text-neutral-300 mb-10 max-w-2xl mx-auto">
          PingGenius analyzes LinkedIn profiles and generates complete, 
          personalized outreach sequences - from connection requests to follow-ups - 
          that sound human and earn replies.
        </p>

        {/* CTA */}
        <div className="flex flex-col items-center justify-center mb-8">
          {/* {session?.user ? (
            <Link href="/dashboard">
              <Button className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-5 transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-600/30">
                Go to Dashboard
              </Button>
            </Link>
          ) : ( */}
            <Link href="/join-waitlist">
              <Button className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-5 flex items-center gap-2 transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-600/30">
                Join (Beta)
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          {/* )} */}
        </div>

        {/* Trust bullets */}
        <div className="flex flex-wrap justify-center gap-6 text-sm text-neutral-400">
          {[
            "Account-safe approach",
            "No auto-sending ever",
            "Copy-paste ready",
            "Multiple tones",
          ].map((t) => (
            <div key={t} className="flex items-center">
              <CheckCircle className="w-4 h-4 text-blue-500 mr-2" />
              {t}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
