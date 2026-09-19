import test from 'node:test';
import assert from 'node:assert/strict';
import { rooms, roomImport } from '../src/rooms.js';
import { floors } from '../src/floors.js';

test('es conserven tots els espais identificats del full a la planta correcta', () => {
  assert.equal(rooms.length, 39);
  assert.equal(new Set(rooms.map((room) => room.id)).size, 39);
  assert.deepEqual(floors.map((floor) => floor.rooms.filter((room) => room.kind === 'room').length), [7, 10, 10, 7, 5]);
  for (const floor of floors) assert.ok(floor.rooms.every((room) => room.floorId === floor.id));
  assert.deepEqual(roomImport.skippedRows.map((row) => row.row), [41]);
});

test('cada planta inclou exactament una entrada de lavabos sense atribucions inventades', () => {
  for (const floor of floors) {
    const bathrooms = floor.rooms.filter((room) => room.kind === 'bathroom');
    assert.equal(bathrooms.length, 1);
    assert.equal(bathrooms[0].name, 'Lavabos');
    assert.deepEqual(bathrooms[0].uses, []);
  }
  assert.equal(floors.flatMap((floor) => floor.rooms).length, 44);
});

test('els espais compartits mantenen els centres, períodes i usos del full', () => {
  assert.deepEqual(rooms.find((room) => room.code === 'LAB.REHAB').uses, [
    { institution: 'EUSES', period: 'weekdays', activity: 'Grau de fisioteràpia' },
    { institution: 'ISEP', period: 'weekends', activity: 'Curs ISEP 2' },
    { institution: 'FISIOFOCUS', period: 'weekends', activity: 'Fisioteràpia' },
  ]);
  assert.equal(rooms.find((room) => room.code === 'OFICINES').uses.length, 4);
  assert.equal(rooms.find((room) => room.code === 'PB.02').uses[0].activity, 'Nou grau / Cicle de salut 1 / Màster de música i ciberseguretat');
});
