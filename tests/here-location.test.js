import test from 'node:test';
import assert from 'node:assert/strict';
import { hereFromSearch as parseHere, hereFloorStatus as floorStatus } from '../src/here-location.js';

const floors = Array.from({length:5}, (_,i)=>({id:String(i),level:i,name:i===0?'Planta baixa':`Planta ${i}`}));
const texts = {upOne:'1 planta més amunt',upMany:'{count} plantes més amunt',downOne:'1 planta més avall',downMany:'{count} plantes més avall',hereDescription:'{label}: {floor}.',hereRelative:'La teva ubicació és {distance}.'};
const hereFromSearch = search => parseHere(search, floors);
const hereFloorStatus = (here, viewed) => floorStatus(here, viewed, floors, texts);

test('la ubicació admet la planta baixa, decimals i els extrems del plànol', () => {
  assert.deepEqual(hereFromSearch('?aqui=0&x=0&y=100'), { floorId: '0', x: 0, y: 100 });
  assert.deepEqual(hereFromSearch('?aqui=4&x=52.5&y=60.25'), { floorId: '4', x: 52.5, y: 60.25 });
  assert.deepEqual(hereFromSearch('?aqui=1&x=.5&y=0&extra=valor'), { floorId: '1', x: .5, y: 0 });
});

test('les ubicacions incompletes, ambigües o fora del plànol no generen cap punt', () => {
  for (const search of [
    '', '?x=50&y=50', '?aqui=1&x=50', '?aqui=1&x=&y=50',
    '?aqui=1&x=%20&y=50', '?aqui=5&x=50&y=50', '?aqui=1.5&x=50&y=50',
    '?aqui=1&x=-1&y=50', '?aqui=1&x=50&y=100.01', '?aqui=1&x=NaN&y=50',
    '?aqui=1&x=Infinity&y=50', '?aqui=1&x=0x10&y=50', '?aqui=1&x=50abc&y=50',
    '?aqui=1&x=50&y=50&x=75', '?aqui=1&aqui=2&x=50&y=50',
  ]) assert.equal(hereFromSearch(search), null, search);
});

test('les fletxes apunten cap a la ubicació real des de qualsevol planta', () => {
  for (let source = 0; source <= 4; source++) {
    const here = { floorId: String(source), x: 50, y: 50 };
    for (let viewed = 0; viewed <= 4; viewed++) {
      const status = hereFloorStatus(here, String(viewed));
      assert.equal(status.direction, source === viewed ? 'same' : source > viewed ? 'up' : 'down');
      if (source === viewed) assert.equal(status.distance, '');
      else assert.ok(status.distance.startsWith(String(Math.abs(source - viewed))));
    }
  }
  assert.equal(hereFloorStatus({ floorId: '1' }, '0').distance, '1 planta més amunt');
  assert.equal(hereFloorStatus({ floorId: '1' }, '3').distance, '2 plantes més avall');
  assert.match(hereFloorStatus({ floorId: '0' }, '0').description, /planta baixa/);
});

test('els nivells físics i la ubicació per defecte venen de la configuració', () => {
 const configured=[{id:'soterrani',level:-1,name:'Soterrani'},{id:'terrassa',level:7,name:'Terrassa'}];
 const fallback={floorId:'soterrani',x:25,y:75};
 assert.deepEqual(parseHere('',configured,fallback),fallback);
 assert.equal(parseHere('?x=30',configured,fallback),null);
 assert.deepEqual(parseHere('?aqui=terrassa&x=50&y=0',configured,fallback),{floorId:'terrassa',x:50,y:0});
 assert.equal(floorStatus(fallback,'terrassa',configured,texts).distance,'8 plantes més avall');
 assert.equal(floorStatus({floorId:'terrassa'},'soterrani',configured,texts).direction,'up');
});
