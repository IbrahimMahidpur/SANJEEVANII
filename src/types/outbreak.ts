export interface OutbreakAlert {
  alert_id: string;
  created_at: string;
  disease: string;
  region: string;
  lat: number;
  lon: number;
  window_start?: string;
  window_end?: string;
  metric: 'zscore' | 'threshold' | 'news_based';
  value: number;
  expected: number;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  status: 'open' | 'acknowledged' | 'resolved';
  case_count: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  cases_per_100k?: number;
  population?: number;
  updated_at?: string;
  source?: string;
  source_url?: string;
  confidence?: number;
  title?: string;
  description?: string;
  weekly_trend?: number[];
  sources?: SourceReference[];
}

export interface SourceReference {
  name: string;
  url: string;
  type: 'government' | 'who' | 'news' | 'research' | 'other';
  published_at?: string;
}

export interface DailyCount {
  date: string;
  disease: string;
  region: string;
  confirmed_cases: number;
  suspected_cases: number;
  tests: number;
  population: number;
  cases_per_100k: number;
}

export interface Region {
  name: string;
  lat: number;
  lon: number;
  population: number;
}

export interface OutbreakStatistics {
  total: number;
  by_severity: Record<string, number>;
  by_disease: Record<string, number>;
  by_status: Record<string, number>;
}
