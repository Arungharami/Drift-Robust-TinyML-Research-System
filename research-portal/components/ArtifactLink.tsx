import { githubBlobUrl } from "@/lib/evidence";

/** Links a displayed value back to the exact repository artifact it came from. */
export function ArtifactLink({ path, commit, label }: { path: string; commit?: string; label?: string }) {
  return (
    <a href={githubBlobUrl(path, commit)} target="_blank" rel="noreferrer">
      <code>{label ?? path}</code>
    </a>
  );
}
