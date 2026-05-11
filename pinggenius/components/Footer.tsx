import { Zap } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-black border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-blue-600 rounded-md flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white">
              PingGenius
            </span>
          </div>

          {/* Links */}
          <div className="flex items-center gap-8 text-sm text-white/50">
            <Link href="/" className="hover:text-white transition">
              Privacy
            </Link>
            <Link href="/" className="hover:text-white transition">
              Terms
            </Link>
            <Link
              href="https://x.com/hasnainXdev"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition"
            >
              Founder
            </Link>
          </div>

          {/* Product Hunt */}
          {/* <Link
            href="https://www.producthunt.com/products/pinggenius?embed=true&utm_source=badge-featured&utm_medium=badge"
            target="_blank"
            className="opacity-80 hover:opacity-100 transition"
          >
            <Image
              src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1026128&theme=dark"
              alt="PingGenius on Product Hunt"
              width={220}
              height={48}
            />
          </Link> */}
        </div>

        {/* Bottom note */}
        <div className="mt-10 text-center text-xs text-white/40">
          © {new Date().getFullYear()} PingGenius built to start conversations, not spam.
        </div>
      </div>
    </footer>
  );
}
