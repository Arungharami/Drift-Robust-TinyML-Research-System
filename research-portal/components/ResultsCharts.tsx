"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from "recharts";

const SERIES_COLORS = ["#1f4d3d", "#8f6b1f", "#1f4c8f", "#8f1f3f"];

export function BatchMetricLineChart({
  data,
  metricKey,
  models,
  yLabel,
}: {
  data: Record<string, number | string>[];
  metricKey: string;
  models: string[];
  yLabel: string;
}) {
  return (
    <div className="chart-scroll" role="region" aria-label={`${yLabel} by test batch chart`} tabIndex={0}>
      <div className="chart-canvas chart-canvas-wide">
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="test_batch" label={{ value: "Test batch", position: "insideBottom", offset: -4 }} />
            <YAxis domain={[0, 1]} label={{ value: yLabel, angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Legend />
            {models.map((model, i) => (
              <Line
                key={model}
                type="monotone"
                dataKey={`${model}_${metricKey}`}
                name={model}
                stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
                dot={{ r: 3 }}
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function ModelBarChart({
  data,
  dataKey,
  yLabel,
}: {
  data: { model: string; value: number }[];
  dataKey: string;
  yLabel: string;
}) {
  return (
    <div className="chart-scroll" role="region" aria-label={`${yLabel} by model chart`} tabIndex={0}>
      <div className="chart-canvas">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="model" />
            <YAxis label={{ value: yLabel, angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Bar dataKey="value" name={dataKey} fill="#1f4d3d" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
