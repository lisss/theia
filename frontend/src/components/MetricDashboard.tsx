import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './MetricDashboard.css';

interface MetricData {
  name: string;
  time_bucket: string;
  avg_value: number;
  count: number;
}

interface MetricDashboardProps {
  metricsData: Record<string, MetricData[]>;
  selectedMetrics: string[];
  timeWindow?: string;
  aggregateFunction?: string;
}

const MetricDashboard: React.FC<MetricDashboardProps> = ({
  metricsData,
  selectedMetrics,
  timeWindow = '5m',
  aggregateFunction = 'mean',
}) => {
  if (selectedMetrics.length === 0) {
    return (
      <div className="metric-dashboard">
        <p>Select metrics from above to display graphs.</p>
      </div>
    );
  }

  // Transform data for Recharts
  const chartData: Record<string, any>[] = [];
  const timeBuckets = new Set<string>();

  // Collect all time buckets
  selectedMetrics.forEach(metricName => {
    const data = metricsData[metricName] || [];
    data.forEach(item => timeBuckets.add(item.time_bucket));
  });

  // Create chart data points
  Array.from(timeBuckets).sort().forEach(timeBucket => {
    const dataPoint: Record<string, any> = { time: new Date(timeBucket).toLocaleTimeString() };
    selectedMetrics.forEach(metricName => {
      const metricData = metricsData[metricName] || [];
      const point = metricData.find(d => d.time_bucket === timeBucket);
      dataPoint[metricName] = point ? point.avg_value : null;
    });
    chartData.push(dataPoint);
  });

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

  return (
    <div className="metric-dashboard">
      <h2>Metrics Visualization</h2>
      <div className="charts-container">
        {selectedMetrics.map((metricName, index) => {
          const metricData = metricsData[metricName] || [];
          const chartDataForMetric = metricData.map(item => ({
            time: new Date(item.time_bucket).toLocaleTimeString(),
            value: item.avg_value,
            count: item.count,
          }));

          return (
            <div key={metricName} className="chart-card">
              <h3>{metricName}</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartDataForMetric}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name={aggregateFunction === 'mean' ? 'Average' : 
                          aggregateFunction === 'sum' ? 'Sum' :
                          aggregateFunction === 'max' ? 'Maximum' :
                          aggregateFunction === 'min' ? 'Minimum' :
                          aggregateFunction === 'count' ? 'Count' :
                          aggregateFunction === 'last' ? 'Last Value' : 'Value'}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MetricDashboard;

