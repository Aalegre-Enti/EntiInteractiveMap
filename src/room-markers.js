export function roomMarkerLabel(room) {
  return room.marker?.label ?? room.name;
}

function appendMarkerContents(marker, room) {
  const dot = document.createElement('span');
  dot.className = 'room-marker-dot';
  dot.setAttribute('aria-hidden', 'true');
  const label = document.createElement('span');
  label.className = 'room-marker-label';
  label.textContent = roomMarkerLabel(room);
  label.setAttribute('aria-hidden', 'true');
  marker.append(dot, label);
}

// Coordinates are percentages of the full floor image, just like “Ets aquí”.
export function createRoomMarkers(floor, { onSelect, t, display = false }) {
  const fragment = document.createDocumentFragment();
  for (const room of floor.rooms) {
    if (!room.marker) continue;
    if (display) {
      const marker = document.createElement('span');
      marker.className = 'room-marker display-room-marker';
      marker.dataset.labelPosition = room.marker.labelPosition;
      marker.style.left = `${room.marker.x}%`;
      marker.style.top = `${room.marker.y}%`;
      marker.setAttribute('role', 'img');
      const label = roomMarkerLabel(room);
      marker.setAttribute('aria-label', label === room.name ? room.name : `${label}: ${room.name}`);
      appendMarkerContents(marker, room);
      fragment.append(marker);
      continue;
    }
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
    appendMarkerContents(button, room);
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
