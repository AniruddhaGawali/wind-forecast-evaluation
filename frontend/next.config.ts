import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Plain HTML/JS/CSS in out/, served by nginx in Docker. The page is fully client-side.
  output: "export",
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
