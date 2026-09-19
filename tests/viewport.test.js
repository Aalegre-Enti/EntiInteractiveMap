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
