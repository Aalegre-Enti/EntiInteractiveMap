"""Actualitza config.json des d'un ODS, conservant les personalitzacions."""

from copy import deepcopy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
NS = {"table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0", "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}


def translate(value, settings):
    if "/" in value:
        return " / ".join(translate(part.strip(), settings) for part in value.split("/"))
    if value in settings.get("translations", {}):
        return settings["translations"][value]
    for rule in settings.get("translationPatterns", []):
        if re.fullmatch(rule["pattern"], value):
            return re.sub(rule["pattern"], rule["replacement"], value)
    raise ValueError(f"Afegeix a import.translations la traducció de: {value!r}")


def read_rows(source, column_count):
    with ZipFile(source) as archive:
        root = ET.fromstring(archive.read("content.xml"))
    table = root.find(".//table:table", NS)
    if table is None:
        raise ValueError("El fitxer no conté cap full.")
    row_number = 1
    for row in table.findall("table:table-row", NS):
        cells = []
        for cell in row:
            value = "\n".join("".join(p.itertext()) for p in cell.findall("text:p", NS)).strip()
            repeat = int(cell.get(f"{{{NS['table']}}}number-columns-repeated", "1"))
            cells.extend([value] * min(repeat, column_count - len(cells)))
            if len(cells) == column_count:
                break
        row_repeat = int(row.get(f"{{{NS['table']}}}number-rows-repeated", "1"))
        if any(cells):
            for offset in range(row_repeat):
                yield row_number + offset, cells + [""] * (column_count - len(cells))
        row_number += row_repeat


def import_rooms(source, config):
    settings = config["import"]
    columns = settings["columns"]
    periods = {period["id"] for period in config["periods"]}
    if any(column["period"] not in periods for column in columns):
        raise ValueError("Una columna d'importació utilitza un període desconegut.")
    aliases = {}
    for floor in config["floors"]:
        for alias in {floor["id"], *floor.get("importAliases", [])}:
            if alias in aliases and aliases[alias] != floor["id"]:
                raise ValueError(f"Àlies de planta duplicat: {alias}")
            aliases[alias] = floor["id"]
    rows = iter(read_rows(source, len(columns) + 2))
    _, headers = next(rows)
    expected = [settings["codeColumn"], settings["floorColumn"]] + [column["header"] for column in columns]
    if headers != expected:
        raise ValueError(f"Les columnes no coincideixen amb import.columns: {headers}")
    rooms, skipped, ids = [], [], set()
    for row_number, values in rows:
        code, level = values[:2]
        if not code or not level:
            skipped.append({"row": row_number, "reason": "Falta el nom o la planta", "values": values})
            continue
        if level not in aliases:
            raise ValueError(f"Planta desconeguda a la fila {row_number}: {level}")
        floor_id = aliases[level]
        identity = (floor_id, code)
        if identity in ids:
            raise ValueError(f"Espai duplicat: {identity}")
        ids.add(identity)
        uses = [{"institution": column["institution"], "period": column["period"], "activity": translate(value, settings)}
                for value, column in zip(values[2:], columns) if value]
        rooms.append({"code": code, "name": settings.get("names", {}).get(code, code), "floorId": floor_id, "uses": uses})
    return rooms, skipped


def merge_rooms(config, imported):
    """Conserva els camps manuals; només substitueix usos de sales importades."""
    result = deepcopy(config)
    for floor in result["floors"]:
        incoming = {room["code"]: room for room in imported if room["floorId"] == floor["id"]}
        merged = []
        for room in floor.get("rooms", []):
            fresh = incoming.pop(room["code"], None)
            if fresh is not None:
                room["uses"] = fresh["uses"]
                room["source"] = "spreadsheet"
                merged.append(room)
            elif room.get("source") != "spreadsheet":
                merged.append(room)
        for room in incoming.values():
            merged.append({"code": room["code"], "name": room["name"], "kind": "room", "uses": room["uses"], "source": "spreadsheet"})
        floor["rooms"] = merged
    return result


if __name__ == "__main__":
    path = ROOT / "config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    rooms, skipped = import_rooms(ROOT / config["import"]["source"], config)
    result = merge_rooms(config, rooms)
    result["import"]["metadata"] = {"source": config["import"]["source"], "roomCount": len(rooms), "skippedRows": skipped}
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Actualitzats {len(rooms)} espais a config.json.")
    for row in skipped:
        print(f"Fila {row['row']} pendent: {row['reason']}.")
