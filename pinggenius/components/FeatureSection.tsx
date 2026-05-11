import Image from "next/image";
import FeatureCard from "./FeatureCard";
import { Brain, Clock, TrendingUp, PlayCircle } from "lucide-react";

export default function FeaturesSection() {
  return (
    <section className="py-28 bg-black border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Heading */}
        <div className="text-center mb-14">
          <h2 className="text-4xl lg:text-5xl font-semibold text-white mb-4 leading-14">
            Why Most LinkedIn Outreach Gets Ignored And Why PingGenius Doesn’t
          </h2>
          <p className="text-lg text-neutral-400 max-w-2xl mx-auto">
            Replies don’t come from automation.
            They come from relevance, timing,
            and saying the right thing without sounding like everyone else.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">

          <FeatureCard
            icon={<Brain className="w-7 h-7 text-white" />}
            title="Complete Outreach Sequences"
            description="Generate full LinkedIn outreach sequences - from connection requests to follow-ups - 
            tailored to each prospect's role, company, and context."
            points={[
              "Connection notes, DMs, and follow-up messages",
              "Context-aware messaging that feels personal",
            ]}
          />

          <FeatureCard
            icon={<Clock className="w-7 h-7 text-white" />}
            title="Multiple Tones & Refinement"
            description="Choose from multiple tones (Friendly, Direct, Authority, Casual) and refine 
            messages based on your feedback to perfect your outreach."
            points={[
              "4 different messaging tones",
              "Refine messages with feedback",
            ]}
          />

          <FeatureCard
            icon={<TrendingUp className="w-7 h-7 text-white" />}
            title="Safe & Account-Friendly"
            description="Human-in-the-loop approach with copy-paste only - no automation that risks 
            getting your account flagged."
            points={[
              "No auto-sending (account-safe)",
              "Copy-paste ready sequences",
            ]}
          />
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-neutral-900 rounded-full border border-white/10">
            <Clock className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-medium text-neutral-300">
              Live demo opening with private beta access
            </span>
          </div>

          <p className="mt-6 text-sm text-neutral-500 max-w-xl mx-auto">
            We’re finishing the generation engine behind PingGenius.
            Beta users will see real message generation before public launch.
          </p>
        </div>


        {/* Demo */}
        {/* <div className="text-center">
          <div className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-neutral-900 rounded-full border border-white/10">
            <PlayCircle className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-medium text-neutral-300">
              Watch a real DM get written in under 10 seconds
            </span>
          </div>

          <div className="mt-8">
            <div className="w-full max-w-5xl mx-auto bg-neutral-900/60 rounded-2xl p-2">
              <Image
                src="/pinggenius.gif"
                unoptimized
                width={1000}
                height={1000}
                alt="PingGenius demo"
                className="object-cover rounded-xl"
              />
            </div>
            <p className="mt-3 text-xs text-neutral-500">
              Real generation no templates, no prewritten examples
            </p>
          </div>
        </div> */}

      </div>
    </section>
  );
}
