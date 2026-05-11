"use client";

import { useEffect, useState } from "react";
import { Zap } from "lucide-react";
import { Button } from "./ui/button";
import Link from "next/link";
import { useSession } from "next-auth/react";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`sticky top-0 z-50 transition-all duration-300
    ${scrolled
          ? "backdrop-blur-xl bg-black/30 border-b border-white/10 transition-colors duration-300"
          : "bg-[#020918]"
        }
  `}
    >
      <div
        className={`mx-auto px-4 sm:px-6 lg:px-8 transition-all duration-300 ${scrolled ? "max-w-5xl" : "max-w-7xl"
          }`}
      >
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-800 rounded-md flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <Link href="/">
              <span className="text-xl font-semibold tracking-tight text-white">
                PingGenius
              </span>
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {/* <Link href={"/pricing"}>
              <Button
                variant="link"
                className="cursor-pointer text-neutral-300 hover:text-white transition"
              >
                Pricing
              </Button>
            </Link> */}
            {/* Optional Mode Toggle */}
            {/* {session?.user ? (
              <Link href="/dashboard">
                <Button className="cursor-pointer bg-primary hover:bg-primary/80 text-white rounded-md font-medium transition-all duration-200 hover:shadow-lg hover:scale-105">
                  Dashboard
                </Button>
              </Link>
            ) : ( */}
              <Link href="/sign-in">
                <Button className="bg-blue-600 hover:bg-blue-500 text-white rounded-md font-medium transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-600/30 cursor-pointer">
                  Sign In
                </Button>
              </Link>
            {/* )} */}
          </div>
        </div>
      </div>
    </nav>
  );
}
