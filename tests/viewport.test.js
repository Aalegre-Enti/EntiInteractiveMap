import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { floors } from '../src/floors.js';
import { fitScale, constrainOffset, zoomAround, MAX_ZOOM } from '../src/viewport.js';

test('les cinc imatges existeixen i les dimensions coincideixen amb els plànols', async () => {
  assert.equal(new Set(floors.map((floor) => floor.id)).size, 5);
  for (const floor of floors) {
    const data = await readFile(new URL(`../${floor.image}`, import.meta.url));
    assert.equal(data.readUInt32BE(16), floor.width);
    assert.equal(data.readUInt32BE(20), floor.height);
  }
});

test('els 14 espais de la planta baixa tenen capes transparents alineades amb el plànol', async () => {
  const floor = floors.find((item) => item.id === '0');
  assert.equal(floor.rooms.length, 14);
  assert.equal(new Set(floor.rooms.map((room) => room.overlay)).size, 14);
  for (const room of floor.rooms) {
    assert.ok(room.overlay, room.name);
    const data = await readFile(new URL(`../${room.overlay}`, import.meta.url));
    assert.equal(data.readUInt32BE(16), floor.width, room.name);
    assert.equal(data.readUInt32BE(20), floor.height, room.name);
    assert.equal(data[25], 6, `${room.name}: PNG amb canal alfa`);
  }
  const auditorium = floor.rooms.find((room) => room.code === 'AUDITORI');
  assert.equal(auditorium.kind, 'common');
  assert.equal(auditorium.showUsage, false);
  assert.deepEqual(auditorium.uses, []);
  assert.ok(floors.slice(1).every((otherFloor) => otherFloor.rooms.every((room) => !room.overlay)));
});

test('el plànol sencer cap en pantalles verticals i horitzontals', () => {
  for (const [width, height] of [[280, 300], [360, 640], [1000, 600]]) {
    for (const floor of floors) {
      const scale = fitScale(width, height, floor.width, floor.height);
      assert.ok(floor.width * scale <= width);
      assert.ok(floor.height * scale <= height);
    }
  }
});

test('el punt sota el cursor es conserva en ampliar i reduir', () => {
  const before = { zoom: 1, x: 30, y: 40 };
  const after = zoomAround(before, 2, 100, 120, 0.5);
  assert.equal((100 - before.x) / 0.5, (100 - after.x) / 1);
  assert.equal((120 - before.y) / 0.5, (120 - after.y) / 1);
  assert.deepEqual(zoomAround(after, 1, 100, 120, 0.5), before);
  assert.equal(zoomAround(before, 100, 0, 0, 0.5).zoom, MAX_ZOOM);
});

test('el desplaçament no pot fer desaparèixer el plànol', () => {
  assert.equal(constrainOffset(-9999, 400, 800), -424);
  assert.equal(constrainOffset(9999, 400, 800), 24);
  assert.equal(constrainOffset(9999, 400, 200), 100);
});
