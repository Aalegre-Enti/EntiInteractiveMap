# Mapa interactiu de l’edifici

Aplicació estàtica en català, adaptable a ordinadors i mòbils i compatible amb GitHub Pages. Totes les dades i opcions de l’edifici són a **`config.json`**. No cal editar JavaScript per afegir plantes, sales o capes.

## Configuració

Edita `config.json`, desa’l i recarrega la pàgina. A GitHub Pages, publica també aquest fitxer. El JSON no admet comentaris ni comes després de l’últim element.

| Apartat | Què configura |
| --- | --- |
| `site` | Nom, descripció, idioma, icona i favicon. |
| `theme` | Color principal `brand`, text `ink`, text secundari `muted`, vores `line`, fons `surface` i tipografia `fontFamily`. Els colors utilitzen `#RRGGBB`. |
| `floors` | Plantes, ordre del menú, imatges, sales, usos, capes i punts d’informació. La quantitat de plantes es calcula automàticament. |
| `periods` | Identificadors i noms dels períodes d’ús, com ara entre setmana i caps de setmana. |
| `view` | Planta inicial, ampliació màxima, pas d’ampliació, marge inicial, sensibilitat de la roda, desplaçament amb teclat i menú mòbil plegat. |
| `overlay` | Opacitat fixa, opacitat màxima de la pulsació, durada de cada cicle en segons i nombre de cicles. `pulseCount: 0` desactiva la pulsació. |
| `roomMarkers` | Visibilitat dels punts de sala (`enabled`), opacitat quan no estan seleccionats (`inactiveOpacity`), diàmetre del punt (`dotSize`) i mida de l’etiqueta (`labelSize`), en píxels. |
| `here` | Etiqueta, mida del punt en píxels, opacitat en altres plantes i ubicació per defecte. |
| `texts` | Textos visibles, ajuda, missatges i etiquetes accessibles. Conserva les variables entre claus, com `{room}`, `{floor}` o `{count}`. |
| `import` | Opcions de la importació opcional del full ODS: origen, columnes, centres, períodes, noms, traduccions i registre de files incompletes. |

La configuració conté cinc plantes i 63 espais, tots amb punt i capa de ressaltat. Tots els plànols i les capes comparteixen un llenç de 1200 × 895 píxels per mantenir l’alineació entre plantes. Els lavabos, ascensors, escales i altres espais comuns són sales explícites del JSON: pots afegir-los, canviar-los o retirar-los per planta.

### Afegir una planta

Afegeix un objecte a `floors`, a la posició on vols que aparegui al menú. Exemple que reutilitza un plànol existent; substitueix la imatge i les dimensions pel nou plànol:

```json
{
  "id": "soterrani",
  "level": -1,
  "code": "S1",
  "name": "Soterrani",
  "shortName": "Soterrani",
  "image": "./img/CleanedFloorplan/Level0.png",
  "width": 1200,
  "height": 895,
  "importAliases": ["S1"],
  "rooms": [],
  "points": []
}
```

- `id`: identificador únic i estable, escrit com a text. Admet lletres, números, guions i guions baixos. S’utilitza als enllaços.
- `level`: nivell físic enter i únic; admet negatius. Les fletxes d’«Ets aquí» calculen la diferència entre aquests nivells, independentment de l’ordre del menú.
- `code`, `name` i `shortName`: etiqueta curta, nom complet i nom per al mòbil. `code` i `shortName` poden ometre’s: es deriven d’`id` i `name`.
- `image`: ruta relativa a la pàgina. `width` i `height`: dimensions originals de la imatge, en píxels.
- `rooms` i `points`: llistes opcionals; poden estar buides.
- `importAliases`: noms que el full de càlcul fa servir per aquesta planta; només afecta l’importador.

No hi ha un límit fix de cinc plantes. Al mòbil el selector es desplaça horitzontalment quan cal. Si retires una planta, revisa també `view.defaultFloorId` i `here.defaultLocation`.

### Afegir una sala

Afegeix-la a `rooms` de la planta corresponent:

```json
{
  "code": "A.01",
  "name": "Aula de pràctiques",
  "kind": "room",
  "showUsage": true,
  "uses": [
    {
      "institution": "Nom del centre",
      "period": "weekdays",
      "activity": "Classes pràctiques"
    }
  ]
}
```

`code` és obligatori i únic dins la planta. `name` pot ometre’s per mostrar el codi. `id` és opcional i es deriva de la planta i el codi; si el defineixes, ha de ser únic a tot l’edifici. Cada `uses[].period` ha de correspondre a un `id` de `periods`.

Per a un espai comú, utilitza `kind: "common"`; per als lavabos, `kind: "bathroom"`. Tots dos amaguen els usos per defecte i utilitzen l’estil compacte amb icona. `showUsage: false` també permet amagar els usos d’una aula existent, com Oficines, Menjador o Sala d’estudi.

```json
{
  "code": "ASCENSORS",
  "name": "Ascensors",
  "kind": "common",
  "icon": "elevator",
  "subtitle": "Espai comú"
}
```

Opcions visuals de les sales comunes:

- `icon`: `office`, `dining`, `study`, `lobby`, `entrance`, `tutoring`, `vending`, `terrace`, `elevator`, `stairs`, `auditorium`, `map`, `layers`, `pin`, `info`, `help`, `plus`, `minus`, `fit`, `expand`, `close`, `arrow` o `move`.
- `iconImage`: ruta a una imatge pròpia, que té prioritat sobre la icona incorporada.
- `badge`: text curt en lloc d’icona, per exemple `"WC"`.
- `subtitle`: text sota el nom. Sense aquest camp, es mostra el text de serveis o espai comú de `texts`.

Per destacar una sala al mapa, afegeix `overlay` amb la ruta a la seva capa, per exemple `"./img/CleanedFloorplan/Level0/Auditori.png"`. La capa ha de ser una imatge transparent amb les mateixes dimensions i alineació que el plànol complet. L’app utilitza el canal alfa per aplicar el color de `theme.brand`. Sense `overlay`, la sala conserva la informació i l’enllaç, però no mostra ressaltat.

Les dades són text pla, no HTML. Només una fitxa de sala pot quedar desplegada alhora. En seleccionar-la, la URL s’actualitza; recarregar o compartir l’enllaç recupera la planta i la sala. Exemple: `#planta-0/sala/PB.01`. També funciona amb plantes noves: `#planta-soterrani/sala/A.01`.

### Punts de les sales

Cada espai actual té un punt amb una etiqueta curta. Només apareixen els punts de la planta que s’està consultant. Prémer un punt selecciona la sala, desplega la seva informació, actualitza l’enllaç i mostra la capa si en té. El punt seleccionat té intensitat completa; els altres queden atenuats. La selecció també se sincronitza amb el menú, els enllaços compartits i els botons enrere i endavant.

Afegeix o modifica `marker` dins de cada sala:

```json
"marker": {
  "x": 38.04,
  "y": 15.47,
  "label": "PB.01",
  "labelPosition": "bottom"
}
```

`x` i `y` són percentatges entre 0 i 100 de la imatge completa, amb l’origen a dalt a l’esquerra. Les posicions s’han ajustat al llenç compartit de 1200 × 895 píxels i s’ha comprovat que cada punt queda dins de la seva capa. `label` és opcional: per defecte s’utilitza el nom de la sala. `labelPosition` admet `top`, `bottom`, `left` o `right` per evitar que les etiquetes se superposin; el valor per defecte és `bottom`. Els punts mantenen la mida visual en ampliar el plànol.

Per a sales noves, defineix les coordenades a `marker`; sense aquestes coordenades, la sala continua disponible al menú. `marker: null` amaga un punt individual i `roomMarkers.enabled: false` els amaga tots. La importació de l’ODS conserva els punts i les etiquetes ja configurats.

### Punt «Ets aquí»

Per establir una ubicació fixa per defecte:

```json
"here": {
  "label": "Ets aquí",
  "defaultLocation": { "floorId": "1", "x": 52.5, "y": 60 },
  "otherFloorOpacity": 0.65,
  "size": 28
}
```

Utilitza `defaultLocation: null` per no mostrar cap ubicació per defecte. La URL pot substituir-la:

```text
?aqui=1&x=52.5&y=60#planta-0/sala/PB.01
```

`aqui` és l’`id` de qualsevol planta configurada. `x` i `y` són percentatges de la imatge completa entre 0 i 100, d’esquerra a dreta i de dalt a baix; admeten decimals amb punt. Si la URL no conté cap dels tres paràmetres, s’utilitza la ubicació del JSON. Si els paràmetres són incomplets o invàlids, no es mostra cap punt.

Sense fragment explícit de planta, s’obre la planta de la ubicació; si no hi ha ubicació, s’obre `view.defaultFloorId`. En altres plantes el marcador queda atenuat i les fletxes indiquen on és la ubicació real. El punt conserva la mida visual en ampliar i no utilitza el GPS.

### Punts d’informació

Afegeix entrades a `points` dins d’una planta. Les coordenades són percentatges; `description`, `icon` i `polygon` són opcionals:

```json
{
  "title": "Punt d’informació",
  "description": "Atenció al públic.",
  "icon": "info",
  "x": 50,
  "y": 40,
  "polygon": [[40, 30], [60, 30], [60, 50], [40, 50]]
}
```

## Importació opcional de Rooms.ods

Pots editar directament el JSON sense utilitzar el full. Si prefereixes continuar actualitzant els usos des del full, executa amb Python 3:

```sh
python scripts/import_rooms.py
```

L’importador llegeix `import.source` i actualitza **`config.json`**, sense modificar l’ODS ni generar fitxers JavaScript. Les primeres dues columnes han de correspondre a `codeColumn` i `floorColumn`; les següents, a `import.columns`, en el mateix ordre. Les plantes es reconeixen per `id` o `importAliases`. Les traduccions són a `import.translations` i `import.translationPatterns`; afegeix les noves activitats abans d’importar. `import.names` proporciona el nom inicial de sales noves.

Les sales del full tenen `source: "spreadsheet"`. Quan es torna a importar:

- Es renoven els usos de cada sala coincident per planta i codi.
- Es conserven els noms personalitzats, tipus, icones, capes i visibilitat dels usos.
- S’afegeixen les sales noves i es retiren les sales amb `source: "spreadsheet"` que ja no apareixen al full.
- Es conserven les sales manuals que no apareixen al full.
- Les files incompletes es registren a `import.metadata.skippedRows`; una planta, període o traducció desconeguts aturen la importació abans d’escriure.

A la tercera planta, l’antic Estudi de música es divideix en Sala de gravació, Sala de control i Bucs de gravació, cadascun amb un punt propi. La Sala de gravació conserva el codi `ESTUDI MUSICA` per mantenir els enllaços anteriors i la relació amb el full; les altres dues entrades són manuals. Les tres conserven l’ús d’ENTI de l’espai original.

El Magatzem de música és una altra entrada manual de la tercera planta, incorporada amb la seva capa proporcionada. No té centres ni usos assignats.

## Previsualització i comprovacions

Amb Node.js 18 o posterior, sense instal·lar paquets:

```sh
node scripts/serve.mjs
node --test
python -B -m unittest discover -s tests -p "*_test.py"
```

Obre `http://127.0.0.1:4173`. També pots utilitzar `npm run dev` i `npm test`. Cal un servidor HTTP: obrir `index.html` directament com a fitxer no carrega el JSON ni els mòduls.

L’app valida identificadors, referències, coordenades i paràmetres abans de mostrar el mapa. Si el JSON no es pot carregar o conté errors, ofereix tornar-ho a provar; la consola del navegador indica el camp que cal corregir. Els missatges inicials d’error i càrrega són en català i viuen al codi perquè han de funcionar fins i tot sense configuració.

## GitHub Pages

1. Puja `config.json`, `index.html`, `styles.css`, `favicon.svg`, `src`, `img` i `.nojekyll` al repositori.
2. A **Settings → Pages → Build and deployment**, tria **Deploy from a branch**.
3. Selecciona la branca de l’aplicació i **/ (root)**.

No cal compilació ni servidor a producció. Les rutes relatives funcionen també dins del subdirectori d’un repositori. Només cal tornar a publicar els fitxers modificats; l’ODS i Python no són necessaris al navegador.
