"use client";

import { useState } from "react";
import { ArtifactLink } from "@/components/ArtifactLink";
import { SPEECH_PARAGRAPHS, SPEECH_SOURCE_PATH } from "@/lib/three-mt/content";

/**
 * Renders the actual submitted 3MT speech verbatim — see lib/three-mt/content.ts for provenance.
 * "Presentation mode" only changes typography (larger text, narrower measure) via a CSS class —
 * it never touches SPEECH_PARAGRAPHS, which stays word-for-word what was submitted.
 */
export function ThreeMTSpeech() {
  const [presentationMode, setPresentationMode] = useState(false);
  return (
    <div className={`threemt-speech${presentationMode ? " threemt-speech-presentation" : ""}`}>
      <div className="threemt-speech-toolbar">
        <div className="section-label">Verbatim transcript</div>
        <button
          type="button"
          className="btn"
          aria-pressed={presentationMode}
          onClick={() => setPresentationMode((v) => !v)}
        >
          {presentationMode ? "Exit presentation mode" : "Presentation mode"}
        </button>
      </div>
      {SPEECH_PARAGRAPHS.map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
      <p className="threemt-speech-source">
        Source: <ArtifactLink path={SPEECH_SOURCE_PATH} label={SPEECH_SOURCE_PATH} />
      </p>
    </div>
  );
}
