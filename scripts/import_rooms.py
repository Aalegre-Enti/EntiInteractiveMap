"""Extreu Rooms.ods sense modificar-lo i genera les dades estàtiques de l'app."""

from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}
COLUMNS = [
    ("ENTI - During the week", "ENTI", "weekdays"),
    ("EUSES - During the week", "EUSES", "weekdays"),
    ("ISEP - Weekends", "ISEP", "weekends"),
    ("FISIOFOCUS - Weekends", "FISIOFOCUS", "weekends"),
]
NAMES = {
    "ESTUDI MUSICA": "Estudi de música",
    "OFICINES": "Oficines",
    "SALA ESTUDI": "Sala d’estudi",
    "MENJADOR": "Menjador",
    "SALA SIMULACIO": "Sala de simulació",
}
TRANSLATIONS = {
    "GRADO FISIO": "Grau de fisioteràpia",
    "FISIO": "Fisioteràpia",
    "GRADO MUSICA": "Grau de música",
    "GRADO ARTIST": "Grau Artist",
    "GRADO DEVELOPER": "Grau Developer",
    "GRADO CIBER": "Grau de ciberseguretat",
    "GRADO I CICLO CIBER": "Grau i cicle de ciberseguretat",
    "CICLO ARTISTA": "Cicle d’artista",
    "CICLO DEVELOPER": "Cicle Developer",
    "CICLO FINANZAS": "Cicle de finances",
    "CICLO MARKETING": "Cicle de màrqueting",
    "CICLO TECNICO DE SONIDO": "Cicle de tècnic de so",
    "CICLO CIBER": "Cicle de ciberseguretat",
    "CICLO SALUT": "Cicle de salut",
    "AULA COMODIN": "Aula comodí",
    "AREA MUSICA ENTI": "Àrea de música ENTI",
    "AREA VIDEOJUEGOS ENTI": "Àrea de videojocs ENTI",
    "TODOS": "Tots",
    "MASTER E LEADER": "Màster E Leader",
    "MASTER MUSICA I CIBER": "Màster de música i ciberseguretat",
    "NUEVO GRADO": "Nou grau",
}


def translate(value):
    if "/" in value:
        return " / ".join(translate(part.strip()) for part in value.split("/"))
    if value in TRANSLATIONS:
        return TRANSLATIONS[value]
    if re.fullmatch(r"CICLO SALUT \d+", value):
        return "Cicle de salut " + value.rsplit(" ", 1)[1]
    if re.fullmatch(r"MASTER \d+", value):
        return "Màster " + value.rsplit(" ", 1)[1]
    if re.fullmatch(r"CURS ISEP \d+", value):
        return "Curs ISEP " + value.rsplit(" ", 1)[1]
    raise ValueError(f"Cal afegir la traducció al català de: {value!r}")


def read_rows(source):
    with ZipFile(source) as archive:
        root = ET.fromstring(archive.read("content.xml"))
    table = root.find(".//table:table", NS)
    if table is None:
        raise ValueError("El fitxer no conté cap full.")
    for row_number, row in enumerate(table.findall("table:table-row", NS), 1):
        cells = []
        for cell in row:
            value = "\n".join("".join(p.itertext()) for p in cell.findall("text:p", NS)).strip()
            repeat = int(cell.get(f"{{{NS['table']}}}number-columns-repeated", "1"))
            cells.extend([value] * min(repeat, 6 - len(cells)))
            if len(cells) == 6:
                break
        if any(cells):
            yield row_number, cells + [""] * (6 - len(cells))


def import_rooms(source):
    rows = iter(read_rows(source))
    _, headers = next(rows)
    expected = ["CODE", "LEVEL"] + [column[0] for column in COLUMNS]
    if headers != expected:
        raise ValueError(f"Les columnes han canviat: {headers}")
    rooms, skipped, ids = [], [], set()
    for row_number, values in rows:
        code, level = values[:2]
        if not code or not level:
            skipped.append({"row": row_number, "reason": "Falta el nom o la planta", "values": values})
            continue
        if level not in {"PB", "P1", "P2", "P3", "P4"}:
            raise ValueError(f"Planta desconeguda a la fila {row_number}: {level}")
        floor_id = "0" if level == "PB" else level[1:]
        room_id = f"{floor_id}-{code}"
        if room_id in ids:
            raise ValueError(f"Espai duplicat: {room_id}")
        ids.add(room_id)
        uses = [
            {"institution": institution, "period": period, "activity": translate(value)}
            for value, (_, institution, period) in zip(values[2:], COLUMNS)
            if value
        ]
        rooms.append({"id": room_id, "code": code, "name": NAMES.get(code, code), "floorId": floor_id, "kind": "room", "uses": uses})
    return rooms, skipped


if __name__ == "__main__":
    rooms, skipped = import_rooms(ROOT / "Rooms.ods")
    output = "// Generat a partir de Rooms.ods amb scripts/import_rooms.py.\n"
    output += "// Les files incompletes es conserven al full original.\n"
    output += "export const roomImport = " + json.dumps({"source": "Rooms.ods", "roomCount": len(rooms), "skippedRows": skipped}, ensure_ascii=False, indent=2) + ";\n\n"
    output += "export const rooms = " + json.dumps(rooms, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "src" / "rooms.js").write_text(output, encoding="utf-8")
    print(f"Importats {len(rooms)} espais: {dict(sorted(Counter(room['floorId'] for room in rooms).items()))}")
    for row in skipped:
        print(f"Fila {row['row']} pendent: {row['reason']}.")
