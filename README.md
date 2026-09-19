# Mapa interactiu de l’edifici

Aplicació estàtica en català per explorar els cinc nivells de l’edifici. Funciona en ordinadors, tauletes i mòbils, sense serveis externs ni dependències de producció.

## Funcions

- Selector de cinc plantes amb els plànols nets proporcionats.
- Submenú per planta amb els 39 espais de `Rooms.ods`, 16 espais comuns addicionals i una entrada de lavabos a cadascuna de les cinc plantes.
- Ressaltat dels 14 espais de la planta baixa i de 10 espais de la primera planta amb les capes proporcionades: lila que polsa durant tres segons i després queda semitransparent.
- Fitxes desplegables amb els centres i usos, diferenciant entre setmana i caps de setmana. Oficines, Menjador, Sala d’estudi i els espais comuns afegits tenen una icona pròpia i el mateix estil que els lavabos, sense informació dels centres ni usos acadèmics.
- Ampliació amb botons, roda del ratolí i gest de dos dits.
- Desplaçament amb ratolí, dit o teclat; botó per encaixar el plànol.
- Pantalla completa, amb alternativa per als navegadors que no admeten aquesta funció.
- Enllaços a cada planta i sala, com ara `#planta-3` o `#planta-0/sala/PB.01`. La URL s’actualitza en seleccionar un espai i es pot copiar per compartir-lo.
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

`src/floors.js` afegeix Lavabos, Ascensors i Escales a cada planta; Auditori, Vestíbul, Entrada i Sala de tutories a la planta baixa; i Sala de vending i Terrassa a la quarta planta. També configura Oficines, Menjador i Sala d’estudi perquè no mostrin centres ni usos. Aquestes personalitzacions es mantenen quan es torna a importar el full. En total hi ha 60 entrades: 14, 13, 13, 10 i 10, de la planta baixa a la quarta.

En seleccionar una planta es desplega la seva llista a l’escriptori. Al mòbil, la llista comença plegada per deixar més espai al mapa; es pot obrir amb «Espais de la planta» o prement de nou la planta activa. Les llistes tenen desplaçament propi. Els espais amb informació d’ús es poden desplegar per consultar-la; només hi ha una fitxa d’informació oberta a la vegada. Les capçaleres, els marges i els controls són compactes, amb botons d’almenys 44 píxels d’alçada. La publicació continua sent estàtica i no necessita Python ni el full de càlcul al navegador.

En seleccionar qualsevol espai, inclosos els comuns, la URL incorpora la planta i el codi de la sala (`#planta-0/sala/AUDITORI`, per exemple). Obrir o recarregar aquest enllaç recupera la planta, desplega la llista i la informació disponible, marca la sala i carrega el ressaltat si té capa. També funciona amb els botons enrere i endavant del navegador. Canviar de planta o desmarcar amb Esc elimina la sala de la URL. Els fragments de la URL funcionen en subdirectoris de GitHub Pages sense configurar redireccions.

## Afegir ubicacions dels espais

Les capes PNG es relacionen amb els codis dels espais a `src/room-overlays.js`. Cada imatge ha de conservar les dimensions del plànol complet (1083 × 976 píxels per a la planta baixa; 1200 × 895 per a la primera planta) i delimitar l’espai amb transparència. L’app utilitza el canal alfa com a màscara del color `#94167f`, sense modificar els fitxers originals. L’Auditori comú utilitza `Auditori.png`; AUD-01 i AUD-02 utilitzen les seves capes individuals.

La primera planta té capes per a les aules 1.01–1.05, LAB.REHAB, LAB-1.01, LAB-1.02, Sala d’estudi i Sala de simulació. Els fitxers són a `img/CleanedFloorplan/Level1`. Ascensors, Escales i Lavabos mantenen la selecció i l’enllaç directe, però encara no tenen una capa proporcionada en aquesta planta.

En seleccionar un espai es mostra el plànol sencer, es ressalta només la seva zona i es marca la fila seleccionada. La capa polsa durant tres segons, entre un 32% i un 65% d’opacitat, i després es manté al 32%. La preferència de moviment reduït omet la pulsació. La capa segueix el plànol en ampliar-lo o desplaçar-lo; seleccionar un altre espai la substitueix, i canviar de planta o prémer Esc la retira. Al mòbil, la selecció porta el plànol a la vista. Les altres plantes mantenen les seves llistes i queden preparades per afegir-hi capes al mateix fitxer de configuració.

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
