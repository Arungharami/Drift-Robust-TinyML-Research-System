"use client";

import { useRef } from "react";
import { SLIDE_ASSET_PATH, SLIDE_CONTENT, SLIDE_SOURCE_PATH } from "@/lib/three-mt/content";

/**
 * Accessible HTML/CSS recreation of the actual single-slide PPTX, using its exact text content
 * (see lib/three-mt/content.ts). This is a recreation for the web, not a pixel copy of the
 * original design — the authoritative file is linked below for download. The slide's own text
 * content is never touched by the fullscreen control below.
 */
export function ThreeMTSlide() {
  const { title, subtitle, panelA, panelB, driftLabel, driftCaption, statLine, goalLine, attribution } = SLIDE_CONTENT;
  const cardRef = useRef<HTMLDivElement>(null);

  function handleFullscreen() {
    const el = cardRef.current;
    if (!el) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      el.requestFullscreen?.();
    }
  }

  return (
    <figure className="threemt-slide">
      <div className="threemt-slide-controls">
        <button type="button" className="btn" onClick={handleFullscreen}>
          Fullscreen
        </button>
        <a className="btn" href={SLIDE_ASSET_PATH} download>
          Download
        </a>
      </div>
      <div className="threemt-slide-card" ref={cardRef}>
        <h3 className="threemt-slide-title">{title}</h3>
        <p className="threemt-slide-subtitle">{subtitle}</p>
        <div className="threemt-slide-panels">
          <div className="threemt-slide-panel">
            <span className="threemt-slide-panel-label">{panelA.label}</span>
            <span className="threemt-slide-panel-stat">{panelA.stat}</span>
            <span className="threemt-slide-panel-caption">{panelA.caption}</span>
          </div>
          <div className="threemt-slide-drift">
            <span className="threemt-slide-arrow" aria-hidden="true">
              →
            </span>
            <span className="threemt-slide-drift-label">{driftLabel}</span>
            <span className="threemt-slide-drift-caption">
              {driftCaption.split("\n").map((line, i) => (
                <span key={i}>
                  {line}
                  <br />
                </span>
              ))}
            </span>
          </div>
          <div className="threemt-slide-panel">
            <span className="threemt-slide-panel-label">{panelB.label}</span>
            <span className="threemt-slide-panel-stat">{panelB.stat}</span>
            <span className="threemt-slide-panel-caption">{panelB.caption}</span>
          </div>
        </div>
        <p className="threemt-slide-stat-line">{statLine}</p>
        <p className="threemt-slide-goal-line">{goalLine}</p>
        <p className="threemt-slide-attribution">{attribution}</p>
      </div>
      <figcaption>
        Recreated for the web from the original single slide.{" "}
        <a href={SLIDE_ASSET_PATH} download>
          Download the original slide (PPTX)
        </a>{" "}
        · source: <code>{SLIDE_SOURCE_PATH}</code>
      </figcaption>
    </figure>
  );
}
