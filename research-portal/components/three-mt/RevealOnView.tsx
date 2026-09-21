"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Adds "is-revealed" once the element scrolls into view, for a one-shot CSS transition.
 * Defaults to already-revealed (no observer, or reduced motion) so content is never hidden
 * from a user whose browser/setup skips the observer — this is a presentation flourish, not a
 * gate on content visibility.
 */
export function RevealOnView({
  children,
  className = "",
  as: Tag = "div",
}: {
  children: React.ReactNode;
  className?: string;
  as?: keyof React.JSX.IntrinsicElements;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") {
      setRevealed(true);
      return;
    }
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) {
      setRevealed(true);
      return;
    }
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          setRevealed(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const Component = Tag as React.ElementType;
  return (
    <Component ref={ref} className={`reveal-on-view${revealed ? " is-revealed" : ""} ${className}`}>
      {children}
    </Component>
  );
}
