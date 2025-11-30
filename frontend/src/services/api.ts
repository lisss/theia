import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

export interface Metric {
  id: number;
  name: string;
  value: number;
  tags: Record<string, any>;
  timestamp: string;
  source: string;
}

export interface AggregatedMetric {
  name: string;
  time_bucket: string;
  avg_value: number;
  count: number;
}

export const fetchMetrics = async (params?: {
  name?: string;
  source?: string;
  start_time?: string;
  end_time?: string;
  limit?: number;
}): Promise<Metric[]> => {
  const response = await axios.get(`${API_BASE_URL}/api/metrics`, { params });
  return response.data;
};

export const fetchAggregatedMetrics = async (
  name?: string,
  window: string = '1m'
): Promise<AggregatedMetric[]> => {
  const response = await axios.get(`${API_BASE_URL}/api/metrics/aggregate`, {
    params: { name, window },
  });
  return response.data;
};

export const fetchMetricNames = async (): Promise<string[]> => {
  const response = await axios.get(`${API_BASE_URL}/api/metrics/names`);
  return response.data;
};

