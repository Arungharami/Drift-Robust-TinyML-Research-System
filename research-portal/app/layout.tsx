import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Drift-Robust Explainable TinyML | Research Portal",
  description:
    "Evidence-first research portal for chronological sensor-drift evaluation, resource-aware explainability, and reproducible nRF52840 TinyML deployment.",
  keywords: [
    "TinyML",
    "electronic nose",
    "sensor drift",
    "explainable AI",
    "nRF52840",
    "edge AI",
    "reproducible research",
  ],
  authors: [{ name: "Arun Kumar Gharami" }],
  openGraph: {
    title: "Drift-Robust Explainable TinyML",
    description:
      "Chronological evaluation, resource-aware explanations, and reproducible edge deployment.",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
