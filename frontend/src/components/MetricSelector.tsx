import React from 'react';
import './MetricSelector.css';

interface MetricSelectorProps {
  metricNames: string[];
  selectedMetrics: string[];
  onMetricToggle: (metricName: string) => void;
  loading: boolean;
}

const MetricSelector: React.FC<MetricSelectorProps> = ({
  metricNames,
  selectedMetrics,
  onMetricToggle,
  loading,
}) => {
  if (loading) {
    return (
      <div className="metric-selector">
        <p>Loading metrics...</p>
      </div>
    );
  }

  if (metricNames.length === 0) {
    return (
      <div className="metric-selector">
        <p>No metrics available. Start sending metrics to see them here.</p>
      </div>
    );
  }

  return (
    <div className="metric-selector">
      <h2>Select Metrics to Display</h2>
      <div className="metric-checkboxes">
        {metricNames.map((name) => (
          <label key={name} className="metric-checkbox">
            <input
              type="checkbox"
              checked={selectedMetrics.includes(name)}
              onChange={() => onMetricToggle(name)}
            />
            <span>{name}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default MetricSelector;

