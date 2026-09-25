import { roomMarkerLabel } from './room-markers.js';

export function renderDisplayDirectory(floor, floors, t, { showRoomUsage = false } = {}) {
  const indicators = document.getElementById('display-floors');
  indicators.replaceChildren();
  for (const item of floors) {
    const indicator = document.createElement('span');
    indicator.className = 'display-floor';
    indicator.setAttribute('aria-label', item.name);
    if (item.id === floor.id) indicator.setAttribute('aria-current', 'true');
    const code = document.createElement('strong');
    code.textContent = item.code;
    const name = document.createElement('span');
    name.textContent = item.shortName;
    indicator.append(code, name);
    indicators.append(indicator);
  }
  document.getElementById('display-floor-title').textContent = floor.name;
  document.getElementById('display-room-count').textContent = t(floor.rooms.length === 1 ? 'roomCountOne' : 'roomCountMany', { count: floor.rooms.length });
  const list = document.getElementById('display-rooms');
  list.replaceChildren();
  floor.rooms.forEach((room) => {
    const item = document.createElement('li');
    const code = document.createElement('span');
    code.className = 'display-room-code';
    code.textContent = roomMarkerLabel(room);
    const name = document.createElement('span');
    // Classroom codes already identify the room; only add useful secondary text.
    if (code.textContent === room.name) {
      if (showRoomUsage && room.showUsage) {
        name.className = 'display-room-centres';
        name.textContent = [...new Set(room.uses.map((use) => use.institution))].join(' · ');
      }
    } else name.textContent = room.name;
    item.append(code);
    if (name.textContent) item.append(name);
    list.append(item);
  });
}
