"use client";

import { Component, type ReactNode } from "react";

/** If the WebGL scene throws for any reason (driver quirk, context loss), fall back to the
 * list view instead of breaking the page — matches the site's "honest fallback, never a broken
 * page" convention (see PlannedPage.tsx). */
export class ProcessSceneBoundary extends Component<
  { children: ReactNode; onError: () => void },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode; onError: () => void }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch() {
    this.props.onError();
  }

  render() {
    if (this.state.hasError) return null;
    return this.props.children;
  }
}
