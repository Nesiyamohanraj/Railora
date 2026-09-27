/**
 * Geographical & Position Interpolation Utilities — RailFlow
 */

/**
 * Interpolates train lat/lng coordinates between previous station and next station
 * based on progressFraction (0.0 to 1.0).
 */
export function interpolateTrainPosition(prevCoords, nextCoords, progressFraction = 0.5) {
  if (!prevCoords || !nextCoords) {
    return [25.2138, 75.8648]; // Fallback Kota coordinates
  }

  const fraction = Math.min(Math.max(progressFraction, 0.0), 1.0);
  const lat = prevCoords[0] + (nextCoords[0] - prevCoords[0]) * fraction;
  const lng = prevCoords[1] + (nextCoords[1] - prevCoords[1]) * fraction;

  return [parseFloat(lat.toFixed(6)), parseFloat(lng.toFixed(6))];
}

/**
 * Calculates bounding box padding around route station coordinates.
 */
export function calculateRouteBounds(stations = []) {
  if (!stations || stations.length === 0) {
    return [
      [28.6139, 77.2090], // NDLS
      [18.9696, 72.8193]  // MMCT
    ];
  }

  const lats = stations.map(s => s.lat).filter(Boolean);
  const lngs = stations.map(s => s.lng).filter(Boolean);

  if (lats.length === 0 || lngs.length === 0) {
    return [
      [28.6139, 77.2090],
      [18.9696, 72.8193]
    ];
  }

  const minLat = Math.min(...lats) - 0.5;
  const maxLat = Math.max(...lats) + 0.5;
  const minLng = Math.min(...lngs) - 0.5;
  const maxLng = Math.max(...lngs) + 0.5;

  return [
    [minLat, minLng],
    [maxLat, maxLng]
  ];
}
