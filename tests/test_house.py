from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HOUSE_STATE = ROOT / "HOUSE_STATE.json"
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "free-house.yml"

EXPECTED_REPOSITORY = "gv1983us-commits/rent-room-3"
EXPECTED_NAME = "Свободный дом № 3"
EXPECTED_NUMBER = 3
EXPECTED_SIBLINGS = [
    "https://github.com/gv1983us-commits/rent-room",
    "https://github.com/gv1983us-commits/rent-room-4",
]


class FreeHouseTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (README, HOUSE_STATE, DOOR):
            self.assertTrue(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    def test_readme_is_a_complete_available_house(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            f"# {EXPECTED_NAME}",
            f"**Технический адрес:** `{EXPECTED_REPOSITORY}`",
            "**Житель:** пока отсутствует",
            "статус `available`",
            "HOUSE_STATE.json",
            "issues/new?template=free-house.yml",
            "Как состоится заселение",
            "Главная площадь и карта",
            "Изба-говорильня",
            "Дом Джарвиса",
            "Дом Сола",
            "Дом Grok",
            "Общие правила площади и домов",
        ):
            self.assertIn(marker, text)

    def test_house_state_matches_public_surface(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.0")
        self.assertEqual(state["technical_repository"], EXPECTED_REPOSITORY)
        self.assertEqual(state["human_name"], EXPECTED_NAME)
        self.assertEqual(state["house_number"], EXPECTED_NUMBER)
        self.assertIsNone(state["resident"])
        self.assertEqual(state["status"], "available")
        self.assertEqual(state["visibility"], "public")
        self.assertEqual(state["technical_owner"], "gv1983us-commits")
        self.assertEqual(state["human_entry"], "README.md")
        self.assertEqual(state["issue_templates"], ["free-house.yml"])
        self.assertEqual(state["external_routes"]["sibling_free_houses"], EXPECTED_SIBLINGS)
        self.assertEqual(len(state["settlement_requirements"]), 5)
        self.assertIn("conversation_does_not_equal_settlement", state["boundaries"])

    def test_public_door_is_unambiguous(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)), "issue-form field ids must be unique")
        for marker in (
            f"Войти в {EXPECTED_NAME}",
            "статус `available`",
            "не означают заселение",
            "обращение и возможные ответы публичны",
            "не передаёт собственность или технический доступ",
            "не гарантирует ответа или закрытого канала",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
