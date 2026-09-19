const periods = [
  { id: 'weekdays', label: 'Entre setmana' },
  { id: 'weekends', label: 'Caps de setmana' },
];

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export function createRoomSubmenu(floor) {
  const submenu = element('details', 'room-submenu');
  submenu.id = `floor-rooms-${floor.id}`;
  submenu.dataset.floorRooms = floor.id;
  const summary = element('summary', 'room-submenu-toggle');
  summary.append(element('span', '', 'Espais de la planta'), element('span', 'room-count', String(floor.rooms.length)), element('span', 'disclosure-chevron'));
  summary.lastChild.setAttribute('aria-hidden', 'true');
  const list = element('ul', 'room-list');
  list.setAttribute('aria-label', `Espais: ${floor.name.toLocaleLowerCase('ca')}`);

  for (const room of floor.rooms) {
    const item = element('li', 'room-list-item');
    item.dataset.roomId = room.id;
    if (room.kind === 'bathroom') {
      item.classList.add('bathroom-entry');
      const text = element('div', '');
      text.append(element('span', 'room-name', room.name), element('span', 'room-centres', 'Serveis'));
      item.append(text, element('span', 'bathroom-badge', 'WC'));
    } else {
      const details = element('details', 'room-entry');
      const roomSummary = element('summary', 'room-summary');
      const text = element('span', 'room-summary-text');
      text.append(element('span', 'room-name', room.name));
      text.append(element('span', 'room-centres', [...new Set(room.uses.map((use) => use.institution))].join(' · ') || 'Ús no especificat'));
      const chevron = element('span', 'disclosure-chevron');
      chevron.setAttribute('aria-hidden', 'true');
      roomSummary.append(text, chevron);
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
      if (!room.uses.length) content.append(element('p', 'room-activity', 'Ús no especificat.'));
      details.append(roomSummary, content);
      item.append(details);
    }
    list.append(item);
  }
  submenu.append(summary, list);
  return submenu;
}
