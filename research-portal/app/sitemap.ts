import type { MetadataRoute } from "next";
import { NAV_ITEMS } from "@/lib/nav";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://drift-robust-tinyml-research.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  // Sitemap is regenerated on every build, so "now" is an honest lastModified —
  // an epoch-0 date was actively misleading to crawlers, not just a placeholder.
  const generatedAt = new Date();
  const routes = ["/", ...NAV_ITEMS.map((item) => item.href)];
  return routes.map((route) => ({
    url: `${SITE_URL}${route}`,
    lastModified: generatedAt,
    changeFrequency: "weekly",
  }));
}
