import { useState, useEffect, useRef } from 'react';
import { AlertTriangle, MapPin, Calendar, Activity, ExternalLink, Shield, Globe, FileText, Newspaper, ChevronDown, ChevronUp, RefreshCw, Pause, Clock, Bell, X, TrendingUp, TrendingDown, Map } from 'lucide-react';
import type { OutbreakAlert, Region, OutbreakStatistics, SourceReference } from '../types/outbreak';
import HeatmapModal from '../components/HeatmapModal';

// --- Sparkline Component for Trend Visualization ---
const Sparkline = ({ data, color = "#ef4444", height = 40, width = 100, className = "" }: { data: number[], color?: string, height?: number, width?: number, className?: string }) => {
  if (!data || data.length < 2) return null;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const stepX = width / (data.length - 1);

  // Generate path points
  const points = data.map((val, i) => {
    const x = i * stepX;
    const y = height - ((val - min) / range) * height; // Invert Y for SVG
    return `${x},${y}`;
  }).join(' ');

  // Area path (closed at bottom)
  const areaPath = `${points} ${width},${height} 0,${height}`;

  return (
    <div className={`relative ${className}`} style={{ width: className ? '100%' : width, height: className ? '100%' : height }}>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible" preserveAspectRatio="none">
        <defs>
          <linearGradient id={`gradient-${color}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.2" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Area Fill */}
        <polygon points={areaPath} fill={`url(#gradient-${color})`} />
        {/* Line */}
        <polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
        {/* End Dot */}
        {data.length > 0 && (
          <circle
            cx={width}
            cy={height - ((data[data.length - 1] - min) / range) * height}
            r="3"
            fill={color}
          />
        )}
      </svg>
    </div>
  );
};

const SourceBadge = ({ type }: { type: string }) => {
  switch (type) {
    case 'government':
      return <Shield className="w-3 h-3 text-blue-400" />;
    case 'who':
      return <Globe className="w-3 h-3 text-green-400" />;
    case 'news':
      return <Newspaper className="w-3 h-3 text-orange-400" />;
    case 'research':
      return <FileText className="w-3 h-3 text-purple-400" />;
    default:
      return <ExternalLink className="w-3 h-3 text-gray-400" />;
  }
};

const ReferencesSection = ({ sources }: { sources: SourceReference[] }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 border-t border-gray-700/50 pt-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs font-medium text-gray-400 hover:text-white transition-colors w-full"
      >
        {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        View Sources & References ({sources.length})
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2 animate-slide-in">
          {sources.map((source, index) => (
            <div key={index} className="flex items-start gap-2 text-xs bg-gray-800/30 p-2 rounded-lg hover:bg-gray-800/50 transition-colors">
              <div className="mt-0.5"><SourceBadge type={source.type} /></div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium text-gray-300 truncate">{source.name}</span>
                  {source.published_at && (
                    <span className="text-gray-500 text-[10px] whitespace-nowrap">
                      {new Date(source.published_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 flex items-center gap-1 mt-0.5 truncate"
                >
                  {source.url} <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const API_BASE = 'http://localhost:5000/api/outbreak';

// Time range options
const TIME_RANGES = [
  { label: 'Last Hour', value: '1h', hours: 1 },
  { label: 'Last Day', value: '1d', hours: 24 },
  { label: 'Last Week', value: '1w', hours: 168 },
  { label: 'Last Month', value: '1m', hours: 720 },
  { label: 'Last 6 Months', value: '6m', hours: 4320 },
  { label: 'Last Year', value: '1y', hours: 8760 },
];

export default function OutbreakAlert() {
  const [alerts, setAlerts] = useState<OutbreakAlert[]>([]);
  const [statistics, setStatistics] = useState<OutbreakStatistics | null>(null);
  const [regions, setRegions] = useState<Region[]>([]);
  const [diseases, setDiseases] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);
  const [timeRange, setTimeRange] = useState<string>('1w'); // Default: Last Week
  const refreshIntervalRef = useRef<number | null>(null);

  // Filters
  const [selectedDisease, setSelectedDisease] = useState<string>('');
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('open');

  // Visual Enhancements - Recent Outbreaks Panel
  const [recentOutbreaks, setRecentOutbreaks] = useState<OutbreakAlert[]>([]);
  const [showRecentPanel, setShowRecentPanel] = useState(false);
  const prevAlertsRef = useRef<Set<string>>(new Set());
  const [showHeatmap, setShowHeatmap] = useState(false);

  // Detect new alerts and update recent outbreaks panel
  useEffect(() => {
    if (alerts.length > 0) {
      const currentIds = new Set(alerts.map(a => a.alert_id));

      // Only update if we have previous alerts (skip initial load)
      if (prevAlertsRef.current.size > 0) {
        const newAlerts = alerts.filter(a => !prevAlertsRef.current.has(a.alert_id));
        if (newAlerts.length > 0) {
          // Add new alerts to recent outbreaks (keep last 5)
          setRecentOutbreaks(prev => [...newAlerts, ...prev].slice(0, 5));
          setShowRecentPanel(true);

          // Auto-hide after 10 seconds
          setTimeout(() => setShowRecentPanel(false), 10000);
        }
      }
      prevAlertsRef.current = currentIds;
    }
  }, [alerts]);

  // Calculate start date based on time range
  const getStartDate = () => {
    const now = new Date();
    const range = TIME_RANGES.find(r => r.value === timeRange);
    if (!range) return null;

    const startDate = new Date(now.getTime() - (range.hours * 60 * 60 * 1000));
    return startDate.toISOString(); // Use full ISO string for precise filtering
  };

  // Fetch data with time filtering
  useEffect(() => {
    fetchData();
  }, [selectedDisease, selectedRegion, selectedSeverity, selectedStatus, timeRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query params
      const params = new URLSearchParams();
      if (selectedDisease) params.append('disease', selectedDisease);
      if (selectedRegion) params.append('region', selectedRegion);
      if (selectedSeverity) params.append('severity', selectedSeverity);
      if (selectedStatus) params.append('status', selectedStatus);

      // Add time range filtering
      const startDate = getStartDate();
      if (startDate) params.append('startDate', startDate);

      // Fetch alerts
      const alertsRes = await fetch(`${API_BASE}/alerts?${params}`);
      const alertsData = await alertsRes.json();

      console.log('📊 Fetched Alerts:', alertsData); // Debug log

      if (alertsData.success) {
        setAlerts(alertsData.alerts);

        // FIX: Calculate statistics from filtered alerts
        const stats = {
          total: alertsData.alerts.length,
          by_severity: {} as Record<string, number>,
          by_disease: {} as Record<string, number>,
          by_status: {} as Record<string, number>,
        };

        for (const alert of alertsData.alerts) {
          stats.by_severity[alert.severity] = (stats.by_severity[alert.severity] || 0) + 1;
          stats.by_disease[alert.disease] = (stats.by_disease[alert.disease] || 0) + 1;
          stats.by_status[alert.status] = (stats.by_status[alert.status] || 0) + 1;
        }

        setStatistics(stats);
      }

      // Fetch regions and diseases (only once)
      if (regions.length === 0) {
        const regionsRes = await fetch(`${API_BASE}/regions`);
        const regionsData = await regionsRes.json();
        if (regionsData.success) {
          setRegions(regionsData.regions);
        }
      }

      if (diseases.length === 0) {
        const diseasesRes = await fetch(`${API_BASE}/diseases`);
        const diseasesData = await diseasesRes.json();
        if (diseasesData.success) {
          setDiseases(diseasesData.diseases);
        }
      }

      setLoading(false);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error fetching outbreak data:', err);
      setError('Failed to load outbreak data. Please try again.');
      setLoading(false);
    }
  };

  // Auto-refresh functionality
  useEffect(() => {
    if (isAutoRefresh) {
      refreshIntervalRef.current = setInterval(() => {
        console.log('🔄 Auto-refreshing data...');
        fetchData();
      }, 30000); // Refresh every 30 seconds
    } else {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [isAutoRefresh, selectedDisease, selectedRegion, selectedSeverity, selectedStatus, timeRange]);

  // Live timestamp update (updates every second for real-time display)
  useEffect(() => {
    const timestampInterval = setInterval(() => {
      // Force re-render to update the "X seconds ago" display
      setLastUpdate(prev => new Date(prev));
    }, 1000); // Update every second

    return () => clearInterval(timestampInterval);
  }, []);

  // Format last update time (live updating)
  const formatLastUpdate = () => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - lastUpdate.getTime()) / 1000);

    if (diff < 60) return `${diff} second${diff !== 1 ? 's' : ''} ago`;
    if (diff < 3600) {
      const mins = Math.floor(diff / 60);
      return `${mins} minute${mins !== 1 ? 's' : ''} ago`;
    }
    return lastUpdate.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'bg-red-500/20 border-red-500 text-red-400';
      case 'High': return 'bg-orange-500/20 border-orange-500 text-orange-400';
      case 'Medium': return 'bg-yellow-500/20 border-yellow-500 text-yellow-400';
      case 'Low': return 'bg-green-500/20 border-green-500 text-green-400';
      default: return 'bg-gray-500/20 border-gray-500 text-gray-400';
    }
  };



  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                Outbreak Alert System
              </h1>
              <p className="text-gray-400 mt-1">Real-time disease surveillance & anomaly detection</p>
            </div>
            <div className="flex items-center gap-3">
              {/* Heatmap button */}
              <button
                onClick={() => setShowHeatmap(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 font-medium bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                title="View Heatmap"
              >
                <Map className="w-4 h-4" />
                Heatmap
              </button>

              {/* Auto-refresh toggle */}
              <button
                onClick={() => setIsAutoRefresh(!isAutoRefresh)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 font-medium ${isAutoRefresh
                  ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700'
                  : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                title={isAutoRefresh ? 'Auto-refresh ON (30s)' : 'Auto-refresh OFF'}
              >
                {isAutoRefresh ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Pause className="w-4 h-4" />}
                {isAutoRefresh ? 'Auto' : 'Paused'}
              </button>

              {/* Manual refresh */}
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 font-medium"
              >
                Refresh Data
              </button>
            </div>
          </div>

          {/* Time Range Selector */}
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Clock className="w-4 h-4" />
              <span>Time Range:</span>
            </div>
            {TIME_RANGES.map((range) => (
              <button
                key={range.value}
                onClick={() => setTimeRange(range.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${timeRange === range.value
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
              >
                {range.label}
              </button>
            ))}

            {/* Last update timestamp */}
            <div className="ml-auto flex items-center gap-2 text-sm text-gray-500">
              <Activity className="w-4 h-4" />
              <span>Last updated: {formatLastUpdate()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* News Ticker */}
      <div className="bg-red-900/20 border-y border-red-500/20 overflow-hidden py-2 backdrop-blur-sm">
        <div className="flex gap-8 animate-marquee whitespace-nowrap" style={{ animation: 'marquee 30s linear infinite' }}>
          {alerts.slice(0, 10).map((alert) => (
            <span key={alert.alert_id} className="text-sm font-medium text-red-200 flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${alert.severity === 'Critical' ? 'bg-red-500 animate-ping' : 'bg-orange-500'}`}></span>
              <span className="font-bold">BREAKING:</span> {alert.disease} outbreak in {alert.region} ({alert.severity})
            </span>
          ))}
          {/* Duplicate for seamless loop */}
          {alerts.slice(0, 10).map((alert) => (
            <span key={`dup-${alert.alert_id}`} className="text-sm font-medium text-red-200 flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${alert.severity === 'Critical' ? 'bg-red-500 animate-ping' : 'bg-orange-500'}`}></span>
              <span className="font-bold">BREAKING:</span> {alert.disease} outbreak in {alert.region} ({alert.severity})
            </span>
          ))}
        </div>
        <style>{`
          @keyframes marquee {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
          }
          @keyframes slide-in {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
          }
          .animate-slide-in {
            animation: slide-in 0.5s ease-out;
          }
        `}</style>
      </div>


      {/* Recent Outbreaks Panel - Bottom Right */}
      {showRecentPanel && recentOutbreaks.length > 0 && (
        <div className="fixed bottom-6 right-6 z-50 w-96 animate-slide-in">
          <div className="bg-gradient-to-br from-gray-900/95 to-black/95 backdrop-blur-xl border border-gray-700 rounded-xl shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gradient-to-r from-red-600/20 to-orange-600/20">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-red-400" />
                <h3 className="font-semibold text-white">Recent Outbreaks</h3>
              </div>
              <button
                onClick={() => setShowRecentPanel(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Outbreak List */}
            <div className="max-h-96 overflow-y-auto">
              {recentOutbreaks.map((alert, index) => (
                <div
                  key={alert.alert_id}
                  className={`px-4 py-3 border-b border-gray-800 hover:bg-gray-800/50 transition-colors ${index === 0 ? 'bg-red-900/10' : ''
                    }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${alert.severity === 'Critical' ? 'bg-red-500 animate-ping' :
                      alert.severity === 'High' ? 'bg-orange-500' :
                        alert.severity === 'Medium' ? 'bg-yellow-500' :
                          'bg-green-500'
                      }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${alert.severity === 'Critical' ? 'bg-red-500/20 text-red-400' :
                          alert.severity === 'High' ? 'bg-orange-500/20 text-orange-400' :
                            alert.severity === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-green-500/20 text-green-400'
                          }`}>
                          {alert.severity}
                        </span>
                        {index === 0 && (
                          <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-500/20 text-blue-400">
                            NEW
                          </span>
                        )}
                      </div>
                      <p className="text-white font-medium text-sm leading-tight">
                        {alert.disease} outbreak in {alert.region}
                      </p>
                      <p className="text-gray-400 text-xs mt-1">
                        {alert.case_count} cases • {formatDate(alert.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 bg-gray-900/50 text-center">
              <p className="text-xs text-gray-500">Auto-hide in 10 seconds</p>
            </div>
          </div>
        </div>
      )}


      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20 rounded-2xl p-6 backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Alerts</p>
                  <p className="text-3xl font-bold text-red-400 mt-1">{statistics.total}</p>
                </div>
                <AlertTriangle className="w-12 h-12 text-red-400 opacity-50" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20 rounded-2xl p-6 backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Critical</p>
                  <p className="text-3xl font-bold text-orange-400 mt-1">{statistics.by_severity.Critical || 0}</p>
                </div>
                <Activity className="w-12 h-12 text-orange-400 opacity-50" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border border-yellow-500/20 rounded-2xl p-6 backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">High Priority</p>
                  <p className="text-3xl font-bold text-yellow-400 mt-1">{statistics.by_severity.High || 0}</p>
                </div>
                <TrendingUp className="w-12 h-12 text-yellow-400 opacity-50" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 border border-green-500/20 rounded-2xl p-6 backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Resolved</p>
                  <p className="text-3xl font-bold text-green-400 mt-1">{statistics.by_status.resolved || 0}</p>
                </div>
                <TrendingDown className="w-12 h-12 text-green-400 opacity-50" />
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 mb-8 backdrop-blur-xl">
          <h2 className="text-xl font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Disease</label>
              <select
                value={selectedDisease}
                onChange={(e) => setSelectedDisease(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="">All Diseases</option>
                {diseases.map((disease) => (
                  <option key={disease} value={disease}>{disease}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Region</label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="">All Regions</option>
                {regions.map((region) => (
                  <option key={region.name} value={region.name}>{region.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Severity</label>
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="">All Severities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="acknowledged">Acknowledged</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold mb-4">Active Alerts ({alerts.length})</h2>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
              <p className="text-gray-400 mt-4">Loading outbreak data...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-center">
              <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-2" />
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {!loading && !error && alerts.length === 0 && (
            <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-12 text-center backdrop-blur-xl">
              <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No alerts found matching your filters</p>
            </div>
          )}

          {!loading && !error && alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`border-2 rounded-2xl p-6 backdrop-blur-xl transition-all duration-300 hover:scale-[1.02] ${getSeverityColor(alert.severity)} relative overflow-hidden`}
            >
              <div className="grid grid-cols-12 gap-6 relative z-10">
                {/* Left Content */}
                <div className="col-span-8">
                  <div className="flex items-center gap-3 mb-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                    <span className="text-sm text-gray-400 flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {alert.region}
                    </span>
                    <span className="text-sm text-gray-400 flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(alert.created_at)}
                    </span>
                    {alert.source && (
                      <span className="text-sm text-blue-400 flex items-center gap-1">
                        <Activity className="w-3 h-3" />
                        {alert.source}
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2">
                    {alert.title || `${alert.disease} Outbreak Detected`}
                  </h3>

                  {alert.description && (
                    <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                      {alert.description}
                    </p>
                  )}

                  <div className="grid grid-cols-3 gap-4 text-sm mt-4">
                    <div>
                      <p className="text-gray-500">Cases</p>
                      <p className="font-medium text-white">{alert.case_count.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Trend</p>
                      <div className="flex items-center gap-1">
                        <span className={`text-xs ${alert.trend === 'increasing' ? 'text-red-400' :
                          alert.trend === 'decreasing' ? 'text-green-400' : 'text-yellow-400'
                          }`}>
                          {alert.trend === 'increasing' ? '↗ Increasing' :
                            alert.trend === 'decreasing' ? '↘ Decreasing' : '→ Stable'}
                        </span>
                      </div>
                    </div>
                    {alert.confidence && (
                      <div>
                        <p className="text-gray-500">Confidence</p>
                        <p className="font-medium text-white">{alert.confidence}%</p>
                      </div>
                    )}
                  </div>

                  {/* References Section */}
                  {alert.sources && alert.sources.length > 0 ? (
                    <ReferencesSection sources={alert.sources} />
                  ) : alert.source_url ? (
                    <div className="mt-4 border-t border-gray-700/50 pt-3">
                      <p className="text-xs text-gray-400 mb-2">Primary Source</p>
                      <a
                        href={alert.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 bg-gray-800/30 p-2 rounded-lg hover:bg-gray-800/50 transition-colors inline-flex"
                      >
                        <ExternalLink className="w-3 h-3" />
                        {alert.source || 'Read Full Report'}
                      </a>
                    </div>
                  ) : null}
                </div>

                {/* Right Content - Large Sparkline */}
                <div className="col-span-4 flex flex-col justify-center items-center h-full min-h-[120px] bg-gray-900/20 rounded-xl p-2 border border-white/5">
                  <div className="w-full h-full flex items-center justify-center">
                    <Sparkline
                      data={alert.weekly_trend || []}
                      color={
                        alert.trend === 'increasing' ? '#ef4444' :
                          alert.trend === 'decreasing' ? '#22c55e' : '#eab308'
                      }
                      width={300}
                      height={100}
                      className="w-full h-full"
                    />
                  </div>
                  <p className="text-[10px] text-gray-500 mt-2 text-center w-full">7-Day Trend Analysis</p>
                </div>
              </div>
            </div>
          ))}
        </div >
      </div >

      {/* Heatmap Modal */}
      <HeatmapModal
        isOpen={showHeatmap}
        onClose={() => setShowHeatmap(false)}
        alerts={alerts}
      />
    </div >
  );
}
