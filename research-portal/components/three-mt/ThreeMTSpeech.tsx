import { ArtifactLink } from "@/components/ArtifactLink";
import { SPEECH_PARAGRAPHS, SPEECH_SOURCE_PATH } from "@/lib/three-mt/content";

/** Renders the actual submitted 3MT speech verbatim — see lib/three-mt/content.ts for provenance. */
export function ThreeMTSpeech() {
  return (
    <div className="threemt-speech">
      <div className="section-label">Verbatim transcript</div>
      {SPEECH_PARAGRAPHS.map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
      <p className="threemt-speech-source">
        Source: <ArtifactLink path={SPEECH_SOURCE_PATH} label={SPEECH_SOURCE_PATH} />
      </p>
    </div>
  );
}
