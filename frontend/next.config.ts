import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async redirects() {
    return [
      {
        source: "/admin",
        destination: "/stock-symbol-management",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
