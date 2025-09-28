import type { NextConfig } from "next";

const publicApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";
const internalApiBase = process.env.API_INTERNAL_URL ?? "http://localhost:4000";
const normalizedInternalApiBase = internalApiBase.replace(/\/$/, "");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: publicApiBase,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${normalizedInternalApiBase}/:path*`,
      },
    ];
  },
  poweredByHeader: false,
};

export default nextConfig;
