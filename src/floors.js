import { rooms } from './rooms.js';

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
    ...rooms.filter((room) => room.floorId === floor.id),
    { id: `${floor.id}-wc`, code: 'WC', name: 'Lavabos', floorId: floor.id, kind: 'bathroom', uses: [] },
  ],
}));
