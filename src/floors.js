import { rooms } from './rooms.js';

// Aquests espais es mostren només pel nom, sense centres ni usos.
const nameOnlyRooms = new Set(['OFICINES', 'MENJADOR', 'SALA ESTUDI']);
const sharedSpaces = [['ASCENSORS', 'Ascensors'], ['ESCALES', 'Escales']];
const commonSpacesByFloor = {
  '0': [['VESTIBUL', 'Vestíbul'], ['ENTRADA', 'Entrada'], ['TUTORIES', 'Sala de tutories']],
  '4': [['VENDING', 'Sala de vending'], ['TERRASSA', 'Terrassa']],
};

// Coordenades dels punts i polígons: percentatges (0–100) de la imatge.
// La llista d'espais no pressuposa una ubicació dins del plànol.
export const floors = [
  { id: '0', code: 'PB', name: 'Planta baixa', shortName: 'Baixa', image: './img/CleanedFloorplan/Level0.png', width: 1083, height: 976, points: [] },
  { id: '1', code: '01', name: 'Primera planta', shortName: 'Primera', image: './img/CleanedFloorplan/Level1.png', width: 1200, height: 895, points: [] },
  { id: '2', code: '02', name: 'Segona planta', shortName: 'Segona', image: './img/CleanedFloorplan/Level2.png', width: 1200, height: 895, points: [] },
  { id: '3', code: '03', name: 'Tercera planta', shortName: 'Tercera', image: './img/CleanedFloorplan/Level3.png', width: 1200, height: 895, points: [] },
  { id: '4', code: '04', name: 'Quarta planta', shortName: 'Quarta', image: './img/CleanedFloorplan/Level4.png', width: 1136, height: 941, points: [] },
].map((floor) => ({
  ...floor,
  rooms: [
    ...rooms.filter((room) => room.floorId === floor.id).map((room) => ({
      ...room,
      showUsage: !nameOnlyRooms.has(room.code),
    })),
    ...[...(commonSpacesByFloor[floor.id] ?? []), ...sharedSpaces].map(([code, name]) => ({
      id: `${floor.id}-${code.toLowerCase()}`,
      code,
      name,
      floorId: floor.id,
      kind: 'common',
      showUsage: false,
      uses: [],
    })),
    { id: `${floor.id}-wc`, code: 'WC', name: 'Lavabos', floorId: floor.id, kind: 'bathroom', uses: [] },
  ],
}));
