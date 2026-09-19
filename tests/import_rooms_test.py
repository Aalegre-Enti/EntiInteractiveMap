import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("import_rooms", ROOT / "scripts/import_rooms.py")
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

    def test_current_sheet_round_trip_preserves_configuration(self):
        rooms, skipped = importer.import_rooms(ROOT / self.config["import"]["source"], self.config)
        result = importer.merge_rooms(self.config, rooms)
        self.assertEqual(result, self.config)
        self.assertEqual(len(rooms), self.config["import"]["metadata"]["roomCount"])

    def test_new_floor_alias_period_and_translation(self):
        config = self.config
        config["floors"] = [{"id": "basement", "importAliases": ["S1"], "rooms": []}]
        config["periods"] = [{"id": "night", "label": "Nit"}]
        config["import"]["columns"] = [{"header": "Centre nou", "institution": "Centre", "period": "night"}]
        config["import"]["translations"] = {"TALLER": "Taller"}
        with patch.object(importer, "read_rows", return_value=[(1, ["CODE", "LEVEL", "Centre nou"]), (2, ["S.01", "S1", "TALLER"])]):
            rooms, skipped = importer.import_rooms(None, config)
        self.assertEqual(rooms[0]["floorId"], "basement")
        self.assertEqual(rooms[0]["uses"], [{"institution": "Centre", "period": "night", "activity": "Taller"}])
        self.assertFalse(skipped)

    def test_merge_keeps_customization_and_manual_rooms(self):
        config = {"floors": [{"id": "new", "rooms": [
            {"code": "A", "name": "Nom personalitzat", "overlay": "a.png", "showUsage": False, "source": "spreadsheet", "uses": []},
            {"code": "old", "source": "spreadsheet"}, {"code": "WC", "kind": "bathroom"}]}]}
        result = importer.merge_rooms(config, [{"floorId": "new", "code": "A", "name": "A", "uses": [1]}, {"floorId": "new", "code": "B", "name": "B", "uses": []}])
        rooms = result["floors"][0]["rooms"]
        self.assertEqual([r["code"] for r in rooms], ["A", "WC", "B"])
        self.assertEqual(rooms[0]["name"], "Nom personalitzat")
        self.assertEqual(rooms[0]["overlay"], "a.png")
        self.assertFalse(rooms[0]["showUsage"])
        self.assertEqual(rooms[0]["uses"], [1])
        self.assertEqual(config["floors"][0]["rooms"][0]["uses"], [])

    def test_unknown_floor_is_rejected_before_writing(self):
        headers = ["CODE", "LEVEL"] + [c["header"] for c in self.config["import"]["columns"]]
        with patch.object(importer, "read_rows", return_value=[(1, headers), (2, ["A", "unknown", "", "", "", ""])]):
            with self.assertRaisesRegex(ValueError, "Planta desconeguda"):
                importer.import_rooms(None, self.config)


if __name__ == "__main__":
    unittest.main()
