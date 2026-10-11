"use client";
import { useRef, useState } from "react";
import Image from "next/image";
import { SLIDE_ASSET_PATH, SLIDE_CONTENT, SLIDE_PREVIEW_PATH } from "@/lib/three-mt/content";

/** Supplied October 2 preview, with the source PPTX retained unchanged. */
export function ThreeMTSlide() {
  const cardRef = useRef<HTMLDivElement>(null);
  const [fullscreenError, setFullscreenError] = useState("");
  async function handleFullscreen() {
    setFullscreenError("");
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (cardRef.current?.requestFullscreen) await cardRef.current.requestFullscreen();
      else setFullscreenError("Fullscreen is unavailable. Open the slide image below.");
    } catch { setFullscreenError("Fullscreen is unavailable. Open the slide image below."); }
  }
  return (
    <figure className="threemt-slide">
      <div className="threemt-slide-controls">
        <button type="button" className="btn" onClick={handleFullscreen}>Fullscreen</button>
        <a className="btn" href={SLIDE_ASSET_PATH} download>Download PowerPoint</a>
        <a className="btn" href={SLIDE_PREVIEW_PATH} target="_blank" rel="noreferrer">Open slide image</a>
      </div>
      {fullscreenError ? <p role="status">{fullscreenError}</p> : null}
      <div ref={cardRef} style={{ background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", width: "100%" }}>
        <Image src={SLIDE_PREVIEW_PATH}
          alt={SLIDE_CONTENT.title + ". " + SLIDE_CONTENT.subtitle + ". Concept illustration of an electronic nose in homes, factories, and smart cities. " + SLIDE_CONTENT.attribution}
          width={1920} height={1080} priority unoptimized
          style={{ display: "block", width: "100%", height: "auto", maxHeight: "100vh", objectFit: "contain" }} />
      </div>
      <figcaption>
        Latest single slide · October 2, 2026. <a href={SLIDE_ASSET_PATH} download>Download PowerPoint with speaker notes</a>.
        {" "}Illustrations show potential applications; physical device validation is still pending.
      </figcaption>
    </figure>
  );
}
