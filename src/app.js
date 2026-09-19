import { floors } from './floors.js';
import { MIN_ZOOM, MAX_ZOOM, fitScale, constrainOffset, zoomAround } from './viewport.js';

const $ = (id) => document.getElementById(id);
const viewport = $('map-viewport');
const transform = $('map-transform');
const floorImage = $('floor-image');
const panel = $('map-panel');
const navigation = $('floor-navigation');
const help = $('help-dialog');
const pointers = new Map();
let activeFloor = floors[0];
let view = { zoom: 1, x: 0, y: 0 };
let baseScale = 1;
let ready = false;
let loadVersion = 0;
let lastGesture = null;
let activeMarker = null;
let fallbackExpanded = false;
let resizeFrame = 0;

function icon(name) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.classList.add('icon');
  svg.setAttribute('aria-hidden', 'true');
  const use = document.createElementNS(svg.namespaceURI, 'use');
  use.setAttribute('href', `#icon-${name}`);
  svg.append(use);
  return svg;
}

function announce(message) { $('announcer').textContent = message; }

for (const floor of [...floors].reverse()) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'floor-button';
  button.dataset.floor = floor.id;
  button.setAttribute('aria-label', floor.name);
  button.setAttribute('aria-controls', 'map-panel');
  const number = document.createElement('span');
  number.className = 'floor-number';
  number.textContent = floor.code;
  number.setAttribute('aria-hidden', 'true');
  const label = document.createElement('span');
  const title = document.createElement('span');
  title.className = 'floor-button-title';
  title.textContent = floor.name;
  title.dataset.full = floor.name;
  title.dataset.short = floor.shortName;
  const subtitle = document.createElement('span');
  subtitle.className = 'floor-button-subtitle';
  subtitle.textContent = `Nivell ${floor.id}`;
  label.append(title, subtitle);
  const arrow = icon('arrow');
  arrow.classList.add('floor-chevron');
  button.append(number, label, arrow);
  button.addEventListener('click', () => selectFloor(floor.id));
  navigation.append(button);
}

const compact = matchMedia('(max-width: 760px)');
function updateFloorLabels() {
  for (const title of navigation.querySelectorAll('.floor-button-title')) {
    title.textContent = compact.matches ? title.dataset.short : title.dataset.full;
  }
  // Visual order and keyboard order both follow the building on desktop,
  // and run from the ground floor upward on small screens.
  navigation.style.flexDirection = compact.matches ? 'row' : 'column';
  const order = compact.matches ? floors : [...floors].reverse();
  for (const floor of order) navigation.append(navigation.querySelector(`[data-floor="${floor.id}"]`));
}
compact.addEventListener('change', updateFloorLabels);
updateFloorLabels();

function renderView() {
  if (!ready) return;
  const scale = baseScale * view.zoom;
  view.x = constrainOffset(view.x, viewport.clientWidth, activeFloor.width * scale);
  view.y = constrainOffset(view.y, viewport.clientHeight, activeFloor.height * scale);
  transform.style.transform = `translate(${view.x}px, ${view.y}px) scale(${scale})`;
  transform.style.setProperty('--marker-scale', 1 / scale);
  $('zoom-level').value = `${Math.round(view.zoom * 100)} %`;
  $('zoom-out').disabled = view.zoom <= MIN_ZOOM;
  $('zoom-in').disabled = view.zoom >= MAX_ZOOM;
}

function resetView() {
  if (!ready) return;
  baseScale = fitScale(viewport.clientWidth, viewport.clientHeight, activeFloor.width, activeFloor.height);
  view = {
    zoom: 1,
    x: (viewport.clientWidth - activeFloor.width * baseScale) / 2,
    y: (viewport.clientHeight - activeFloor.height * baseScale) / 2,
  };
  renderView();
}

function zoomTo(zoom, x = viewport.clientWidth / 2, y = viewport.clientHeight / 2) {
  if (!ready) return;
  view = zoomAround(view, zoom, x, y, baseScale);
  renderView();
}

function hideDetails(returnFocus = false) {
  $('point-details').hidden = true;
  $('area-overlay').replaceChildren();
  if (activeMarker) {
    activeMarker.setAttribute('aria-pressed', 'false');
    if (returnFocus && activeMarker.isConnected) activeMarker.focus({ preventScroll: true });
  }
  activeMarker = null;
}

function renderPoints() {
  $('marker-layer').replaceChildren();
  $('area-overlay').setAttribute('viewBox', `0 0 ${activeFloor.width} ${activeFloor.height}`);
  for (const point of activeFloor.points) {
    if (!Number.isFinite(point.x) || !Number.isFinite(point.y) || point.x < 0 || point.x > 100 || point.y < 0 || point.y > 100) continue;
    const button = document.createElement('button');
    button.className = 'map-marker';
    button.type = 'button';
    button.style.left = `${point.x}%`;
    button.style.top = `${point.y}%`;
    button.setAttribute('aria-label', `Informació: ${point.title}`);
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-controls', 'point-details');
    button.append(icon('pin'));
    button.addEventListener('click', () => {
      hideDetails();
      activeMarker = button;
      button.setAttribute('aria-pressed', 'true');
      $('point-title').textContent = point.title;
      $('point-description').textContent = point.description ?? '';
      $('point-details').hidden = false;
      if (point.polygon?.length >= 3) {
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.classList.add('area-highlight');
        polygon.setAttribute('points', point.polygon.map(([x, y]) => `${x * activeFloor.width / 100},${y * activeFloor.height / 100}`).join(' '));
        $('area-overlay').append(polygon);
      }
      $('close-details').focus({ preventScroll: true });
      announce(`${point.title}. ${point.description ?? ''}`);
    });
    $('marker-layer').append(button);
  }
}

function setLoadingState(state) {
  ready = state === 'ready';
  viewport.setAttribute('aria-busy', String(state === 'loading'));
  transform.hidden = !ready;
  $('map-message').hidden = ready;
  $('map-message').querySelector('.loading-spinner').hidden = state !== 'loading';
  $('retry-button').hidden = state !== 'error';
  $('map-message-text').textContent = state === 'error'
    ? 'No s’ha pogut carregar el plànol. Comprova la connexió i torna-ho a provar.'
    : 'S’està carregant el plànol…';
  for (const id of ['zoom-in', 'zoom-out', 'reset-view']) $(id).disabled = !ready;
}

async function selectFloor(id, { updateUrl = true, force = false } = {}) {
  const floor = floors.find((item) => item.id === String(id));
  if (!floor) return false;
  if (activeFloor.id === floor.id && ready && !force) return true;
  const version = ++loadVersion;
  activeFloor = floor;
  hideDetails();
  pointers.clear();
  lastGesture = null;
  viewport.classList.remove('is-dragging');
  $('floor-title').textContent = floor.name;
  $('map-floor-code').textContent = floor.code;
  $('map-floor-name').textContent = floor.name;
  viewport.setAttribute('aria-label', `Plànol interactiu: ${floor.name.toLocaleLowerCase('ca')}`);
  document.title = `${floor.name} · Mapa de l’edifici`;
  for (const button of navigation.querySelectorAll('button')) {
    button.setAttribute('aria-current', String(button.dataset.floor === floor.id));
  }
  if (updateUrl) {
    const url = new URL(location.href);
    url.hash = `planta-${floor.id}`;
    history.replaceState(null, '', url);
  }
  setLoadingState('loading');
  const preload = new Image();
  try {
    await new Promise((resolve, reject) => {
      preload.onload = resolve;
      preload.onerror = reject;
      preload.src = floor.image;
    });
    if (version !== loadVersion) return false;
    floorImage.src = floor.image;
    floorImage.alt = `Plànol: ${floor.name.toLocaleLowerCase('ca')}`;
    floorImage.width = floor.width;
    floorImage.height = floor.height;
    transform.style.width = `${floor.width}px`;
    transform.style.height = `${floor.height}px`;
    renderPoints();
    setLoadingState('ready');
    resetView();
    announce(`${floor.name}. Plànol carregat.`);
    return true;
  } catch {
    if (version !== loadVersion) return false;
    setLoadingState('error');
    announce(`No s’ha pogut carregar el plànol: ${floor.name.toLocaleLowerCase('ca')}.`);
    return false;
  }
}

$('zoom-in').addEventListener('click', () => zoomTo(view.zoom * 1.25));
$('zoom-out').addEventListener('click', () => zoomTo(view.zoom / 1.25));
$('reset-view').addEventListener('click', () => { resetView(); announce('Es mostra el plànol sencer.'); });
$('retry-button').addEventListener('click', () => selectFloor(activeFloor.id, { force: true }));
$('close-details').addEventListener('click', () => hideDetails(true));

viewport.addEventListener('wheel', (event) => {
  // Ctrl/Cmd + wheel remains the browser's own accessibility zoom.
  if (!ready || event.ctrlKey || event.metaKey) return;
  event.preventDefault();
  const rect = viewport.getBoundingClientRect();
  const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1);
  zoomTo(view.zoom * Math.exp(-delta * 0.002), event.clientX - rect.left, event.clientY - rect.top);
}, { passive: false });

function gesture() {
  const values = [...pointers.values()];
  if (!values.length) return null;
  if (values.length === 1) return { x: values[0].x, y: values[0].y, distance: 0 };
  return {
    x: (values[0].x + values[1].x) / 2,
    y: (values[0].y + values[1].y) / 2,
    distance: Math.hypot(values[0].x - values[1].x, values[0].y - values[1].y),
  };
}

viewport.addEventListener('pointerdown', (event) => {
  if (!ready || event.button !== 0 || event.target.closest('button')) return;
  viewport.focus({ preventScroll: true });
  viewport.setPointerCapture(event.pointerId);
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  lastGesture = gesture();
  viewport.classList.add('is-dragging');
});
viewport.addEventListener('pointermove', (event) => {
  if (!pointers.has(event.pointerId) || !ready) return;
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  const next = gesture();
  if (lastGesture?.distance > 0 && next.distance > 0) {
    const rect = viewport.getBoundingClientRect();
    view = zoomAround(view, view.zoom * next.distance / lastGesture.distance, lastGesture.x - rect.left, lastGesture.y - rect.top, baseScale);
  }
  if (lastGesture) {
    view.x += next.x - lastGesture.x;
    view.y += next.y - lastGesture.y;
  }
  lastGesture = next;
  renderView();
});
function endPointer(event) {
  pointers.delete(event.pointerId);
  lastGesture = gesture();
  if (!pointers.size) viewport.classList.remove('is-dragging');
}
for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) viewport.addEventListener(event, endPointer);

viewport.addEventListener('keydown', (event) => {
  if (event.target !== viewport || !ready || event.ctrlKey || event.metaKey || event.altKey) return;
  const move = event.shiftKey ? 100 : 50;
  switch (event.key) {
    case '+': case '=': zoomTo(view.zoom * 1.25); break;
    case '-': case '_': zoomTo(view.zoom / 1.25); break;
    case 'Home': case '0': resetView(); break;
    case 'ArrowLeft': view.x += move; renderView(); break;
    case 'ArrowRight': view.x -= move; renderView(); break;
    case 'ArrowUp': view.y += move; renderView(); break;
    case 'ArrowDown': view.y -= move; renderView(); break;
    default: return;
  }
  event.preventDefault();
});

const resizeObserver = new ResizeObserver(() => {
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(resetView);
});
resizeObserver.observe(viewport);

function expandedState() { return document.fullscreenElement === panel || fallbackExpanded; }
function updateExpandedButton() {
  const expanded = expandedState();
  $('fullscreen-button').setAttribute('aria-label', expanded ? 'Surt de la pantalla completa' : 'Amplia el mapa a pantalla completa');
  $('fullscreen-button').title = expanded ? 'Surt de la pantalla completa' : 'Pantalla completa';
  $('fullscreen-button').querySelector('use').setAttribute('href', expanded ? '#icon-close' : '#icon-expand');
  if (expanded && !panel.contains(document.activeElement)) $('fullscreen-button').focus({ preventScroll: true });
}
function setFallbackExpanded(expanded) {
  fallbackExpanded = expanded;
  panel.classList.toggle('is-expanded', expanded);
  document.body.classList.toggle('has-expanded-map', expanded);
  // Match native fullscreen focus containment on browsers without that API.
  for (const element of [document.querySelector('.skip-link'), document.querySelector('.site-header'), document.querySelector('.sidebar'), document.querySelector('.map-heading'), document.querySelector('.map-footer')]) element.inert = expanded;
  if (expanded) {
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.setAttribute('aria-label', `Plànol: ${activeFloor.name}`);
  } else {
    panel.removeAttribute('role');
    panel.removeAttribute('aria-modal');
    panel.removeAttribute('aria-label');
  }
  updateExpandedButton();
  $('fullscreen-button').focus({ preventScroll: true });
}
$('fullscreen-button').addEventListener('click', async () => {
  if (document.fullscreenElement === panel) {
    await document.exitFullscreen();
  } else if (fallbackExpanded) {
    setFallbackExpanded(false);
  } else if (panel.requestFullscreen && document.fullscreenEnabled) {
    try { await panel.requestFullscreen(); } catch { setFallbackExpanded(true); }
  } else {
    setFallbackExpanded(true);
  }
});
document.addEventListener('fullscreenchange', updateExpandedButton);
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  if (!$('point-details').hidden) hideDetails(true);
  if (fallbackExpanded) setFallbackExpanded(false);
});

function showHelp() { if (!help.open) help.showModal(); }
$('help-button').addEventListener('click', showHelp);
$('guide-button').addEventListener('click', showHelp);
help.addEventListener('click', (event) => {
  if (event.target !== help) return;
  const rect = help.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) help.close();
});

function floorFromHash() {
  const id = location.hash.match(/^#planta-([0-4])$/)?.[1];
  return id ?? '0';
}
window.addEventListener('hashchange', () => {
  if (/^#planta-[0-4]$/.test(location.hash) || !location.hash) selectFloor(floorFromHash(), { updateUrl: false });
});
selectFloor(floorFromHash(), { updateUrl: false });

// Optional browser integration; uses exactly the same action as the floor buttons.
if (document.modelContext?.registerTool) {
  const lifecycle = new AbortController();
  window.addEventListener('pagehide', (event) => { if (!event.persisted) lifecycle.abort(); }, { once: true });
  try {
    Promise.resolve(document.modelContext.registerTool({
      name: 'select_building_floor',
      title: 'Selecciona una planta',
      description: 'Mostra el plànol de la planta indicada (0: planta baixa; 1–4: plantes superiors).',
      inputSchema: { type: 'object', properties: { floor: { type: 'integer', minimum: 0, maximum: 4 } }, required: ['floor'], additionalProperties: false },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      async execute(input) {
        if (!Number.isInteger(input?.floor) || input.floor < 0 || input.floor > 4) throw new Error('La planta ha de ser un nombre enter entre 0 i 4.');
        const loaded = await selectFloor(String(input.floor));
        if (!loaded) throw new Error('No s’ha pogut mostrar el plànol.');
        return { floor: Number(activeFloor.id), name: activeFloor.name, loaded: true };
      },
    }, { signal: lifecycle.signal })).catch(() => {});
  } catch { /* The visible controls remain available in unsupported browsers. */ }
}
