import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import FooterProvider from "@/components/footer-provider";
import { Analytics } from "@vercel/analytics/next"
import Providers from "@/components/Providers";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";


const poppins = Poppins({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-poppins',
});

export const metadata: Metadata = {
  title: {
    default: "PingGenius - Turn Any LinkedIn Profile Into Personalized Outreach Sequences",
    template: "%s | PingGenius"
  },
  description: "PingGenius analyzes LinkedIn profiles and generates complete, personalized outreach sequences - from connection requests to follow-ups - that sound human and earn replies.",
  keywords: [
    "PingGenius",
    "AI cold outreach",
    "LinkedIn DMs",
    "personalized messages",
    "sales automation",
    "indie hackers",
    "startup founders",
    "B2B outreach",
    "AI outreach tool",
    "email outreach AI",
    "LinkedIn automation",
    "outreach sequences",
    "lead generation",
    "sales development",
    "conversion optimization",
    "LinkedIn messaging",
    "professional networking",
    "business development",
    "CRM integration",
    "outreach automation"
  ],
  authors: [{ name: "Muhammad Hasnain", url: "https://x.com/HasnainXdev" }],
  creator: "Muhammad Hasnain",
  publisher: "PingGenius",
  openGraph: {
    title: "PingGenius - Turn Any LinkedIn Profile Into Personalized Outreach Sequences",
    description: "Ultra-personalized LinkedIn messages powered by AI for indie hackers, startup founders, and solo teams. Get replies without automation risks.",
    url: "https://pinggenius.vercel.app",
    siteName: "PingGenius",
    images: [
      {
        url: "/og_image.png",
        width: 1200,
        height: 630,
        alt: "PingGenius AI Outreach - Turn Any LinkedIn Profile Into Personalized Outreach Sequences",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "PingGenius - Turn Any LinkedIn Profile Into Personalized Outreach Sequences",
    description: "PingGenius analyzes LinkedIn profiles and generates complete, personalized outreach sequences - from connection requests to follow-ups - that sound human and earn replies.",
    creator: "@HasnainXdev",
    site: "@PingGeniusApp",
    images: ["/og_image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: "https://pinggenius.vercel.app",
  },
  verification: {
    google: 'google-site-verification-token', // Add actual token when available
    yahoo: 'yahoo-verification-token', // Add actual token when available
    yandex: 'yandex-verification-token', // Add actual token when available
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest", // Add web app manifest for PWA features
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${poppins.variable} antialiased bg-background text-foreground`}
      >
        <Providers>
          <TooltipProvider>
            {children}
            <Toaster position="top-center" />
          </TooltipProvider>
        </Providers>
        <Analytics />
        <FooterProvider />
      </body>
    </html>
  );
}
