# 🚨 Feature 2: Outbreak Alert System

## Overview

The **Outbreak Alert System** is a real-time disease surveillance dashboard that monitors, displays, and analyzes active disease outbreaks. It features live auto-refreshing alerts, sparkline trend charts, a geographic heatmap, multi-dimensional filtering, and a live news ticker.

It integrates with the backend to pull structured outbreak data and supports time-range filtering from 1 hour to 1 year of historical data.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`src/pages/OutbreakAlert.tsx`](../src/pages/OutbreakAlert.tsx) | Main page — full dashboard UI (740 lines) |
| [`src/components/HeatmapModal.tsx`](../src/components/HeatmapModal.tsx) | Geographic heatmap modal |
| [`src/types/outbreak.ts`](../src/types/outbreak.ts) | TypeScript types |
| [`backend/outbreak-api.js`](../backend/outbreak-api.js) | REST API for outbreak data |
| [`backend/outbreak-data.js`](../backend/outbreak-data.js) | Outbreak data store |
| [`backend/outbreak-detector.js`](../backend/outbreak-detector.js) | Anomaly detection logic |
| [`backend/real-outbreak-detector.js`](../backend/real-outbreak-detector.js) | Real-world data scraping |

---

## 🧩 Features

### 1. Real-Time Auto-Refresh
- Data auto-refreshes every **30 seconds** using `setInterval`
- Toggle button to pause/resume auto-refresh
- Manual "Refresh Data" button for on-demand updates
- Live timestamp counter ("Updated X seconds ago") that ticks every second

```typescript
refreshIntervalRef.current = setInterval(() => {
  fetchData();
}, 30000); // 30s auto-refresh
```

### 2. Severity-Coded Alert Cards
Each outbreak is displayed in a color-coded card:

| Severity | Color | Border |
|----------|-------|--------|
| Critical | Red | `border-red-500` |
| High | Orange | `border-orange-500` |
| Medium | Yellow | `border-yellow-500` |
| Low | Green | `border-green-500` |

Each card shows:
- Disease name + region + date
- Case count, trend direction (↗/↘/→), and AI confidence %
- Source links (government, WHO, news, research badges)
- 7-day trend sparkline chart

### 3. Sparkline Trend Visualization
Custom inline SVG sparklines render the 7-day case trend directly inside each alert card:

```tsx
const Sparkline = ({ data, color, height, width }) => {
  // Plots weekly_trend[] as SVG polyline with area fill gradient
  const points = data.map((val, i) => ({ x: i * stepX, y: height - normalized * height }));
  return <svg>...<polyline points={...} /></svg>;
};
```

Color codes:
- 🔴 Red → Increasing trend
- 🟢 Green → Decreasing trend
- 🟡 Yellow → Stable

### 4. Time Range Filtering
Users can filter alerts by time window:

| Range | Value |
|-------|-------|
| Last Hour | 1h |
| Last Day | 1d |
| Last Week | 1w (default) |
| Last Month | 1m |
| Last 6 Months | 6m |
| Last Year | 1y |

The filter sends a precise ISO timestamp (`startDate`) to the API.

### 5. Multi-Dimensional Filter Panel
4 simultaneous filters:
- **Disease** — dropdown of all disease types in the dataset
- **Region** — dropdown of all regions (fetched from `/api/outbreak/regions`)
- **Severity** — Critical / High / Medium / Low
- **Status** — Open / Acknowledged / Resolved

All filters update the data fetch and statistics simultaneously.

### 6. Statistics Summary Cards
4 metric cards at the top of the dashboard:

```
Total Alerts | Critical Count | High Priority | Resolved
```

Statistics are computed client-side from the filtered alert set, so they always match the current view.

### 7. Live News Ticker
An animated scrolling ticker at the top shows breaking outbreak headlines:

```css
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
```

Critical alerts pulse their indicator dot with `animate-ping`.

### 8. Recent Outbreaks Panel (Toast Notification)
When new alerts are detected on auto-refresh:
- A slide-up panel appears in the **bottom-right corner**
- Shows the last 5 new alerts with severity badges
- Auto-hides after **10 seconds**
- Can be manually dismissed with ✕

```typescript
// Detects newly arrived alerts by comparing IDs
const newAlerts = alerts.filter(a => !prevAlertsRef.current.has(a.alert_id));
```

### 9. Geographic Heatmap
Clicking **"Heatmap"** opens a fullscreen modal showing outbreak density on an interactive map:
- Rendered via `HeatmapModal.tsx`
- Plots all current alerts as heatmap intensity points by region
- Supports zoom and pan

### 10. Source References
Each alert card has an expandable "View Sources & References" section:
- Shows government, WHO, news, and research source badges
- Links to original articles/reports
- Collapsible to keep the UI clean

---

## 🔌 API Endpoints

All served from `backend/outbreak-api.js`:

### `GET /api/outbreak/alerts`
```
?disease=Dengue&region=Indore&severity=High&status=open&startDate=2025-01-01T00:00:00.000Z
```
**Response:**
```json
{
  "success": true,
  "alerts": [{
    "alert_id": "alert_001",
    "disease": "Dengue",
    "region": "Indore",
    "severity": "High",
    "case_count": 1250,
    "trend": "increasing",
    "weekly_trend": [800, 900, 1000, 1100, 1150, 1200, 1250],
    "confidence": 87,
    "status": "open",
    "created_at": "2025-06-01T10:00:00Z",
    "sources": [...]
  }]
}
```

### `GET /api/outbreak/regions`
Returns list of regions with metadata.

### `GET /api/outbreak/diseases`
Returns list of tracked disease names.

---

## 🏗️ Data Flow

```
Backend (outbreak-data.js)
    ↓ REST API (outbreak-api.js)
    ↓ GET /api/outbreak/alerts?[filters]
Frontend (OutbreakAlert.tsx)
    ↓ Statistics computed from response
    ↓ Renders alert cards + sparklines
    ↓ Auto-refreshes every 30s
    ↓ Compares IDs → new alert toast
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + TypeScript |
| Charts | Custom SVG sparklines |
| Map | HeatmapModal (canvas/SVG) |
| Icons | Lucide React |
| Animations | CSS keyframes + Tailwind |
| Backend | Node.js + Express |
| Data | `outbreak-data.js` (structured store) |
| Detection | `outbreak-detector.js` (anomaly logic) |

---

## 🚀 Running

```bash
# Backend (port 5000)
cd backend
npm start

# Frontend (port 5173)
npm run dev
```

Navigate to: `http://localhost:5173/outbreak-alerts`
