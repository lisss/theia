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

  useEffect(() => {
    loadMetricNames();
  }, []);

  useEffect(() => {
    if (selectedMetrics.length > 0) {
      loadMetricsData();
      const interval = setInterval(loadMetricsData, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [selectedMetrics]);

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
        const metrics = await fetchAggregatedMetrics(metricName);
        data[metricName] = metrics;
      }
      setMetricsData(data);
    } catch (error) {
      console.error('Failed to load metrics data:', error);
    }
  };

  const handleMetricToggle = (metricName: string) => {
    setSelectedMetrics(prev => {
      if (prev.includes(metricName)) {
        return prev.filter(name => name !== metricName);
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
        <MetricDashboard
          metricsData={metricsData}
          selectedMetrics={selectedMetrics}
        />
      </main>
    </div>
  );
}

export default App;

