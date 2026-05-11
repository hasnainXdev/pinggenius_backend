"use client";

import React from "react";
import { CheckCircle, Mail, Zap, Rocket, ShieldCheck, Users } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useSession } from "next-auth/react";

const plans = [
    {
        name: "Free",
        price: "$0",
        icon: Mail,
        description:
            "For trying PingGenius and generating your first few outreach ideas.",
        features: [
            "Analyze LinkedIn profiles",
            "Generate outreach sequences",
            "Refine messages manually",
            "Copy-paste ready drafts",
            "No setup required",
        ],
        note: "Best for light, experimental use",
        cta: "Start Free",
    },
    {
        name: "Pro",
        price: "$19",
        icon: Zap,
        description:
            "For founders and operators who write outreach weekly and want to move faster without burnout.",
        features: [
            "Faster response generation",
            "Consistent message quality",
            "Refine messages without rethinking",
            "Reuse sequences across conversations",
            "Built for daily outreach workflows",
        ],
        highlight: true,
        note: "Most users upgrade once this becomes part of their routine",
        cta: "Upgrade to Pro",
    },
    {
        name: "Growth",
        price: "Coming Soon",
        icon: Rocket,
        description:
            "For teams scaling outreach workflows with deeper automation and insights.",
        features: [
            "Workflow-level automation",
            "Smarter personalization logic",
            "Advanced refinement controls",
            "Usage insights & optimization",
        ],
        cta: "Join Waitlist",
    },
];

const PricingSection = () => {

    const { data: session } = useSession()


    const handlePlanClick = (planName: string) => {
        if (planName === "Free" && session?.user) {
            window.location.href = "/dashboard";
        } else if (planName === "Free" && !session?.user) {
            window.location.href = "/sign-in";
        } else if (planName === "Pro" && session?.user) {
            window.location.href = process.env.LEMMON_SQUEEZY_CHECKOUT_URL as string || "https://pinggenius.lemonsqueezy.com/buy/456f581c-f01c-48e6-9964-61d0c479cbc0";
        } else if (!session?.user && planName === "Pro") {
            window.location.href = "/sign-in";
        }
    };


    const handlePortal = async () => {
        const res = await fetch('/api/customer-portal', {
            method: 'POST',
            body: JSON.stringify({ email: session?.user?.email })
        }
        );
        const data = await res.json();
        console.log(data);
        if (data.url) window.location.href = data.url;
        else alert('Failed to open portal');

        // window.location.href = "https://x.com/hasnainXdev";
    };

    return (
        <section className="py-20 bg-black text-white">
            <div className="max-w-6xl mx-auto px-6 text-center">
                <h2 className="text-3xl font-semibold text-white mb-4">
                    Simple pricing. No tricks.
                </h2>

                <p className="text-neutral-400 max-w-xl mx-auto">
                    PingGenius will offer a free tier and a paid plan once the beta is live.
                    Early users get lifetime discounted pricing.
                </p>

                {/* <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-4xl font-bold mb-4"
                >
                    Start free.{" "}
                    <span className="text-blue-500">Pay only when it delivers results.</span>
                </motion.h2>

                <p className="text-gray-400 mb-16 max-w-2xl mx-auto text-lg">
                    No credit card needed. Upgrade only when PingGenius becomes part of your daily workflow.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {plans.map((plan, index) => {
                        const Icon = plan.icon;
                        return (
                            <motion.div
                                key={plan.name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.15 }}
                                className={cn(
                                    "relative rounded-2xl border border-white/10 p-8 flex flex-col transition-all duration-300",
                                    plan.highlight &&
                                    "bg-gradient-to-br from-blue-900/20 to-blue-800/30 border-blue-500/30"
                                )}
                            >
                                {plan.highlight && (
                                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs px-3 py-1 rounded-full font-semibold shadow-md">
                                        Most Popular
                                    </span>
                                )}

                                <div className="flex justify-center mb-4">
                                    <div
                                        className={cn(
                                            "p-3 rounded-full",
                                            plan.highlight
                                                ? "bg-blue-500 shadow-md shadow-blue-400/30 text-white"
                                                : "bg-white/10 text-blue-500"
                                        )}
                                    >
                                        <Icon className="w-6 h-6" />
                                    </div>
                                </div>

                                <h3 className="text-2xl font-semibold mb-2">{plan.name}</h3>
                                <p className="text-gray-400 text-sm mb-6">{plan.description}</p>

                                <div className="text-4xl font-bold relative inline-block mb-1">
                                    <span
                                        className={cn(
                                            "bg-[length:200%_100%] animate-shimmer text-transparent bg-clip-text",
                                            plan.name === "Pro" ? "bg-gradient-to-r from-blue-400 to-blue-600" :
                                                "text-white/90"
                                        )}
                                    >
                                        {plan.price}
                                    </span>
                                    <span className="text-base text-gray-400 font-normal ml-1">/month</span>
                                </div>

                                <ul className="text-left mt-4 space-y-3">
                                    {plan.features.map((feature, i) => (
                                        <li key={i} className="flex items-center text-gray-300">
                                            <CheckCircle className="w-5 h-5 text-blue-500 mr-2" />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>

                                <button
                                    disabled={plan.name === "Growth"}
                                    className={cn(
                                        "mt-8 py-3 px-6 rounded-xl font-medium w-full transition-all",
                                        plan.highlight
                                            ? "cursor-pointer bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg hover:shadow-blue-500/40 hover:scale-105"
                                            : plan.name === "Growth"
                                                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                                                : "bg-white/10 text-white hover:bg-white/20"
                                    )}
                                    onClick={() =>
                                        plan.name === "Pro" && session?.user?.isProUser
                                            ? handlePortal()
                                            : handlePlanClick(plan.name)
                                    }
                                >
                                    {plan.name === "Pro" && session?.user?.isProUser ? "Manage Subscription" : plan.cta}
                                </button>
                            </motion.div>
                        );
                    })}
                </div>

                Trust row
                <div className="flex flex-wrap justify-center gap-6 mt-16 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-blue-500" />
                        Secure payments via Lemon Squeezy
                    </div>
                    <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-blue-500" />
                        Trusted by early builders
                    </div>
                    <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        Cancel anytime
                    </div>
                </div> */}
            </div>
        </section>
    );
};

export default PricingSection;
