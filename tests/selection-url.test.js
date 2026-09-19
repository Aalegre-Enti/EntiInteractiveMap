import test from 'node:test';
import assert from 'node:assert/strict';
import { floors } from './config-fixture.js';
import { selectionHash, selectionFromHash } from '../src/selection-url.js';

const fromHash = hash => selectionFromHash(hash, floors);

test('els enllaços recuperen totes les sales configurades a la planta correcta', () => {
  const hashes = new Set();
  for (const floor of floors) {
    for (const room of floor.rooms) {
      const hash = selectionHash(floor, room);
      hashes.add(hash);
      assert.deepEqual(fromHash(hash), { floor, room });
      const url = new URL(`https://example.org/mapa/${hash}`);
      assert.equal(url.pathname, '/mapa/');
      assert.deepEqual(fromHash(url.hash), { floor, room });
    }
  }
  assert.equal(hashes.size, floors.flatMap(floor=>floor.rooms).length);
});

test('es mantenen els enllaços de planta i l’entrada sense selecció', () => {
  for (const floor of floors) {
    assert.equal(selectionHash(floor), `#planta-${floor.id}`);
    assert.deepEqual(fromHash(selectionHash(floor)), { floor, room: null });
  }
  assert.deepEqual(fromHash(''), { floor: floors[0], room: null });
});

test('admet soterranis i plantes noves amb codis de sala amb espais i signes', () => {
  const custom = [{id:'soterrani',rooms:[{code:'Sala à / #1'}]}, {id:'12',rooms:[]}];
  const room = custom[0].rooms[0];
  const hash = selectionHash(custom[0],room);
  assert.equal(hash,'#planta-soterrani/sala/Sala%20%C3%A0%20%2F%20%231');
  assert.deepEqual(selectionFromHash(hash,custom),{floor:custom[0],room});
  assert.deepEqual(selectionFromHash('#planta-12',custom),{floor:custom[1],room:null});
  for(const hash of ['#planta-soterrani/sala/inexistent','#planta-soterrani/sala/%E0%A4%A'])
    assert.deepEqual(selectionFromHash(hash,custom),{floor:custom[0],room:null});
  assert.equal(selectionFromHash('#planta-0',custom),null);
  assert.equal(selectionFromHash('#map-viewport',custom),null);
});
