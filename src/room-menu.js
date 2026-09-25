function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export function createRoomSubmenu(floor, { onSelect, periods, t, language, showRoomUsage = false }) {
  const submenu = element('details', 'room-submenu');
  submenu.id = `floor-rooms-${floor.id}`;
  submenu.dataset.floorRooms = floor.id;
  const summary = element('summary', 'room-submenu-toggle');
  summary.append(element('span', '', t('roomsToggle')), element('span', 'room-count', String(floor.rooms.length)), element('span', 'disclosure-chevron'));
  summary.lastChild.setAttribute('aria-hidden', 'true');
  const list = element('ul', 'room-list');
  list.setAttribute('aria-label', t('roomsList', { floor: floor.name.toLocaleLowerCase(language) }));

  for (const room of floor.rooms) {
    const item = element('li', 'room-list-item');
    item.dataset.roomId = room.id;
    if (room.kind === 'bathroom' || room.showUsage === false) {
      const isBathroom = room.kind === 'bathroom';
      item.classList.add(isBathroom ? 'bathroom-entry' : 'common-space-entry');
      const service = element('button', 'service-entry room-select-button');
      service.type = 'button';
      service.setAttribute('aria-label', t(room.overlay ? 'showRoom' : 'selectRoom', { room: room.name }));
      service.setAttribute('aria-pressed', 'false');
      if (room.overlay) service.setAttribute('aria-controls', 'room-overlay');
      service.dataset.roomSelect = room.id;
      service.addEventListener('click', () => onSelect(floor, room));
      item.append(service);
      const text = element('div', '');
      text.append(element('span', 'room-name', room.name), element('span', 'room-centres', room.subtitle ?? t(isBathroom ? 'services' : 'commonSpace')));
      const badge = element('span', 'service-badge');
      badge.setAttribute('aria-hidden', 'true');
      if (room.iconImage) {
        const image = element('img', 'icon');
        image.src = room.iconImage;
        image.alt = '';
        badge.append(image);
      } else if (room.badge) {
        badge.textContent = room.badge;
      } else {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.classList.add('icon');
        svg.setAttribute('focusable', 'false');
        const use = document.createElementNS(svg.namespaceURI, 'use');
        use.setAttribute('href', `#icon-${room.icon ?? 'layers'}`);
        svg.append(use);
        badge.append(svg);
      }
      service.append(text, badge);
    } else if (!showRoomUsage) {
      const button = element('button', 'room-summary room-select-button');
      button.type = 'button';
      button.setAttribute('aria-label', t(room.overlay ? 'showRoom' : 'selectRoom', { room: room.name }));
      button.setAttribute('aria-pressed', 'false');
      if (room.overlay) button.setAttribute('aria-controls', 'room-overlay');
      button.dataset.roomSelect = room.id;
      button.append(element('span', 'room-name', room.name));
      button.addEventListener('click', () => onSelect(floor, room));
      item.append(button);
    } else {
      const details = element('details', 'room-entry');
      details.name = 'room-information';
      const roomSummary = element('summary', 'room-summary');
      const text = element('span', 'room-summary-text');
      text.append(element('span', 'room-name', room.name));
      text.append(element('span', 'room-centres', [...new Set(room.uses.map((use) => use.institution))].join(' · ') || t('unspecifiedUse')));
      const chevron = element('span', 'disclosure-chevron');
      chevron.setAttribute('aria-hidden', 'true');
      roomSummary.append(text, chevron);
      roomSummary.dataset.roomSelect = room.id;
      if (room.overlay) roomSummary.setAttribute('aria-controls', 'room-overlay');
      roomSummary.addEventListener('click', () => onSelect(floor, room));
      const content = element('div', 'room-uses');
      for (const period of periods) {
        const uses = room.uses.filter((use) => use.period === period.id);
        if (!uses.length) continue;
        const section = element('section', 'room-period');
        section.append(element('h3', 'room-period-title', period.label));
        const definitions = element('dl', 'room-use-list');
        for (const use of uses) {
          const entry = element('div', 'room-use');
          entry.append(element('dt', 'room-institution', use.institution), element('dd', 'room-activity', use.activity));
          definitions.append(entry);
        }
        section.append(definitions);
        content.append(section);
      }
      if (!room.uses.length) content.append(element('p', 'room-activity', t('unspecifiedUse')));
      details.append(roomSummary, content);
      item.append(details);
    }
    list.append(item);
  }
  submenu.append(summary, list);
  return submenu;
}
