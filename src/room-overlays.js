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

export const roomOverlays = {
  '0': Object.fromEntries(Object.entries(groundFloorFiles).map(([code, file]) => [
    code, `./img/CleanedFloorplan/Level0/${encodeURIComponent(file)}`,
  ])),
};
