// Cada PNG té la mida del plànol complet i delimita l'espai amb el canal alfa.
// Els noms dels fitxers originals es conserven, inclosos els accents.
const groundFloorFiles = {
  'AUD-01': 'AUD.01.png',
  'AUD-02': 'AUD.02.png',
  'PB.01': 'PB.01.png',
  'PB.02': 'PB.02.png',
  'PB.03': 'PB.03.png',
  'PB.04': 'PB.04.png',
  'PB.05': 'PB.05.png',
  AUDITORI: 'Auditori.png',
  VESTIBUL: 'Vestíbul.png',
  ENTRADA: 'Entrada.png',
  TUTORIES: 'Sala de tutoríes.png',
  ASCENSORS: 'Ascensors.png',
  ESCALES: 'Escales.png',
  WC: 'WC.png',
};

const firstFloorFiles = {
  '1.01': '1.01.png',
  '1.02': '1.02.png',
  '1.03': '1.03.png',
  '1.04': '1.04.png',
  '1.05': '1.05.png',
  'LAB.REHAB': 'Lab-Rehab.png',
  'LAB-1.01': 'LAB-1.01.png',
  'LAB-1.02': 'LAB-1.02.png',
  'SALA ESTUDI': "Sala d'estudi.png",
  'SALA SIMULACIO': 'Simulació.png',
};

export const roomOverlays = {
  '0': Object.fromEntries(Object.entries(groundFloorFiles).map(([code, file]) => [
    code, `./img/CleanedFloorplan/Level0/${encodeURIComponent(file)}`,
  ])),
  '1': Object.fromEntries(Object.entries(firstFloorFiles).map(([code, file]) => [
    code, `./img/CleanedFloorplan/Level1/${encodeURIComponent(file)}`,
  ])),
};
