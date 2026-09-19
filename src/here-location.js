import { formatText } from './config.js';

// URL: ?aqui=1&x=50&y=50. Coordinates are percentages of the complete plan.
export function hereFromSearch(search, floors, defaultLocation = null) {
  const params = new URLSearchParams(search);
  if (!['aqui', 'x', 'y'].some((key) => params.has(key))) return defaultLocation;
  if (['aqui', 'x', 'y'].some((key) => params.getAll(key).length !== 1)) return null;
  const floorId = params.get('aqui');
  if (!floors.some((floor) => floor.id === floorId)) return null;
  const values = ['x', 'y'].map((key) => params.get(key).trim());
  if (values.some((value) => !/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(value))) return null;
  const [x, y] = values.map(Number);
  if ([x, y].some((value) => !Number.isFinite(value) || value < 0 || value > 100)) return null;
  return { floorId, x, y };
}

export function hereFloorStatus(here, viewedFloorId, floors, texts, label = 'Ets aquí', language = 'ca') {
  const ownFloor = floors.find((floor) => floor.id === here.floorId);
  const viewedFloor = floors.find((floor) => floor.id === viewedFloorId);
  const difference = ownFloor.level - viewedFloor.level;
  const levels = Math.abs(difference);
  const direction = difference === 0 ? 'same' : difference > 0 ? 'up' : 'down';
  const distance = difference === 0 ? '' : formatText(texts, `${direction}${levels === 1 ? 'One' : 'Many'}`, { count: levels });
  return {
    direction,
    distance,
    description: formatText(texts, 'hereDescription', { label, floor: ownFloor.name.toLocaleLowerCase(language) }) + (distance ? ` ${formatText(texts, 'hereRelative', { distance })}` : ''),
  };
}
