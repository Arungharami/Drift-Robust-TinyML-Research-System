/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    dirs: ["app", "components", "lib"],
  },
  images: {
    remotePatterns: [{ protocol: "https", hostname: "www.nordicsemi.cn", pathname: "/assets/images/**" }],
  },
};

export default nextConfig;
