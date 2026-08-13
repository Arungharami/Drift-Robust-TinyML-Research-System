import { getProjectStatus } from "@/lib/evidence";

export function SiteFooter() {
  const status = getProjectStatus();
  return (
    <footer className="site-footer">
      <div className="container">
        <p style={{ margin: 0 }}>
          Evidence last exported {status.last_updated} from commit{" "}
          <code>{status.git_commit.slice(0, 7)}</code> on <code>{status.branch}</code>.{" "}
          <a href={`https://github.com/${status.repository}`} target="_blank" rel="noreferrer">
            {status.repository}
          </a>
        </p>
        <p style={{ margin: "0.5rem 0 0" }}>
          Licensed MIT. No experimental result on this site is estimated, simulated, or
          demonstration data — every number links to a saved artifact, or is marked{" "}
          <code>NOT EXECUTED</code>.
        </p>
      </div>
    </footer>
  );
}
