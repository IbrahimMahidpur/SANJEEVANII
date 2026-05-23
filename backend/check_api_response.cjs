const fs = require('fs');
const data = JSON.parse(fs.readFileSync('api_response.json', 'utf8'));
const alerts = data.alerts;
const missing = alerts.filter(a => !a.weekly_trend || a.weekly_trend.length === 0);
const output = {
  total: alerts.length,
  missing_count: missing.length,
  first_missing: missing.length > 0 ? {
    alert_id: missing[0].alert_id,
    title: missing[0].title,
    created_at: missing[0].created_at,
    weekly_trend: missing[0].weekly_trend
  } : null
};
fs.writeFileSync('check_result.json', JSON.stringify(output, null, 2));
console.log('Done');
