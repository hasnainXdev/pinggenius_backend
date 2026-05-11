import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  allowedDevOrigins: ["http://localhost:8000", "c036f34c77c9.ngrok-free.app", "https://labs.pathfix.com", "https://api.pathfix.com",],

};

export default nextConfig;
