import { useEffect, useRef, useState } from 'react';
import { X, MapPin, TrendingUp, TrendingDown, Minus, Users, Calendar, AlertTriangle, Layers } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import type { OutbreakAlert } from '../types/outbreak';

interface HeatmapModalProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: OutbreakAlert[];
}

export default function HeatmapModal({ isOpen, onClose, alerts }: HeatmapModalProps) {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const heatLayerRef = useRef<any>(null);
  const [selectedAlert, setSelectedAlert] = useState<OutbreakAlert | null>(null);
  const [showHeatLayer, setShowHeatLayer] = useState(true);
  const [showMarkers, setShowMarkers] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [stats, setStats] = useState({ critical: 0, high: 0, medium: 0, low: 0, total: 0 });

  // Calculate statistics
  useEffect(() => {
    const critical = alerts.filter(a => a.severity === 'Critical').length;
    const high = alerts.filter(a => a.severity === 'High').length;
    const medium = alerts.filter(a => a.severity === 'Medium').length;
    const low = alerts.filter(a => a.severity === 'Low').length;
    setStats({ critical, high, medium, low, total: alerts.length });
  }, [alerts]);

  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    // Initialize map centered on India
    if (!mapRef.current) {
      mapRef.current = L.map(containerRef.current, {
        zoomControl: false, // We'll add custom controls
      }).setView([20.5937, 78.9629], 5);

      // Use Google Maps tiles
      L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google Maps'
      }).addTo(mapRef.current);
    }

    // Clear existing layers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];
    if (heatLayerRef.current) {
      heatLayerRef.current.remove();
      heatLayerRef.current = null;
    }

    // Filter alerts by severity
    const filteredAlerts = filterSeverity === 'all'
      ? alerts
      : alerts.filter(a => a.severity === filterSeverity);

    // Prepare heatmap data
    const heatData: [number, number, number][] = filteredAlerts
      .filter(alert => alert.lat && alert.lon)
      .map(alert => {
        let intensity = alert.case_count / 100;
        switch (alert.severity) {
          case 'Critical': intensity *= 3; break;
          case 'High': intensity *= 2; break;
          case 'Medium': intensity *= 1.5; break;
          default: intensity *= 1;
        }
        return [alert.lat, alert.lon, Math.min(intensity, 10)];
      });

    // Add heatmap layer
    if (heatData.length > 0 && showHeatLayer) {
      // @ts-ignore
      heatLayerRef.current = L.heatLayer(heatData, {
        radius: 30,
        blur: 40,
        maxZoom: 10,
        max: 1.0,
        gradient: {
          0.0: 'rgba(0, 255, 0, 0)',
          0.2: '#00ff00',
          0.4: '#ffff00',
          0.6: '#ff9900',
          0.8: '#ff4400',
          1.0: '#ff0000'
        }
      }).addTo(mapRef.current);
    }

    // Add interactive markers
    if (showMarkers) {
      filteredAlerts
        .filter(alert => alert.lat && alert.lon)
        .forEach(alert => {
          const iconColor =
            alert.severity === 'Critical' ? '#ef4444' :
              alert.severity === 'High' ? '#f97316' :
                alert.severity === 'Medium' ? '#eab308' : '#22c55e';

          const pulseAnimation = alert.severity === 'Critical'
            ? 'animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;'
            : '';

          const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `
              <div style="
                position: relative;
                width: 32px;
                height: 32px;
                z-index: 1000;
              ">
                ${alert.severity === 'Critical' ? `
                  <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 32px;
                    height: 32px;
                    background-color: ${iconColor};
                    border-radius: 50%;
                    opacity: 0.3;
                    ${pulseAnimation}
                  "></div>
                ` : ''}
                <div style="
                  position: absolute;
                  top: 4px;
                  left: 4px;
                  background: linear-gradient(135deg, ${iconColor} 0%, ${iconColor}dd 100%);
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  border: 3px solid white;
                  box-shadow: 0 4px 12px rgba(0,0,0,0.4), 0 0 0 4px ${iconColor}22;
                  cursor: pointer;
                  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-size: 10px;
                  font-weight: bold;
                  color: white;
                  z-index: 10000;
                ">
                  ${alert.case_count > 100 ? '!' : ''}
                </div>
              </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
          });

          const marker = L.marker([alert.lat, alert.lon], { icon: customIcon });

          // Add hover tooltip with quick info
          const tooltipContent = `
            <div style="font-family: system-ui, -apple-system, sans-serif; min-width: 200px;">
              <div style="
                font-size: 14px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 6px;
                padding-bottom: 6px;
                border-bottom: 2px solid ${iconColor}44;
              ">${alert.disease}</div>
              <div style="
                font-size: 12px;
                color: #6b7280;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 4px;
              ">
                📍 ${alert.region}
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px;">
                <div>
                  <div style="font-size: 10px; color: #9ca3af; text-transform: uppercase; margin-bottom: 2px;">Cases</div>
                  <div style="font-size: 16px; font-weight: 700; color: #1f2937;">${alert.case_count.toLocaleString()}</div>
                </div>
                <div>
                  <div style="font-size: 10px; color: #9ca3af; text-transform: uppercase; margin-bottom: 2px;">Severity</div>
                  <div style="
                    font-size: 11px;
                    font-weight: 600;
                    color: ${iconColor};
                    background: ${iconColor}22;
                    padding: 3px 8px;
                    border-radius: 4px;
                    display: inline-block;
                  ">${alert.severity}</div>
                </div>
              </div>
              <div style="
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px solid #e5e7eb;
                font-size: 11px;
                color: #6b7280;
                text-align: center;
              ">Click for full details</div>
            </div>
          `;

          marker.bindTooltip(tooltipContent, {
            direction: 'top',
            offset: [0, -10],
            opacity: 0.95,
            className: 'custom-tooltip'
          });

          marker.on('click', () => {
            setSelectedAlert(alert);
          });

          marker.on('mouseover', (e) => {
            const marker = e.target as L.Marker;
            const el = marker.getElement();
            if (el) {
              const inner = el.querySelector('div > div:last-child') as HTMLElement;
              if (inner) {
                inner.style.transform = 'scale(1.3)';
                inner.style.zIndex = '10000';
              }
            }
          });

          marker.on('mouseout', (e) => {
            const marker = e.target as L.Marker;
            const el = marker.getElement();
            if (el) {
              const inner = el.querySelector('div > div:last-child') as HTMLElement;
              if (inner) {
                inner.style.transform = 'scale(1)';
              }
            }
          });

          marker.addTo(mapRef.current!);
          markersRef.current.push(marker);
        });
    }

    return () => {
      if (mapRef.current) {
        markersRef.current.forEach(marker => marker.remove());
        markersRef.current = [];
        if (heatLayerRef.current) {
          heatLayerRef.current.remove();
          heatLayerRef.current = null;
        }
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [isOpen, alerts, showHeatLayer, showMarkers, filterSeverity]);

  if (!isOpen) return null;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return '#ef4444';
      case 'High': return '#f97316';
      case 'Medium': return '#eab308';
      default: return '#22c55e';
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-md animate-in fade-in duration-300">
      <div className="relative w-[98vw] h-[95vh] bg-gradient-to-br from-gray-900 via-gray-900 to-black rounded-3xl overflow-hidden border border-gray-700/50 shadow-2xl">

        {/* Header */}
        <div className="absolute top-0 left-0 right-0 z-20 bg-gradient-to-b from-black/95 via-black/80 to-transparent p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl">
                  <MapPin className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-white tracking-tight">
                    Interactive Outbreak Heatmap
                  </h2>
                  <p className="text-sm text-gray-400 mt-1">
                    Real-time visualization • Click markers for details • {stats.total} active alerts
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-3 bg-gray-800/80 hover:bg-gray-700 rounded-xl transition-all duration-200 hover:scale-105 group"
              aria-label="Close heatmap"
            >
              <X className="w-6 h-6 text-gray-400 group-hover:text-white transition-colors" />
            </button>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-5 gap-3 mt-4">
            <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 backdrop-blur-sm rounded-xl p-3 border border-gray-700/50">
              <div className="text-xs text-gray-400 mb-1">Total Alerts</div>
              <div className="text-2xl font-bold text-white">{stats.total}</div>
            </div>
            <div className="bg-gradient-to-br from-red-900/30 to-red-950/30 backdrop-blur-sm rounded-xl p-3 border border-red-500/30 cursor-pointer hover:scale-105 transition-transform"
              onClick={() => setFilterSeverity(filterSeverity === 'Critical' ? 'all' : 'Critical')}>
              <div className="text-xs text-red-300 mb-1">Critical</div>
              <div className="text-2xl font-bold text-red-400">{stats.critical}</div>
            </div>
            <div className="bg-gradient-to-br from-orange-900/30 to-orange-950/30 backdrop-blur-sm rounded-xl p-3 border border-orange-500/30 cursor-pointer hover:scale-105 transition-transform"
              onClick={() => setFilterSeverity(filterSeverity === 'High' ? 'all' : 'High')}>
              <div className="text-xs text-orange-300 mb-1">High</div>
              <div className="text-2xl font-bold text-orange-400">{stats.high}</div>
            </div>
            <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-950/30 backdrop-blur-sm rounded-xl p-3 border border-yellow-500/30 cursor-pointer hover:scale-105 transition-transform"
              onClick={() => setFilterSeverity(filterSeverity === 'Medium' ? 'all' : 'Medium')}>
              <div className="text-xs text-yellow-300 mb-1">Medium</div>
              <div className="text-2xl font-bold text-yellow-400">{stats.medium}</div>
            </div>
            <div className="bg-gradient-to-br from-green-900/30 to-green-950/30 backdrop-blur-sm rounded-xl p-3 border border-green-500/30 cursor-pointer hover:scale-105 transition-transform"
              onClick={() => setFilterSeverity(filterSeverity === 'Low' ? 'all' : 'Low')}>
              <div className="text-xs text-green-300 mb-1">Low</div>
              <div className="text-2xl font-bold text-green-400">{stats.low}</div>
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div ref={containerRef} className="absolute top-[180px] left-0 right-0 bottom-0 w-full" style={{ zIndex: 1 }} />

        {/* Layer Controls */}
        <div className="absolute top-48 right-6 z-20 bg-black/80 backdrop-blur-xl rounded-2xl p-4 border border-gray-700/50 space-y-3">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Layers</div>
          <button
            onClick={() => setShowHeatLayer(!showHeatLayer)}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all ${showHeatLayer
              ? 'bg-gradient-to-r from-orange-600 to-red-600 text-white shadow-lg'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
          >
            <Layers className="w-4 h-4" />
            <span className="text-sm font-medium">Heatmap</span>
          </button>
          <button
            onClick={() => setShowMarkers(!showMarkers)}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all ${showMarkers
              ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
          >
            <MapPin className="w-4 h-4" />
            <span className="text-sm font-medium">Markers</span>
          </button>
        </div>

        {/* Legend */}
        <div className="absolute bottom-6 left-6 z-20 bg-black/90 backdrop-blur-xl rounded-2xl p-5 border border-gray-700/50 max-w-xs">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <div className="w-1 h-4 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full"></div>
            Map Legend
          </h3>

          {showHeatLayer && (
            <div className="mb-4 pb-4 border-b border-gray-700/50">
              <div className="text-xs text-gray-400 mb-2 uppercase tracking-wide">Heat Intensity</div>
              <div className="relative h-3 rounded-full overflow-hidden mb-2" style={{
                background: 'linear-gradient(to right, #00ff00, #ffff00, #ff9900, #ff4400, #ff0000)'
              }}>
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>Low</span>
                <span>Moderate</span>
                <span>High</span>
              </div>
            </div>
          )}

          {showMarkers && (
            <div>
              <div className="text-xs text-gray-400 mb-3 uppercase tracking-wide">Severity Levels</div>
              <div className="space-y-2.5">
                {[
                  { label: 'Critical', color: '#ef4444', count: stats.critical },
                  { label: 'High', color: '#f97316', count: stats.high },
                  { label: 'Medium', color: '#eab308', count: stats.medium },
                  { label: 'Low', color: '#22c55e', count: stats.low }
                ].map(({ label, color, count }) => (
                  <div key={label} className="flex items-center justify-between group cursor-pointer hover:bg-gray-800/50 rounded-lg p-1.5 transition-colors"
                    onClick={() => setFilterSeverity(filterSeverity === label ? 'all' : label)}>
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-4 h-4 rounded-full border-2 border-white shadow-lg" style={{ backgroundColor: color }}></div>
                        {filterSeverity === label && (
                          <div className="absolute inset-0 rounded-full border-2 border-white animate-ping" style={{ backgroundColor: color }}></div>
                        )}
                      </div>
                      <span className="text-sm text-gray-300 group-hover:text-white transition-colors">{label}</span>
                    </div>
                    <span className="text-xs font-semibold text-gray-500 group-hover:text-gray-300 transition-colors">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Selected Alert Detail Panel */}
        {selectedAlert && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 z-30 w-[500px] bg-gradient-to-br from-gray-900 via-gray-900 to-black backdrop-blur-2xl rounded-2xl border border-gray-700/50 shadow-2xl overflow-hidden animate-in slide-in-from-top duration-300">
            <div className="relative">
              {/* Header with gradient */}
              <div className="p-6 bg-gradient-to-r from-gray-800/50 to-gray-900/50 border-b border-gray-700/50">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl" style={{
                      backgroundColor: `${getSeverityColor(selectedAlert.severity)}22`,
                      border: `2px solid ${getSeverityColor(selectedAlert.severity)}44`
                    }}>
                      <AlertTriangle className="w-5 h-5" style={{ color: getSeverityColor(selectedAlert.severity) }} />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{selectedAlert.disease}</h3>
                      <p className="text-sm text-gray-400 flex items-center gap-1.5 mt-1">
                        <MapPin className="w-3.5 h-3.5" />
                        {selectedAlert.region}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedAlert(null)}
                    className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-400" />
                  </button>
                </div>

                {/* Severity Badge */}
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold"
                  style={{
                    backgroundColor: `${getSeverityColor(selectedAlert.severity)}22`,
                    color: getSeverityColor(selectedAlert.severity),
                    border: `1px solid ${getSeverityColor(selectedAlert.severity)}44`
                  }}>
                  <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: getSeverityColor(selectedAlert.severity) }}></div>
                  {selectedAlert.severity} Severity
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4 p-6">
                <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 text-gray-400 text-xs mb-2">
                    <Users className="w-3.5 h-3.5" />
                    <span className="uppercase tracking-wide">Total Cases</span>
                  </div>
                  <div className="text-3xl font-bold text-white">{selectedAlert.case_count.toLocaleString()}</div>
                </div>

                <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 text-gray-400 text-xs mb-2">
                    {selectedAlert.trend === 'increasing' ? <TrendingUp className="w-3.5 h-3.5" /> :
                      selectedAlert.trend === 'decreasing' ? <TrendingDown className="w-3.5 h-3.5" /> :
                        <Minus className="w-3.5 h-3.5" />}
                    <span className="uppercase tracking-wide">Trend</span>
                  </div>
                  <div className={`text-2xl font-bold ${selectedAlert.trend === 'increasing' ? 'text-red-400' :
                    selectedAlert.trend === 'decreasing' ? 'text-green-400' : 'text-yellow-400'
                    }`}>
                    {selectedAlert.trend === 'increasing' ? '↗ Rising' :
                      selectedAlert.trend === 'decreasing' ? '↘ Falling' : '→ Stable'}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 text-gray-400 text-xs mb-2">
                    <Calendar className="w-3.5 h-3.5" />
                    <span className="uppercase tracking-wide">Status</span>
                  </div>
                  <div className="text-lg font-semibold text-gray-300 capitalize">{selectedAlert.status}</div>
                </div>

                {selectedAlert.confidence && (
                  <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-4 border border-gray-700/30">
                    <div className="flex items-center gap-2 text-gray-400 text-xs mb-2">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span className="uppercase tracking-wide">Confidence</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-400">{selectedAlert.confidence}%</div>
                  </div>
                )}
              </div>

              {/* Description */}
              {selectedAlert.description && (
                <div className="px-6 pb-6">
                  <div className="bg-gradient-to-br from-gray-800/30 to-gray-900/30 rounded-xl p-4 border border-gray-700/30">
                    <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Details</div>
                    <p className="text-sm text-gray-300 leading-relaxed">{selectedAlert.description}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Custom CSS */}
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.1; transform: scale(1.5); }
          }
          .custom-marker:hover div > div:last-child {
            transform: scale(1.3) !important;
            z-index: 1000 !important;
          }
          .custom-tooltip .leaflet-tooltip {
            background: white;
            border: none;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(0, 0, 0, 0.05);
            padding: 12px;
            font-family: system-ui, -apple-system, sans-serif;
          }
          .custom-tooltip .leaflet-tooltip-top:before {
            border-top-color: white;
          }
        `}</style>
      </div>
    </div>
  );
}
