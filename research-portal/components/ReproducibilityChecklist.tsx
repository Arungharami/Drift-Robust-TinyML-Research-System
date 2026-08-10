import { getEnvironment, getProjectStatus } from "@/lib/evidence";

export function ReproducibilityChecklist() {
  const env = getEnvironment();
  const status = getProjectStatus();
  const items: { label: string; value: string | null }[] = [
    { label: "Random seed", value: env ? String(env.seed) : null },
    { label: "Python version", value: env?.python ?? null },
    { label: "OS / runtime", value: env?.platform ?? null },
    { label: "Git commit (environment capture)", value: env?.git_commit?.slice(0, 12) ?? null },
    { label: "Git commit (this evidence export)", value: status.git_commit.slice(0, 12) },
    {
      label: "Key package versions",
      value: env ? Object.entries(env.packages).map(([k, v]) => `${k} ${v}`).join(", ") : null,
    },
  ];
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Item</th>
            <th>Recorded value</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.label}>
              <td>{item.label}</td>
              <td><code>{item.value ?? "NOT EXECUTED"}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
