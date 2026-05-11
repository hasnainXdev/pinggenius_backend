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
        description: "Perfect to test PingGenius and automate your first outreach.",
        features: [
            // TODO: add this later
            // "50 email analyses / month",
            // "Basic Gmail sync",
            "2 outreach sequence",
            "1 Follow-up on sequence",
            "2 contacts",
            "Friendly tone only",
        ],
        cta: "Start for Free",
    },
    {
        name: "Pro",
        price: "$19",
        icon: Zap,
        description: "Ideal for small teams who want to automate smarter and faster.",
        features: [
            // TODO: add this later
            // "500 email analyses / month",
            // "Faster Gmail sync",
            "100 outreach sequences",
            "5 follow-ups on each sequence",
            "100 contacts",
            "All tones unlocked",
            "Advanced analytics",
            "priority support",
        ],
        highlight: true,
        cta: "Upgrade to Pro",
    },
    {
        name: "Growth",
        price: "$29",
        icon: Rocket,
        description: "Scale your outreach with unlimited automation and insights.",
        features: [
            "Unlimited email analyses",
            "Unlimited sequences & contacts",
            "Priority Gmail sync (real-time)",
            "Smart scheduling (coming soon)",
            "Advanced analytics",
            "Early AI access",
        ],
        cta: "Coming Soon 🚀",
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
        <section className="py-20 bg-gradient-to-b from-white to-gray-50">
            <div className="max-w-6xl mx-auto px-6 text-center">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-4xl font-bold text-gray-900 mb-4"
                >
                    Start free.{" "}
                    <span className="text-primary">
                        Pay only when it delivers results.
                    </span>
                </motion.h2>

                <p className="text-gray-600 mb-16 max-w-2xl mx-auto text-lg">
                    Start free. No credit card needed. Upgrade only when PingGenius
                    becomes part of your daily workflow.
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
                                    "relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 p-8 flex flex-col",
                                    plan.highlight &&
                                    "border-2 border-transparent bg-gradient-to-br from-primary/10 via-primary/10 to-primary/10 shadow-[0_0_25px_rgba(37,99,235,0.25)] hover:border-primary/50"
                                )}
                            >
                                {plan.highlight && (
                                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-primary to-primary text-white text-xs px-3 py-1 rounded-full font-semibold shadow-md">
                                        Most Popular
                                    </span>
                                )}

                                <div className="flex justify-center mb-4">
                                    <div
                                        className={cn(
                                            "p-3 rounded-full",
                                            plan.highlight
                                                ? "bg-gradient-to-r from-primary to-primary shadow-md shadow-primary/30"
                                                : "bg-gray-100"
                                        )}
                                    >
                                        <Icon
                                            className={cn(
                                                "w-6 h-6",
                                                plan.highlight ? "text-white" : "text-primary"
                                            )}
                                        />
                                    </div>
                                </div>

                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                                    {plan.name}
                                </h3>
                                <p className="text-gray-500 text-sm mb-6">{plan.description}</p>

                                <div className="text-4xl font-bold text-gray-900 mb-1">
                                    {plan.price}
                                    <span className="text-base text-gray-500 font-normal">
                                        /month
                                    </span>
                                </div>

                                <ul className="text-left mt-4 space-y-3">
                                    {plan.features.map((feature, i) => (
                                        <li key={i} className="flex items-center text-gray-600">
                                            <CheckCircle className="w-5 h-5 text-primary mr-2" />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>


                                <button
                                    disabled={plan.name === "Growth"}
                                    className={cn(
                                        "mt-8 py-3 px-6 rounded-xl font-medium transition w-full cursor-pointer",
                                        plan.highlight
                                            ? "bg-gradient-to-r from-primary to-primary text-white shadow-lg hover:shadow-primary/40 hover:scale-105"
                                            : plan.name === "Growth"
                                                ? "bg-gray-300 text-gray-600 cursor-not-allowed"
                                                : "bg-black/90 text-white hover:bg-gray-900"
                                    )}
                                    onClick={() => plan.name === "Pro" && session?.user.isProUser ? handlePortal() : handlePlanClick(plan.name)}
                                >
                                    {plan.name === "Pro" && session?.user.isProUser ? "Manage Subscription" : plan.cta}
                                </button>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Trust row */}
                <div className="flex flex-wrap justify-center gap-6 mt-16 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-primary" />
                        Secure payments via Lemon Squeezy
                    </div>
                    <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-primary" />
                        Trusted by early builders
                    </div>
                    <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        Cancel anytime
                    </div>
                </div>
            </div>
        </section>
    );
};

export default PricingSection;
