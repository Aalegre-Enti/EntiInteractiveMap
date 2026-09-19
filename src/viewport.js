export const MIN_ZOOM = 1;
export const MAX_ZOOM = 5;
export const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export function fitScale(viewportWidth, viewportHeight, imageWidth, imageHeight, paddingScale = 0.94) {
  return Math.min(viewportWidth / imageWidth, viewportHeight / imageHeight) * paddingScale;
}

export function constrainOffset(offset, viewportSize, imageSize) {
  if (imageSize <= viewportSize) return (viewportSize - imageSize) / 2;
  return clamp(offset, viewportSize - imageSize - 24, 24);
}

export function zoomAround(view, nextZoom, anchorX, anchorY, baseScale, maxZoom = MAX_ZOOM) {
  const zoom = clamp(nextZoom, MIN_ZOOM, maxZoom);
  const scale = baseScale * zoom;
  const ratio = scale / (baseScale * view.zoom);
  return { zoom, x: anchorX - (anchorX - view.x) * ratio, y: anchorY - (anchorY - view.y) * ratio };
}
