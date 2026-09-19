const iconNames = new Set(['map', 'layers', 'help', 'plus', 'minus', 'fit', 'expand', 'close', 'arrow', 'move', 'info', 'pin', 'office', 'dining', 'study', 'lobby', 'entrance', 'tutoring', 'vending', 'terrace', 'elevator', 'stairs', 'auditorium']);

export function formatText(texts, key, values = {}) {
  return (texts[key] ?? key).replace(/\{(\w+)\}/g, (match, name) => Object.hasOwn(values, name) ? String(values[name]) : match);
}

export function validateConfig(input) {
  const fail = (path, message) => { throw new Error(`config.json · ${path}: ${message}`); };
  const object = (value, path) => { if (!value || typeof value !== 'object' || Array.isArray(value)) fail(path, 'cal un objecte'); return value; };
  const string = (value, path) => { if (typeof value !== 'string' || !value.trim()) fail(path, 'cal un text no buit'); return value; };
  const number = (value, path, min, max = Infinity) => { if (!Number.isFinite(value) || value < min || value > max) fail(path, `cal un nombre entre ${min} i ${max}`); return value; };
  const boolean = (value, path) => { if (typeof value !== 'boolean') fail(path, 'cal true o false'); return value; };
  const asset = (value, path) => { string(value, path); if (/^(?:[a-z][\w+.-]*:|\/\/)/i.test(value) && !/^https?:\/\//i.test(value)) fail(path, 'ruta o URL HTTP no vàlida'); return value; };
  const icon = (value, path) => { if (!iconNames.has(value)) fail(path, `icona desconeguda: ${value}`); return value; };
  const unique = (values, path) => { if (new Set(values).size !== values.length) fail(path, 'hi ha identificadors duplicats'); };
  object(input, 'arrel');
  if (input.version !== 1) fail('version', 'versió no admesa');
  const config = structuredClone(input);
  object(config.site, 'site');
  for (const key of ['name', 'language', 'description']) string(config.site[key], `site.${key}`);
  try { new Intl.Locale(config.site.language); } catch { fail('site.language', 'idioma no vàlid'); }
  config.site.caption ??= '';
  if (config.site.favicon) asset(config.site.favicon, 'site.favicon');
  config.site.icon = icon(config.site.icon ?? 'map', 'site.icon');
  object(config.theme, 'theme');
  for (const [key, value] of Object.entries(config.theme)) {
    if (key === 'fontFamily') string(value, 'theme.fontFamily');
    else if (!/^#[\da-f]{6}$/i.test(value)) fail(`theme.${key}`, 'cal un color #RRGGBB');
  }
  string(config.theme.brand, 'theme.brand');
  object(config.view, 'view');
  number(config.view.maxZoom, 'view.maxZoom', 1, 50);
  number(config.view.zoomStep, 'view.zoomStep', 1.01, 5);
  number(config.view.fitScale, 'view.fitScale', .1, 1);
  number(config.view.wheelSensitivity, 'view.wheelSensitivity', .0001, .1);
  number(config.view.panStep, 'view.panStep', 1, 1000);
  number(config.view.fastPanStep, 'view.fastPanStep', 1, 1000);
  boolean(config.view.mobileMenuCollapsed, 'view.mobileMenuCollapsed');
  object(config.overlay, 'overlay');
  for (const key of ['opacity', 'pulseOpacity']) number(config.overlay[key], `overlay.${key}`, 0, 1);
  number(config.overlay.pulseDuration, 'overlay.pulseDuration', .1, 10);
  number(config.overlay.pulseCount, 'overlay.pulseCount', 0, 20);
  if (!Number.isInteger(config.overlay.pulseCount)) fail('overlay.pulseCount', 'cal un enter');
  object(config.here, 'here');
  string(config.here.label, 'here.label');
  number(config.here.otherFloorOpacity, 'here.otherFloorOpacity', .1, 1);
  number(config.here.size, 'here.size', 16, 64);
  config.roomMarkers ??= {};
  object(config.roomMarkers, 'roomMarkers');
  config.roomMarkers.enabled ??= true;
  config.roomMarkers.inactiveOpacity ??= .68;
  config.roomMarkers.dotSize ??= 9;
  config.roomMarkers.labelSize ??= 11;
  boolean(config.roomMarkers.enabled, 'roomMarkers.enabled');
  number(config.roomMarkers.inactiveOpacity, 'roomMarkers.inactiveOpacity', .1, 1);
  number(config.roomMarkers.dotSize, 'roomMarkers.dotSize', 4, 24);
  number(config.roomMarkers.labelSize, 'roomMarkers.labelSize', 9, 18);
  if (!Array.isArray(config.periods)) fail('periods', 'cal una llista');
  config.periods.forEach((period, i) => { object(period, `periods[${i}]`); string(period.id, `periods[${i}].id`); string(period.label, `periods[${i}].label`); });
  unique(config.periods.map((period) => period.id), 'periods');
  object(config.texts, 'texts');
  for (const [key, value] of Object.entries(config.texts)) if (typeof value !== 'string') fail(`texts.${key}`, 'cal un text');
  if (!Array.isArray(config.floors) || !config.floors.length) fail('floors', 'cal almenys una planta');
  const roomIds = [];
  config.floors.forEach((floor, i) => {
    const path = `floors[${i}]`;
    object(floor, path);
    if (typeof floor.id !== 'string' || !/^[a-zA-Z0-9_-]+$/.test(floor.id)) fail(`${path}.id`, 'utilitza lletres, números, guions o guions baixos');
    string(floor.name, `${path}.name`);
    floor.code ??= floor.id;
    floor.shortName ??= floor.name;
    string(floor.code, `${path}.code`);
    string(floor.shortName, `${path}.shortName`);
    if (!Number.isSafeInteger(floor.level)) fail(`${path}.level`, 'cal un nivell enter (pot ser negatiu)');
    asset(floor.image, `${path}.image`);
    number(floor.width, `${path}.width`, 1);
    number(floor.height, `${path}.height`, 1);
    floor.rooms ??= [];
    if (!Array.isArray(floor.rooms)) fail(`${path}.rooms`, 'cal una llista');
    floor.rooms.forEach((room, j) => {
      const roomPath = `${path}.rooms[${j}]`;
      object(room, roomPath);
      string(room.code, `${roomPath}.code`);
      room.id ??= `${floor.id}-${room.code}`;
      string(room.id, `${roomPath}.id`);
      roomIds.push(room.id);
      room.floorId = floor.id;
      room.name ??= room.code;
      string(room.name, `${roomPath}.name`);
      room.kind ??= 'room';
      if (!['room', 'common', 'bathroom'].includes(room.kind)) fail(`${roomPath}.kind`, 'utilitza room, common o bathroom');
      room.showUsage ??= room.kind === 'room';
      boolean(room.showUsage, `${roomPath}.showUsage`);
      if (room.overlay) asset(room.overlay, `${roomPath}.overlay`);
      if (room.icon) icon(room.icon, `${roomPath}.icon`);
      if (room.iconImage) asset(room.iconImage, `${roomPath}.iconImage`);
      for (const key of ['subtitle', 'badge']) if (room[key] !== undefined && typeof room[key] !== 'string') fail(`${roomPath}.${key}`, 'cal un text');
      if (room.marker != null) {
        object(room.marker, `${roomPath}.marker`);
        for (const key of ['x', 'y']) number(room.marker[key], `${roomPath}.marker.${key}`, 0, 100);
        if (room.marker.label !== undefined) string(room.marker.label, `${roomPath}.marker.label`);
        room.marker.labelPosition ??= 'bottom';
        if (!['top', 'bottom', 'left', 'right'].includes(room.marker.labelPosition)) fail(`${roomPath}.marker.labelPosition`, 'utilitza top, bottom, left o right');
      }
      room.uses ??= [];
      if (!Array.isArray(room.uses)) fail(`${roomPath}.uses`, 'cal una llista');
      room.uses.forEach((use, k) => {
        object(use, `${roomPath}.uses[${k}]`);
        for (const key of ['institution', 'activity']) string(use[key], `${roomPath}.uses[${k}].${key}`);
        if (!config.periods.some((period) => period.id === use.period)) fail(`${roomPath}.uses[${k}].period`, 'període desconegut');
      });
    });
    unique(floor.rooms.map((room) => room.code), `${path}.rooms`);
    floor.points ??= [];
    if (!Array.isArray(floor.points)) fail(`${path}.points`, 'cal una llista');
    floor.points.forEach((point, j) => {
      const pointPath = `${path}.points[${j}]`;
      object(point, pointPath);
      string(point.title, `${pointPath}.title`);
      if (point.description !== undefined && typeof point.description !== 'string') fail(`${pointPath}.description`, 'cal un text');
      for (const key of ['x', 'y']) number(point[key], `${pointPath}.${key}`, 0, 100);
      if (point.icon) icon(point.icon, `${pointPath}.icon`);
      if (point.polygon !== undefined) {
        if (!Array.isArray(point.polygon) || point.polygon.length < 3) fail(`${pointPath}.polygon`, 'calen almenys tres vèrtexs');
        point.polygon.forEach((pair) => { if (!Array.isArray(pair) || pair.length !== 2) fail(`${pointPath}.polygon`, 'calen parelles [x, y]'); pair.forEach((value) => number(value, `${pointPath}.polygon`, 0, 100)); });
      }
    });
  });
  unique(config.floors.map((floor) => floor.id), 'floors.id');
  unique(config.floors.map((floor) => floor.level), 'floors.level');
  unique(roomIds, 'rooms.id');
  config.view.defaultFloorId ??= config.floors[0].id;
  if (!config.floors.some((floor) => floor.id === config.view.defaultFloorId)) fail('view.defaultFloorId', 'planta desconeguda');
  if (config.here.defaultLocation != null) {
    const location = object(config.here.defaultLocation, 'here.defaultLocation');
    if (!config.floors.some((floor) => floor.id === location.floorId)) fail('here.defaultLocation.floorId', 'planta desconeguda');
    for (const key of ['x', 'y']) number(location[key], `here.defaultLocation.${key}`, 0, 100);
  }
  return config;
}

export async function loadConfig(url, fetcher = fetch) {
  const response = await fetcher(url, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`config.json: HTTP ${response.status}`);
  return validateConfig(await response.json());
}
