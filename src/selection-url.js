export function selectionHash(floor, room = null) {
  return `#planta-${floor.id}${room ? `/sala/${encodeURIComponent(room.code)}` : ''}`;
}

export function selectionFromHash(hash, floors) {
  if (!hash || hash === '#') return { floor: floors[0], room: null };
  const match = hash.match(/^#planta-([a-zA-Z0-9_-]+)(?:\/sala\/([^/]+))?$/);
  if (!match) return null;
  const floor = floors.find((item) => item.id === match[1]);
  if (!floor) return null;
  let code;
  try { code = decodeURIComponent(match[2] ?? ''); } catch { /* Keep the valid floor if the room link is malformed. */ }
  return { floor, room: floor.rooms.find((item) => item.code === code) ?? null };
}
