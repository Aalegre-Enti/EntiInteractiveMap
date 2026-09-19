import test from 'node:test';
import assert from 'node:assert/strict';
import { floors } from '../src/floors.js';
import { selectionHash, selectionFromHash } from '../src/selection-url.js';

test('els enllaços recuperen totes les sales a la planta correcta, també sense capa', () => {
  const hashes = new Set();
  for (const floor of floors) {
    for (const room of floor.rooms) {
      const hash = selectionHash(floor, room);
      hashes.add(hash);
      assert.deepEqual(selectionFromHash(hash), { floor, room });
      const url = new URL(`https://example.org/mapa/${hash}`);
      assert.equal(url.pathname, '/mapa/');
      assert.deepEqual(selectionFromHash(url.hash), { floor, room });
    }
  }
  assert.equal(hashes.size, 60);
});

test('es mantenen els enllaços de planta i l’entrada sense selecció', () => {
  for (const floor of floors) {
    assert.equal(selectionHash(floor), `#planta-${floor.id}`);
    assert.deepEqual(selectionFromHash(selectionHash(floor)), { floor, room: null });
  }
  assert.deepEqual(selectionFromHash(''), { floor: floors[0], room: null });
});

test('els espais i signes dels codis no trenquen l’enllaç', () => {
  const floor = floors[1];
  const room = floor.rooms.find((item) => item.code === 'SALA ESTUDI');
  assert.equal(selectionHash(floor, room), '#planta-1/sala/SALA%20ESTUDI');
  assert.equal(selectionFromHash('#planta-0/sala/PB.01').room.code, 'PB.01');
  assert.equal(selectionFromHash('#planta-0/sala/AUD-01').room.code, 'AUD-01');
});

test('un codi desconegut o malformat conserva la planta sense seleccionar una sala incorrecta', () => {
  for (const hash of ['#planta-2/sala/PB.01', '#planta-2/sala/inexistent', '#planta-2/sala/%E0%A4%A']) {
    assert.deepEqual(selectionFromHash(hash), { floor: floors[2], room: null });
  }
  assert.equal(selectionFromHash('#planta-9/sala/PB.01'), null);
  assert.equal(selectionFromHash('#map-viewport'), null);
});
