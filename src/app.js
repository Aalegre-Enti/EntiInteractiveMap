import { formatText } from './config.js';
import { configurePage } from './configure-page.js';
import { createRoomSubmenu } from './room-menu.js';
import { createRoomMarkers, updateRoomMarkers } from './room-markers.js';
import { selectionHash, selectionFromHash } from './selection-url.js';
import { hereFromSearch, hereFloorStatus } from './here-location.js';
import { autoFlipDelayFromSearch, createAutoFlipTimer } from './auto-flip.js';
import { renderDisplayDirectory } from './display-mode.js';
import { MIN_ZOOM, fitScale, constrainOffset, zoomAround } from './viewport.js';

const $ = (id) => document.getElementById(id);
export function startApp(config) {
  configurePage(config);
  const { floors } = config;
  const t = (key, values) => formatText(config.texts, key, values);
  const numberFormatter = new Intl.NumberFormat(config.site.language);
  const getHereStatus = (location, floorId) => hereFloorStatus(location, floorId, floors, config.texts, config.here.label, config.site.language);
  const viewport = $('map-viewport');
  const transform = $('map-transform');
  const floorImage = $('floor-image');
  const roomOverlay = $('room-overlay');
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
  let currentFloorLoad = Promise.resolve();
  let roomSelectionVersion = 0;
  let selectedRoom = null;
  let urlRestoreVersion = 0;
  let lastHandledUrl;
  let hereLocation = null;
  let displayMode = false;
  let autoFlipDelay = null;
  let autoFlipPaused = false;
  let floorLoading = true;
  let autoFlipProgressFrame = 0;
  const autoFlip = createAutoFlipTimer({
    floors,
    getFloorId: () => activeFloor.id,
    onAdvance: (id) => selectFloor(id, { replaceUrl: true }),
  });

  function scheduleAutoFlip() {
    autoFlip.restart(!autoFlipPaused && !floorLoading && !document.hidden && !help.open ? autoFlipDelay : null);
    renderAutoFlipProgress();
  }

  function renderAutoFlipProgress() {
    cancelAnimationFrame(autoFlipProgressFrame);
    const progress = $('auto-flip-progress');
    progress.hidden = autoFlipDelay === null || floors.length < 2;
    if (progress.hidden) return;
    const remaining = autoFlip.remaining();
    progress.value = floorLoading ? 1 : remaining / autoFlipDelay;
    const label = floorLoading ? t('loading') : t('autoFlipTimeLeft', {
      seconds: numberFormatter.format(Math.ceil(remaining / 1000)),
    });
    if (progress.getAttribute('aria-valuetext') !== label) progress.setAttribute('aria-valuetext', label);
    if (remaining > 0) autoFlipProgressFrame = requestAnimationFrame(renderAutoFlipProgress);
  }

  function renderAutoFlipControl() {
    const button = $('auto-flip-button');
    const enabled = autoFlipDelay !== null && floors.length > 1;
    button.hidden = !enabled;
    panel.classList.toggle('has-auto-flip', enabled);
    const label = t(autoFlipPaused ? 'resumeAutoFlip' : 'pauseAutoFlip', {
      seconds: numberFormatter.format(autoFlipDelay / 1000),
    });
    button.setAttribute('aria-label', label);
    button.title = label;
    button.querySelector('use').setAttribute('href', autoFlipPaused ? '#icon-play' : '#icon-pause');
  }

  $('auto-flip-button').addEventListener('click', () => {
    autoFlipPaused = !autoFlipPaused;
    renderAutoFlipControl();
    scheduleAutoFlip();
  });
  document.addEventListener('visibilitychange', scheduleAutoFlip);
  window.addEventListener('pagehide', () => { autoFlip.stop(); renderAutoFlipProgress(); });
  window.addEventListener('pageshow', scheduleAutoFlip);

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

  function renderHereLocation() {
    const marker = $('here-marker');
    marker.hidden = !hereLocation;
    $('here-help').hidden = !hereLocation;
    if (!hereLocation) return;
    const status = getHereStatus(hereLocation, activeFloor.id);
    marker.style.left = `${hereLocation.x}%`;
    marker.style.top = `${hereLocation.y}%`;
    marker.dataset.direction = status.direction;
    marker.classList.toggle('label-right', hereLocation.x < 25);
    marker.classList.toggle('label-left', hereLocation.x > 75);
    marker.classList.toggle('label-below', hereLocation.y < 20);
    marker.setAttribute('aria-label', status.description);
    $('here-level').textContent = status.distance;
    $('here-level').hidden = !status.distance;
  }

  for (const floor of floors) {
    const group = document.createElement('div');
    group.className = 'floor-group';
    group.dataset.floorGroup = floor.id;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'floor-button';
    button.dataset.floor = floor.id;
    button.setAttribute('aria-label', floor.name);
    button.setAttribute('aria-controls', `map-panel floor-rooms-${floor.id}`);
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
    subtitle.textContent = t(floor.rooms.length === 1 ? 'roomCountOne' : 'roomCountMany', {count:floor.rooms.length});
    label.append(title, subtitle);
    const arrow = icon('arrow');
    arrow.classList.add('floor-chevron');
    button.append(number, label, arrow);
    const submenu = createRoomSubmenu(floor, { onSelect: selectRoom, periods: config.periods, t, language: config.site.language });
    submenu.hidden = true;
    button.addEventListener('click', () => {
      if (activeFloor.id === floor.id) {
        submenu.open = !submenu.open;
        scheduleAutoFlip();
      } else {
        selectFloor(floor.id);
      }
    });
    submenu.addEventListener('toggle', () => button.setAttribute('aria-expanded', String(!submenu.hidden && submenu.open)));
    group.append(button, submenu);
    navigation.append(group);
  }

  const compact = matchMedia('(max-width: 760px)');
  function updateFloorLabels() {
    for (const title of navigation.querySelectorAll('.floor-button-title')) {
      title.textContent = compact.matches ? title.dataset.short : title.dataset.full;
    }
    // Keep the configured order on desktop and mobile.
    navigation.style.flexDirection = compact.matches ? 'row' : 'column';
    for (const floor of floors) {
      const group = navigation.querySelector(`[data-floor-group="${floor.id}"]`);
      const submenu = $(`floor-rooms-${floor.id}`);
      navigation.append(group);
      (compact.matches ? $('mobile-room-submenus') : group).append(submenu);
    }
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
    $('zoom-in').disabled = view.zoom >= config.view.maxZoom;
  }

  function resetView() {
    if (!ready) return;
    baseScale = fitScale(viewport.clientWidth, viewport.clientHeight, activeFloor.width, activeFloor.height, config.view.fitScale);
    view = {
      zoom: 1,
      x: (viewport.clientWidth - activeFloor.width * baseScale) / 2,
      y: (viewport.clientHeight - activeFloor.height * baseScale) / 2,
    };
    renderView();
  }

  function zoomTo(zoom, x = viewport.clientWidth / 2, y = viewport.clientHeight / 2) {
    if (!ready) return;
    view = zoomAround(view, zoom, x, y, baseScale, config.view.maxZoom);
    renderView();
  }

  function updateSelectionUrl(floor, room = null, { replace = false } = {}) {
    // An interaction supersedes any link that is still waiting for its floor image.
    urlRestoreVersion++;
    const url = new URL(location.href);
    url.hash = selectionHash(floor, room);
    lastHandledUrl = url.href;
    if (location.href === url.href) return;
    if (replace) history.replaceState(null, '', url);
    else history.pushState(null, '', url);
  }

  function clearRoomSelection({ updateUrl = false, closeInformation = true } = {}) {
    roomSelectionVersion++;
    selectedRoom = null;
    updateRoomMarkers($('marker-layer'), null);
    roomOverlay.hidden = true;
    roomOverlay.classList.remove('is-pulsing');
    roomOverlay.style.removeProperty('--room-mask');
    delete roomOverlay.dataset.roomId;
    $('map-floor-name').textContent = activeFloor.name;
    document.title = t('titleFloor', {floor:activeFloor.name, site:config.site.name});
    $('overlay-notice').hidden = true;
    for (const item of document.querySelectorAll('.room-list-item.is-selected')) item.classList.remove('is-selected');
    for (const control of document.querySelectorAll('[data-room-select]')) {
      control.removeAttribute('aria-current');
      if (control.tagName === 'BUTTON') control.setAttribute('aria-pressed', 'false');
    }
    if (closeInformation) {
      for (const details of document.querySelectorAll('.room-entry[open]')) details.open = false;
    }
    if (updateUrl) updateSelectionUrl(activeFloor);
  }

  async function selectRoom(floor, room, { updateUrl = true, reveal = false, fromMap = false } = {}) {
    if (activeFloor.id !== floor.id) return;
    scheduleAutoFlip();
    clearRoomSelection({ closeInformation: false });
    hideDetails();
    const version = roomSelectionVersion;
    selectedRoom = room;
    updateRoomMarkers($('marker-layer'), room.id);
    const control = [...document.querySelectorAll('[data-room-select]')].find((element) => element.dataset.roomSelect === room.id);
    for (const details of document.querySelectorAll('.room-entry[open]')) {
      if (!details.contains(control)) details.open = false;
    }
    control?.closest('.room-list-item').classList.add('is-selected');
    control?.setAttribute('aria-current', 'true');
    if (control?.tagName === 'BUTTON') control.setAttribute('aria-pressed', 'true');
    if (reveal) {
      $(`floor-rooms-${floor.id}`).open = true;
      const details = control?.closest('.room-entry');
      if (details) details.open = true;
      if (fromMap) {
        // Reveal the selected entry without scrolling the page or moving focus off the map.
        const list = control?.closest('.room-list');
        if (list) list.scrollTop += control.getBoundingClientRect().top - list.getBoundingClientRect().top - 8;
      } else control?.scrollIntoView({ block: 'nearest', behavior: 'instant' });
    }
    $('map-floor-name').textContent = room.name;
    document.title = t('titleRoom', {room:room.name, floor:floor.name, site:config.site.name});
    if (updateUrl) updateSelectionUrl(floor, room);
    announce(t('selectedRoom', {room:room.name, floor:floor.name}));
    if (!room.overlay) return;
    const isCurrent = () => version === roomSelectionVersion && activeFloor.id === floor.id;
    try {
      await currentFloorLoad;
      if (!isCurrent()) return;
      if (!ready) throw new Error(t('unavailableFloor'));
      const url = new URL(room.overlay, document.baseURI).href;
      const mask = new Image();
      await new Promise((resolve, reject) => {
        mask.onload = resolve;
        mask.onerror = reject;
        mask.src = url;
      });
      if (!isCurrent()) return;
      if (mask.naturalWidth !== floor.width || mask.naturalHeight !== floor.height) throw new Error(t('badOverlay'));
      if (!fromMap) resetView();
      roomOverlay.style.setProperty('--room-mask', `url("${url}")`);
      roomOverlay.dataset.roomId = room.id;
      roomOverlay.hidden = false;
      // Restart even when the same cached room is selected twice in one frame.
      void roomOverlay.offsetWidth;
      roomOverlay.classList.add('is-pulsing');
      $('map-floor-name').textContent = room.name;
      announce(t('highlightRoom', {room:room.name}));
      if (compact.matches && !fromMap) panel.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    } catch {
      if (!isCurrent()) return;
      $('overlay-notice').textContent = t('overlayError', {room:room.name});
      $('overlay-notice').hidden = false;
    }
  }

  roomOverlay.addEventListener('animationend', (event) => {
    if (event.animationName === 'room-highlight-pulse') roomOverlay.classList.remove('is-pulsing');
  });

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
    if (config.roomMarkers.enabled) {
      $('marker-layer').append(createRoomMarkers(activeFloor, {
        t,
        display: displayMode,
        onSelect: (floor, room) => selectRoom(floor, room, { reveal: true, fromMap: true }),
      }));
      updateRoomMarkers($('marker-layer'), selectedRoom?.id);
    }
    $('area-overlay').setAttribute('viewBox', `0 0 ${activeFloor.width} ${activeFloor.height}`);
    for (const point of activeFloor.points) {
      if (!Number.isFinite(point.x) || !Number.isFinite(point.y) || point.x < 0 || point.x > 100 || point.y < 0 || point.y > 100) continue;
      const button = document.createElement('button');
      button.className = 'map-marker';
      button.type = 'button';
      button.style.left = `${point.x}%`;
      button.style.top = `${point.y}%`;
      button.setAttribute('aria-label', t('pointInfo', {title:point.title}));
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-controls', 'point-details');
      button.append(icon(point.icon ?? 'pin'));
      button.addEventListener('click', () => {
        clearRoomSelection({ updateUrl: true });
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
    floorLoading = state === 'loading';
    scheduleAutoFlip();
    viewport.setAttribute('aria-busy', String(state === 'loading'));
    transform.hidden = !ready;
    $('map-message').hidden = ready;
    $('map-message').querySelector('.loading-spinner').hidden = state !== 'loading';
    $('retry-button').hidden = state !== 'error';
    $('map-message-text').textContent = state === 'error'
      ? t('loadError')
      : t('loading');
    for (const id of ['zoom-in', 'zoom-out', 'reset-view']) $(id).disabled = !ready;
  }

  async function selectFloor(id, { updateUrl = true, force = false, replaceUrl = false } = {}) {
    const floor = floors.find((item) => item.id === String(id));
    if (!floor) return false;
    if (activeFloor.id === floor.id && ready && !force) {
      clearRoomSelection({ updateUrl });
      hideDetails();
      renderHereLocation();
      scheduleAutoFlip();
      return true;
    }
    const version = ++loadVersion;
    activeFloor = floor;
    if (displayMode) renderDisplayDirectory(floor, floors, t);
    renderHereLocation();
    clearRoomSelection();
    hideDetails();
    pointers.clear();
    lastGesture = null;
    viewport.classList.remove('is-dragging');
    $('floor-title').textContent = floor.name;
    $('map-floor-code').textContent = floor.code;
    $('map-floor-name').textContent = floor.name;
    viewport.setAttribute('aria-label', t(displayMode ? 'plan' : 'interactivePlan', {floor:floor.name.toLocaleLowerCase(config.site.language)}));
    document.title = t('titleFloor', {floor:floor.name, site:config.site.name});
    for (const button of navigation.querySelectorAll('.floor-button')) {
      button.setAttribute('aria-current', String(button.dataset.floor === floor.id));
      const selected = button.dataset.floor === floor.id;
      const submenu = $(`floor-rooms-${button.dataset.floor}`);
      submenu.hidden = !selected;
      submenu.open = selected && (!compact.matches || !config.view.mobileMenuCollapsed);
      button.setAttribute('aria-expanded', String(submenu.open));
    }
    // Only scroll when the selected floor button is outside the sidebar view.
    if (!displayMode && !compact.matches) requestAnimationFrame(() => {
      const sidebar = document.querySelector('.sidebar');
      const buttonRect = navigation.querySelector(`[data-floor="${floor.id}"]`).getBoundingClientRect();
      const sidebarRect = sidebar.getBoundingClientRect();
      if (buttonRect.top < sidebarRect.top) sidebar.scrollTop += buttonRect.top - sidebarRect.top - 12;
      else if (buttonRect.bottom > sidebarRect.bottom) sidebar.scrollTop += buttonRect.bottom - sidebarRect.bottom + 12;
    });
    else if (!displayMode) requestAnimationFrame(() => navigation.querySelector(`[data-floor="${floor.id}"]`).scrollIntoView({ block:'nearest', inline:'nearest' }));
    if (updateUrl) updateSelectionUrl(floor, null, { replace: replaceUrl });
    setLoadingState('loading');
    const preload = new Image();
    try {
      currentFloorLoad = new Promise((resolve, reject) => {
        preload.onload = resolve;
        preload.onerror = reject;
        preload.src = floor.image;
      });
      await currentFloorLoad;
      if (version !== loadVersion) return false;
      floorImage.src = floor.image;
      floorImage.alt = t('plan', {floor:floor.name.toLocaleLowerCase(config.site.language)});
      floorImage.width = floor.width;
      floorImage.height = floor.height;
      transform.style.width = `${floor.width}px`;
      transform.style.height = `${floor.height}px`;
      renderPoints();
      setLoadingState('ready');
      resetView();
      announce(`${t('loadedFloor', {floor:floor.name})}${hereLocation ? ` ${getHereStatus(hereLocation, floor.id).description}` : ''}`);
      return true;
    } catch {
      if (version !== loadVersion) return false;
      setLoadingState('error');
      announce(t('loadFloorError', {floor:floor.name.toLocaleLowerCase(config.site.language)}));
      return false;
    }
  }

  $('zoom-in').addEventListener('click', () => zoomTo(view.zoom * config.view.zoomStep));
  $('zoom-out').addEventListener('click', () => zoomTo(view.zoom / config.view.zoomStep));
  $('reset-view').addEventListener('click', () => { resetView(); announce(t('wholeFloor')); });
  $('retry-button').addEventListener('click', () => restoreSelectionFromUrl({ force: true }));
  $('close-details').addEventListener('click', () => hideDetails(true));
  document.querySelector('.skip-link').addEventListener('click', (event) => {
    event.preventDefault();
    viewport.focus({ preventScroll: true });
    viewport.scrollIntoView({ block: 'nearest' });
  });

  viewport.addEventListener('wheel', (event) => {
    // Ctrl/Cmd + wheel remains the browser's own accessibility zoom.
    if (displayMode || !ready || event.ctrlKey || event.metaKey) return;
    event.preventDefault();
    const rect = viewport.getBoundingClientRect();
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1);
    zoomTo(view.zoom * Math.exp(-delta * config.view.wheelSensitivity), event.clientX - rect.left, event.clientY - rect.top);
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
    if (displayMode || !ready || event.button !== 0 || event.target.closest('button')) return;
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
      view = zoomAround(view, view.zoom * next.distance / lastGesture.distance, lastGesture.x - rect.left, lastGesture.y - rect.top, baseScale, config.view.maxZoom);
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
    if (displayMode || event.target !== viewport || !ready || event.ctrlKey || event.metaKey || event.altKey) return;
    const move = event.shiftKey ? config.view.fastPanStep : config.view.panStep;
    switch (event.key) {
      case '+': case '=': zoomTo(view.zoom * config.view.zoomStep); break;
      case '-': case '_': zoomTo(view.zoom / config.view.zoomStep); break;
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
    $('fullscreen-button').setAttribute('aria-label', t(expanded ? 'exitFullscreen' : 'fullscreen'));
    $('fullscreen-button').title = t(expanded ? 'exitFullscreen' : 'titleFullscreen');
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
      panel.setAttribute('aria-label', t('plan', {floor:activeFloor.name}));
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
    if (selectedRoom) clearRoomSelection({ updateUrl: true });
    if (!$('point-details').hidden) hideDetails(true);
    if (fallbackExpanded) setFallbackExpanded(false);
  });

  function showHelp() {
    if (!help.open) help.showModal();
    scheduleAutoFlip();
  }
  help.addEventListener('close', scheduleAutoFlip);
  $('help-button').addEventListener('click', showHelp);
  $('guide-button').addEventListener('click', showHelp);
  help.addEventListener('click', (event) => {
    if (event.target !== help) return;
    const rect = help.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) help.close();
  });

  async function restoreSelectionFromUrl({ initial = false, force = false } = {}) {
    const url = new URL(location.href);
    // Back/forward can emit both popstate and hashchange for the same URL.
    if (!force && url.href === lastHandledUrl) return;
    lastHandledUrl = url.href;
    const version = ++urlRestoreVersion;
    const delay = autoFlipDelayFromSearch(url.search);
    const modeChanged = displayMode !== (delay !== null);
    displayMode = delay !== null;
    document.body.classList.toggle('is-display', displayMode);
    $('display-sidebar').hidden = !displayMode;
    $('display-caption').hidden = !displayMode;
    if (displayMode && help.open) help.close();
    viewport.tabIndex = displayMode ? -1 : 0;
    if (displayMode) viewport.removeAttribute('aria-describedby');
    else viewport.setAttribute('aria-describedby', 'map-keyboard-help');
    if (delay !== autoFlipDelay) autoFlipPaused = false;
    autoFlipDelay = delay;
    renderAutoFlipControl();
    scheduleAutoFlip();
    hereLocation = hereFromSearch(url.search, floors, config.here.defaultLocation);
    renderHereLocation();
    const homeUrl = new URL('./', document.baseURI);
    homeUrl.search = url.search;
    if (displayMode) document.querySelector('.brand').removeAttribute('href');
    else document.querySelector('.brand').href = homeUrl.href;
    // A location-only link starts on its own floor; an explicit floor/room wins.
    const defaultSelection = { floor: floors.find((floor) => floor.id === (hereLocation?.floorId ?? config.view.defaultFloorId)), room: null };
    const selection = (!url.hash || url.hash === '#') ? defaultSelection : selectionFromHash(url.hash, floors) ?? (initial ? defaultSelection : null);
    if (!selection) return; // Preserve regular anchors, such as the skip-to-map link.
    const { floor, room } = selection;
    const loaded = await selectFloor(floor.id, { updateUrl: false, force: force || modeChanged });
    if (!loaded || version !== urlRestoreVersion) return;
    if (room) await selectRoom(floor, room, { updateUrl: false, reveal: !displayMode });
  }
  window.addEventListener('hashchange', () => restoreSelectionFromUrl());
  window.addEventListener('popstate', () => restoreSelectionFromUrl());
  restoreSelectionFromUrl({ initial: true });

  // Optional browser integration; uses exactly the same action as the floor buttons.
  if (document.modelContext?.registerTool) {
    const lifecycle = new AbortController();
    window.addEventListener('pagehide', (event) => { if (!event.persisted) lifecycle.abort(); }, { once: true });
    try {
      Promise.resolve(document.modelContext.registerTool({
        name: 'select_building_floor',
        title: t('integrationTitle'),
        description: t('integrationDescription'),
        inputSchema: { type: 'object', properties: { floor: { type: 'string', enum: floors.map((floor) => floor.id) } }, required: ['floor'], additionalProperties: false },
        annotations: { readOnlyHint: false, untrustedContentHint: false },
        async execute(input) {
          if (!floors.some((floor) => floor.id === input?.floor)) throw new Error(t('integrationInvalidFloor'));
          const loaded = await selectFloor(String(input.floor));
          if (!loaded) throw new Error(t('unavailableFloor'));
          return { floor: activeFloor.id, name: activeFloor.name, loaded: true };
        },
      }, { signal: lifecycle.signal })).catch(() => {});
    } catch { /* The visible controls remain available in unsupported browsers. */ }
  }
}
