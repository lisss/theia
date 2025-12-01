import React, { useState, useEffect } from 'react';
import './App.css';
import MetricDashboard from './components/MetricDashboard';
import MetricSelector from './components/MetricSelector';
import { fetchMetricNames, fetchAggregatedMetrics } from './services/api';

interface MetricData {
  name: string;
  time_bucket: string;
  avg_value: number;
  count: number;
}

function App() {
  const [metricNames, setMetricNames] = useState<string[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [metricsData, setMetricsData] = useState<Record<string, MetricData[]>>({});
  const [loading, setLoading] = useState(true);
  const [timeWindow, setTimeWindow] = useState<string>('5m');
  const [aggregateFunction, setAggregateFunction] = useState<string>('mean');

  useEffect(() => {
    loadMetricNames();
  }, []);

  useEffect(() => {
    if (selectedMetrics.length > 0) {
      loadMetricsData();
      const interval = setInterval(loadMetricsData, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [selectedMetrics, timeWindow, aggregateFunction]);

  const loadMetricNames = async () => {
    try {
      const names = await fetchMetricNames();
      setMetricNames(names);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load metric names:', error);
      setLoading(false);
    }
  };

  const loadMetricsData = async () => {
    try {
      const data: Record<string, MetricData[]> = {};
      for (const metricName of selectedMetrics) {
        const metrics = await fetchAggregatedMetrics(metricName, timeWindow, aggregateFunction);
        data[metricName] = metrics;
      }
      setMetricsData(data);
    } catch (error) {
      console.error('Failed to load metrics data:', error);
    }
  };

  const handleMetricToggle = (metricName: string) => {
    setSelectedMetrics((prev: string[]) => {
      if (prev.includes(metricName)) {
        return prev.filter((name: string) => name !== metricName);
      } else {
        return [...prev, metricName];
      }
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Theia</h1>
      </header>
      <main className="App-main">
        <MetricSelector
          metricNames={metricNames}
          selectedMetrics={selectedMetrics}
          onMetricToggle={handleMetricToggle}
          loading={loading}
        />
        <div className="controls-panel">
          <div className="control-group">
            <label htmlFor="time-window">Time Window: </label>
            <select
              id="time-window"
              value={timeWindow}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setTimeWindow(e.target.value)}
              className="control-dropdown"
            >
              <option value="1m">1 Minute</option>
              <option value="5m">5 Minutes</option>
              <option value="1h">1 Hour</option>
              <option value="1d">1 Day</option>
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="aggregate-function">Aggregation: </label>
            <select
              id="aggregate-function"
              value={aggregateFunction}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAggregateFunction(e.target.value)}
              className="control-dropdown"
            >
              <option value="mean">Average (Mean)</option>
              <option value="sum">Sum</option>
              <option value="max">Maximum</option>
              <option value="min">Minimum</option>
              <option value="count">Count</option>
              <option value="last">Last Value</option>
            </select>
          </div>
        </div>
        <MetricDashboard
          metricsData={metricsData}
          selectedMetrics={selectedMetrics}
          timeWindow={timeWindow}
          aggregateFunction={aggregateFunction}
        />
      </main>
    </div>
  );
}

export default App;

