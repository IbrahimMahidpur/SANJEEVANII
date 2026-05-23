
const data = [301, 284, 299, 283, 313, 304, 311];
const height = 100;
const width = 300;

if (!data || data.length < 2) {
  console.log('Data invalid');
} else {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const stepX = width / (data.length - 1);

  const points = data.map((val, i) => {
    const x = i * stepX;
    const y = height - ((val - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  console.log('Points:', points);

  const areaPath = `${points} ${width},${height} 0,${height}`;
  console.log('Area Path:', areaPath);

  // Check for NaN
  if (points.includes('NaN')) {
    console.log('ERROR: NaN found in points');
  } else {
    console.log('SUCCESS: Valid paths generated');
  }
}
