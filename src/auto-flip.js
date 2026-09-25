// URL: ?autoflip=10 shows each floor for ten seconds. No parameter means manual mode.
export function autoFlipDelayFromSearch(search) {
  const values = new URLSearchParams(search).getAll('autoflip');
  if (values.length !== 1) return null;
  const value = values[0].trim();
  if (!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(value)) return null;
  const seconds = Number(value);
  // Bound the delay to avoid accidental rapid flipping and browser timer overflow.
  return Number.isFinite(seconds) && seconds >= 1 && seconds <= 86400 ? seconds * 1000 : null;
}

export function createAutoFlipTimer({ floors, getFloorId, onAdvance, clock = globalThis }) {
  let timer = null;
  let deadline = null;
  const now = () => clock.performance?.now() ?? Date.now();

  function remaining() {
    return deadline === null ? 0 : Math.max(0, deadline - now());
  }

  function stop() {
    clock.clearTimeout(timer);
    timer = null;
    deadline = null;
  }

  function restart(delay) {
    stop();
    if (!delay || floors.length < 2) return;
    deadline = now() + delay;
    timer = clock.setTimeout(() => {
      timer = null;
      deadline = null;
      const index = floors.findIndex((floor) => floor.id === getFloorId());
      onAdvance(floors[(index + 1) % floors.length].id);
    }, delay);
  }

  // The app restarts the timer after the next floor finishes loading.
  return { restart, stop, remaining };
}
