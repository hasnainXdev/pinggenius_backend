import { MessageSquare, Clock, Target, CheckCircle } from "lucide-react";
import UseCaseCard from "./UseCaseCard";

export default function UseCasesSection() {
  return (
    <section className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Where PingGenius Fits Best
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            PingGenius isn’t about blasting messages.
            It’s built for starting real conversations with people who ignore
            templates.
          </p>
        </div>

        {/* Use cases */}
        <div className="grid lg:grid-cols-2 gap-8">
          <UseCaseCard
            icon={<MessageSquare className="w-6 h-6 text-white" />}
            title="Real LinkedIn Professionals"
            subtitle="Sequences for actual roles"
            message={`Profile: Co-Founder and CEO
            
            Connection Note: "Enjoyed reading your reflections on lessons learned; it resonated. Would love to connect with a fellow Co-Founder in tech."
            
            DM: "As a CEO, balancing ambitious growth with the day-to-day challenges must be constant. How do you prioritize what to focus on with everything on your plate?"
            
            Follow-up: "Circling back – know you're busy. Was curious if the push for growth ever makes you wish for more hours in the day to tackle strategic initiatives?"`}
            result="Role-specific messaging. Maximum relevance. Account-safe."
          />

          {/* Removed for just waitlist */}
          {/*
          <UseCaseCard
            icon={<Clock className="w-6 h-6 text-white" />}
            title="Following Up Without Being Awkward"
            subtitle="Polite nudges that respect time"
            message={`Hey, just circling back
            figured this might not be a priority right now.
            Happy to reconnect later if helpful.`}
            result="No pressure. Keeps the door open."
          /> */}

          <UseCaseCard
            icon={<Target className="w-6 h-6 text-white" />}
            title="Industry-Specific Insights"
            subtitle="Context-aware messaging"
            message={`Profile: Founder & CEO, Abon | Business Operations Software
            
            Connection Note: "Intrigued by the autonomous systems you're building at Abon.AI for diverse industries."
            
            DM: "Building AI operating networks for so many industries must bring unique integration challenges. What's been the biggest hurdle in getting clients fully autonomous?"
            
            Follow-up: "Hey Khalis, just a quick bump. I imagine managing the bespoke AI solutions for so many clients keeps things busy. Curious if you've seen common patterns there."`}
            result="Deep industry knowledge. Personalized approach. Higher reply rates."
          />
        </div>
      </div>
    </section>
  );
}
