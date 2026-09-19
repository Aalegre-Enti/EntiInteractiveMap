import test from 'node:test';
import assert from 'node:assert/strict';
import { config, rawConfig } from './config-fixture.js';
import { validateConfig, loadConfig, formatText } from '../src/config.js';

test('la configuració deriva sales i plantes sense modificar el JSON original', () => {
  assert.ok(config.floors.length > 0);
  assert.ok(config.floors.every(floor => floor.rooms.every(room => room.floorId === floor.id)));
  assert.ok(rawConfig.floors.every(floor => floor.rooms.every(room => room.floorId === undefined)));
});

test('admet qualsevol nombre de plantes, soterranis, sales mínimes i nous períodes', () => {
  const input = structuredClone(rawConfig);
  const template = input.floors[0];
  input.floors = Array.from({length: 9}, (_, i) => ({
    id: `nivell_${i}`, level: i - 2, name: `Nivell ${i - 2}`, image: template.image,
    width: template.width, height: template.height, rooms: [{ code: 'Sala / amb accents', uses: [{period: 'vespre', institution:'Centre', activity:'Taller'}] }],
  }));
  input.periods = [{id:'vespre',label:'Vespre'}];
  input.view.defaultFloorId = 'nivell_8';
  input.here.defaultLocation = {floorId:'nivell_0',x:0,y:100};
  const result = validateConfig(input);
  assert.equal(result.floors.length,9);
  assert.equal(result.floors[0].level,-2);
  assert.equal(result.floors[0].rooms[0].name,'Sala / amb accents');
  assert.equal(result.floors[0].rooms[0].id,'nivell_0-Sala / amb accents');
});

test('rebutja configuracions amb identificadors, referències i valors invàlids', () => {
  const cases = [
    [c=>c.floors=[], /floors/],
    [c=>c.floors.push(structuredClone(c.floors[0])), /duplicats/],
    [c=>c.floors[0].rooms.push(structuredClone(c.floors[0].rooms[0])), /duplicats/],
    [c=>c.floors[0].id='amb espais', /\.id/],
    [c=>c.floors[0].level=1.5, /level/],
    [c=>c.view.defaultFloorId='inexistent', /defaultFloorId/],
    [c=>c.here.defaultLocation={floorId:c.floors[0].id,x:101,y:50}, /defaultLocation.x/],
    [c=>c.theme.brand='red', /theme.brand/],
    [c=>c.view.maxZoom=0, /maxZoom/],
    [c=>c.overlay.opacity=2, /opacity/],
    [c=>c.floors[0].image='javascript:alert(1)', /image/],
    [c=>c.floors[0].rooms[0].uses=[{institution:'Centre',activity:'Taller',period:'missing'}], /period/],
    [c=>c.floors[0].rooms[0].icon='missing', /icona/],
  ];
  for(const [change,pattern] of cases) {
    const input=structuredClone(rawConfig); change(input);
    assert.throws(()=>validateConfig(input), pattern);
  }
});

test('carrega el JSON i informa d’errors HTTP, JSON i validació', async () => {
  let requested;
  const result=await loadConfig('config.json', async (url, options)=>{
    requested={url,options}; return {ok:true,json:async()=>rawConfig};
  });
  assert.equal(result.floors.length,rawConfig.floors.length);
  assert.equal(requested.options.cache,'no-cache');
  await assert.rejects(loadConfig('config.json',async()=>({ok:false,status:404})),/404/);
  await assert.rejects(loadConfig('config.json',async()=>({ok:true,json:async()=>{throw new SyntaxError('JSON invàlid');}})),/JSON invàlid/);
  await assert.rejects(loadConfig('config.json',async()=>({ok:true,json:async()=>({version:99})})),/version/);
});

test('els textos substitueixen variables com a text pla', () => {
  assert.equal(formatText({title:'{room} · {floor}'},'title',{room:'Sala {especial}',floor:'Baixa'}),'Sala {especial} · Baixa');
});

test('els punts de sala validen les coordenades i permeten etiquetes pròpies', () => {
  const input = structuredClone(rawConfig);
  const room = input.floors[0].rooms[0];
  room.marker = { x: 0, y: 100, label: 'Etiqueta curta' };
  const result = validateConfig(input);
  assert.deepEqual(result.floors[0].rooms[0].marker, {x:0,y:100,label:'Etiqueta curta',labelPosition:'bottom'});
  for (const marker of [{x:101,y:50}, {x:50,y:-1}, {x:'50',y:50}, {x:50}, {x:50,y:50,labelPosition:'unknown'}, {x:50,y:50,label:''}]) {
    room.marker = marker;
    assert.throws(() => validateConfig(input), /marker/);
  }
  room.marker = null;
  assert.equal(validateConfig(input).floors[0].rooms[0].marker, null);
  delete room.marker;
  delete input.roomMarkers;
  assert.equal(validateConfig(input).roomMarkers.enabled, true);
  input.roomMarkers = {inactiveOpacity:2};
  assert.throws(() => validateConfig(input), /inactiveOpacity/);
});
