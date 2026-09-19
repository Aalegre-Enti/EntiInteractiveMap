# Mapa interactiu de l’edifici

Aplicació estàtica en català per explorar els cinc nivells de l’edifici. Funciona en ordinadors, tauletes i mòbils, sense serveis externs ni dependències de producció.

## Funcions

- Selector de cinc plantes amb els plànols nets proporcionats.
- Submenú per planta amb els 39 espais de `Rooms.ods`, 15 espais comuns addicionals i una entrada de lavabos a cadascuna de les cinc plantes.
- Fitxes desplegables amb els centres i usos, diferenciant entre setmana i caps de setmana. Oficines, Menjador, Sala d’estudi i els espais comuns afegits tenen una icona pròpia i el mateix estil que els lavabos, sense informació dels centres ni usos acadèmics.
- Ampliació amb botons, roda del ratolí i gest de dos dits.
- Desplaçament amb ratolí, dit o teclat; botó per encaixar el plànol.
- Pantalla completa, amb alternativa per als navegadors que no admeten aquesta funció.
- Enllaços a cada planta, com ara `#planta-3`.
- Controls accessibles, ajuda en català i respecte per la preferència de moviment reduït.
- Capa de punts i àrees ressaltades preparada per afegir-hi les ubicacions dels espais sobre el plànol.

## Previsualització local

Amb Node.js 18 o posterior:

```sh
npm run dev
```

Obre `http://127.0.0.1:4173`. No cal instal·lar paquets. Si no tens npm disponible, executa `node scripts/serve.mjs`. També es pot utilitzar qualsevol servidor de fitxers estàtics; cal servir la carpeta per HTTP, ja que el navegador no carrega els mòduls JavaScript si s’obre `index.html` directament com a fitxer.

```sh
npm test
```

Les proves comproven els cinc fitxers de plànol, les dimensions i els càlculs d’ampliació i desplaçament.

## Publicació a GitHub Pages

1. Puja els fitxers al repositori de GitHub, incloent-hi `img`, `src`, `index.html`, `styles.css`, `favicon.svg` i `.nojekyll`.
2. A **Settings → Pages → Build and deployment**, tria **Deploy from a branch**.
3. Selecciona la branca que conté l’aplicació i la carpeta **/ (root)**. Desa els canvis.
4. GitHub mostrarà l’adreça del lloc quan acabi la publicació.

No hi ha cap pas de compilació. Totes les rutes són relatives, de manera que l’app funciona tant en un domini propi com en el subdirectori d’un repositori de GitHub Pages. No cal cap servidor Node.js a producció. La configuració de Pages i la publicació al repositori s’han de fer a GitHub; no les activa la previsualització local.

## Actualitzar la llista d’espais

`Rooms.ods` és la font de les dades. Per actualitzar la llista després d’editar el full, executa amb Python 3:

```sh
python scripts/import_rooms.py
```

L’importador genera `src/rooms.js` sense modificar el full. Conserva totes les assignacions de les columnes ENTI i EUSES (entre setmana) i ISEP i FISIOFOCUS (caps de setmana), i tradueix els textos al català. Manté els codis i les denominacions Artist, Developer i E Leader. Els camps buits no es converteixen en assignacions. Si apareix una descripció nova, cal afegir-ne la traducció a l’importador abans de regenerar les dades.

La importació actual conté 39 espais: 7 a la planta baixa, 10 a la primera, 10 a la segona, 7 a la tercera i 5 a la quarta. La fila 41 no té ni codi ni planta; es conserva al full i es registra a `roomImport.skippedRows`, però no es mostra en cap planta.

`src/floors.js` afegeix Lavabos, Ascensors i Escales a cada planta; Vestíbul, Entrada i Sala de tutories a la planta baixa; i Sala de vending i Terrassa a la quarta planta. També configura Oficines, Menjador i Sala d’estudi perquè no mostrin centres ni usos. Aquestes personalitzacions es mantenen quan es torna a importar el full. En total hi ha 59 entrades: 13, 13, 13, 10 i 10, de la planta baixa a la quarta.

En seleccionar una planta es desplega la seva llista. Els espais amb informació d’ús es poden desplegar per consultar-la; «Espais de la planta» permet plegar la llista. Al mòbil, el submenú apareix sota els cinc selectors, amb desplaçament propi per mantenir el mapa a l’abast. La publicació continua sent estàtica i no necessita Python ni el full de càlcul al navegador.

## Afegir ubicacions dels espais

Les plantes es defineixen a `src/floors.js`. Cada planta té un camp `points`, actualment buit. Quan es disposi de la informació real, s’hi poden afegir entrades com aquesta (coordenades només d’exemple):

```js
points: [
  {
    id: 'identificador-espai',
    title: 'Nom de l’espai',
    description: 'Informació de l’espai en català.',
    x: 50,
    y: 40,
    polygon: [[40, 30], [60, 30], [60, 50], [40, 50]],
  },
],
```

`x` i `y` indiquen la posició del marcador com a percentatges de l’amplada i de l’alçada de la imatge original. L’origen és la cantonada superior esquerra. `polygon` és opcional i permet ressaltar l’àrea de l’espai quan es prem el marcador. El marcador i la zona segueixen el plànol en ampliar o desplaçar-lo; la fitxa es pot tancar amb el seu botó o amb la tecla Esc. Els textos es mostren com a text pla.

Els plànols originals i els retalls d’espais es conserven a `img` per a futures ampliacions. L’aplicació actual utilitza les cinc imatges de `img/CleanedFloorplan`.

## Estil

El color principal és `#94167f`, definit a la variable `--brand` de `styles.css`. No es carreguen tipografies, recursos ni serveis de tercers.
