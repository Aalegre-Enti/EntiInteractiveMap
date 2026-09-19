// Coordinates are percentages of the full floor image, just like “Ets aquí”.
export function createRoomMarkers(floor, { onSelect, t }) {
  const fragment = document.createDocumentFragment();
  for (const room of floor.rooms) {
    if (!room.marker) continue;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'room-marker';
    button.dataset.roomMarker = room.id;
    button.dataset.labelPosition = room.marker.labelPosition;
    button.style.left = `${room.marker.x}%`;
    button.style.top = `${room.marker.y}%`;
    button.setAttribute('aria-label', t('selectRoom', { room: room.name }));
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-controls', `floor-rooms-${floor.id}${room.overlay ? ' room-overlay' : ''}`);
    button.title = room.name;
    const dot = document.createElement('span');
    dot.className = 'room-marker-dot';
    dot.setAttribute('aria-hidden', 'true');
    const label = document.createElement('span');
    label.className = 'room-marker-label';
    label.textContent = room.marker.label ?? room.name;
    label.setAttribute('aria-hidden', 'true');
    button.append(dot, label);
    button.addEventListener('click', () => onSelect(floor, room));
    fragment.append(button);
  }
  return fragment;
}

export function updateRoomMarkers(layer, roomId) {
  for (const marker of layer.querySelectorAll('[data-room-marker]')) {
    marker.setAttribute('aria-pressed', String(marker.dataset.roomMarker === roomId));
  }
}
