export interface NavItem {
  href: string;
  label: string;
}

// Every route here actually exists — the mission rule "only enable destinations that exist"
// applies to internal nav too, not just homepage CTA buttons.
export const NAV_ITEMS: NavItem[] = [
  { href: "/research", label: "Research" },
  { href: "/dataset", label: "Dataset" },
  { href: "/methodology", label: "Methodology" },
  { href: "/pipeline", label: "Pipeline" },
  { href: "/experiments", label: "Experiments" },
  { href: "/results", label: "Results" },
  { href: "/xai", label: "XAI" },
  { href: "/tinyml", label: "TinyML" },
  { href: "/hardware", label: "Hardware" },
  { href: "/huggingface", label: "Hugging Face" },
  { href: "/reproducibility", label: "Reproducibility" },
  { href: "/paper", label: "Paper" },
  { href: "/references", label: "References" },
  { href: "/professor-review", label: "Professor Review" },
  { href: "/about", label: "About" },
];
