import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import "./globals.css";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://drift-robust-tinyml.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Drift-Robust Explainable TinyML for Electronic-Nose Sensing",
    template: "%s · Drift-Robust TinyML",
  },
  description:
    "Chronological evaluation, resource-aware explanations, and reproducible edge deployment for electronic-nose sensor drift — an evidence-driven research system.",
  keywords: [
    "TinyML",
    "Explainable AI",
    "XAI",
    "Sensor Drift",
    "Electronic Nose",
    "Embedded Machine Learning",
    "nRF52840",
    "Concept Drift",
    "Edge AI",
    "Resource-Aware Explainability",
  ],
  authors: [{ name: "Arun Gharami" }],
  openGraph: {
    title: "Drift-Robust Explainable TinyML for Electronic-Nose Sensing",
    description:
      "Chronological evaluation, resource-aware explanations, and reproducible edge deployment for electronic-nose sensor drift.",
    url: SITE_URL,
    siteName: "Drift-Robust TinyML Research Portal",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Drift-Robust Explainable TinyML for Electronic-Nose Sensing",
    description:
      "Chronological evaluation, resource-aware explanations, and reproducible edge deployment for electronic-nose sensor drift.",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <a href="#main-content" className="skip-link">
          Skip to content
        </a>
        <SiteHeader />
        <main id="main-content">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
