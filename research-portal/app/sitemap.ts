import type { MetadataRoute } from "next";
import { NAV_ITEMS } from "@/lib/nav";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://drift-robust-tinyml.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = ["/", ...NAV_ITEMS.map((item) => item.href)];
  return routes.map((route) => ({
    url: `${SITE_URL}${route}`,
    lastModified: new Date(0), // stamped by CI/deploy time in a future iteration; stable for now
    changeFrequency: "weekly",
  }));
}
