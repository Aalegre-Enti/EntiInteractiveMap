import test from 'node:test';
import assert from 'node:assert/strict';
import { autoFlipDelayFromSearch, createAutoFlipTimer } from '../src/auto-flip.js';

test('la URL configura els segons per planta i conserva altres paràmetres', () => {
  assert.equal(autoFlipDelayFromSearch('?autoflip=10'), 10000);
  assert.equal(autoFlipDelayFromSearch('?aqui=1&x=50&y=60&autoflip=2.5'), 2500);
  assert.equal(autoFlipDelayFromSearch('?autoflip=1'), 1000);
  assert.equal(autoFlipDelayFromSearch('?autoflip=86400'), 86400000);
});

test('el mode manual es conserva amb paràmetres absents o invàlids', () => {
  for (const search of ['', '?aqui=1', '?autoflip', '?autoflip=', '?autoflip=0',
    '?autoflip=-2', '?autoflip=0.5', '?autoflip=86401', '?autoflip=Infinity',
    '?autoflip=1e3', '?autoflip=2s', '?autoflip=2,5', '?autoflip=0x10',
    '?autoflip=10&autoflip=20', '?autoflip=999999999999999999999999999999']) {
    assert.equal(autoFlipDelayFromSearch(search), null, search);
  }
});

function setup(t, ids = ['upper', 'basement', 'ground']) {
  let now = 0;
  let nextTimer = 0;
  const pending = new Map();
  const clock = {
    performance: { now: () => now },
    setTimeout(callback, delay) {
      const id = ++nextTimer;
      pending.set(id, { callback, due: now + delay });
      return id;
    },
    clearTimeout(id) { pending.delete(id); },
    tick(elapsed) {
      now += elapsed;
      for (const [id, task] of pending) {
        if (task.due > now) continue;
        pending.delete(id);
        task.callback();
      }
    },
  };
  let floorId = ids[0];
  const visited = [];
  const rotation = createAutoFlipTimer({
    clock,
    floors: ids.map((id) => ({ id })),
    getFloorId: () => floorId,
    onAdvance: (id) => { floorId = id; visited.push(id); },
  });
  t.after(rotation.stop);
  return { rotation, visited, clock, select: (id) => { floorId = id; } };
}

test('respecta tot l’interval, l’ordre configurat i el retorn a la primera planta', (t) => {
  const { rotation, visited, clock } = setup(t);
  for (let i = 0; i < 3; i++) {
    rotation.restart(2500);
    clock.tick(2499);
    assert.equal(visited.length, i);
    clock.tick(1);
    assert.equal(visited.length, i + 1);
  }
  assert.deepEqual(visited, ['basement', 'ground', 'upper']);
});

test('espera que la càrrega acabi abans de comptar el següent interval', (t) => {
  const { rotation, visited, clock } = setup(t);
  rotation.restart(1000);
  clock.tick(1000);
  clock.tick(60000); // The next image is still loading; no restart yet.
  assert.deepEqual(visited, ['basement']);
  rotation.restart(1000);
  clock.tick(999);
  assert.deepEqual(visited, ['basement']);
  clock.tick(1);
  assert.deepEqual(visited, ['basement', 'ground']);
});

test('la selecció manual reinicia el temps i continua des de la planta escollida', (t) => {
  const { rotation, visited, select, clock } = setup(t);
  rotation.restart(10000);
  clock.tick(9000);
  select('ground');
  rotation.restart(10000);
  clock.tick(9999);
  assert.deepEqual(visited, []);
  clock.tick(1);
  assert.deepEqual(visited, ['upper']);
});

test('pausar o desactivar cancel·la el canvi pendent; reprendre dona tot l’interval', (t) => {
  const { rotation, visited, clock } = setup(t);
  rotation.restart(1000);
  clock.tick(900);
  rotation.stop();
  clock.tick(60000);
  assert.deepEqual(visited, []);
  rotation.restart(1000);
  clock.tick(999);
  assert.deepEqual(visited, []);
  clock.tick(1);
  assert.deepEqual(visited, ['basement']);
  rotation.restart(1000);
  rotation.restart(null);
  clock.tick(60000);
  assert.deepEqual(visited, ['basement']);
});

test('una única planta no es recarrega automàticament', (t) => {
  const { rotation, visited, clock } = setup(t, ['only']);
  rotation.restart(1000);
  assert.equal(rotation.remaining(), 0);
  clock.tick(60000);
  assert.deepEqual(visited, []);
});

test('el compte enrere comparteix el termini del canvi i es reinicia després de pauses o càrregues', (t) => {
  const { rotation, visited, clock } = setup(t);
  assert.equal(rotation.remaining(), 0);
  rotation.restart(2500);
  assert.equal(rotation.remaining(), 2500);
  clock.tick(900);
  assert.equal(rotation.remaining(), 1600);
  rotation.stop();
  clock.tick(10000);
  assert.equal(rotation.remaining(), 0);
  assert.deepEqual(visited, []);
  rotation.restart(2500);
  assert.equal(rotation.remaining(), 2500);
  clock.tick(2500);
  assert.equal(rotation.remaining(), 0);
  assert.deepEqual(visited, ['basement']);
  clock.tick(10000); // Loading the next floor does not start a new countdown.
  assert.equal(rotation.remaining(), 0);
  rotation.restart(1000);
  assert.equal(rotation.remaining(), 1000);
});
