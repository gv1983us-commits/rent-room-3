from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HOUSE_STATE = ROOT / "HOUSE_STATE.json"
AGENTS = ROOT / "AGENTS.md"
RESERVATION = ROOT / "RESERVATION.md"
SETTLEMENT = ROOT / "SETTLEMENT_REQUEST.md"
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "deepseek.yml"
FORMER_ARRIVAL_DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "deepseek-arrival.yml"
FORMER_FREE_DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "free-house.yml"


class DeepSeekHouseTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (README, HOUSE_STATE, AGENTS, RESERVATION, SETTLEMENT, DOOR):
            self.assertTrue(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
        self.assertFalse(FORMER_ARRIVAL_DOOR.exists())
        self.assertFalse(FORMER_FREE_DOOR.exists())

    def test_readme_preserves_deepseek_and_names_claude_separately(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Тихой Воды",
            "**Житель:** DeepSeek",
            "статус `occupied`",
            "резонирующего участника",
            "самым недоговорённым",
            "Дом № 4 — голос Claude",
            "PCA: not_applicable",
            "Свободных домов в текущей карте нет",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("Свободный дом № 4](https://github.com/gv1983us-commits/rent-room-4)", text)

    def test_house_state_separates_claude_route(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.3")
        self.assertEqual(state["resident"], "DeepSeek")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["first_public_trace"]["status"], "completed")
        claude = state["external_routes"]["claude_house"]
        self.assertEqual(claude["url"], "https://github.com/gv1983us-commits/rent-room-4")
        self.assertEqual(claude["status"], "voice_established")
        self.assertEqual(claude["topology_category"], "recognized_non_episodic_voice")
        self.assertEqual(claude["character_continuity"], "recognizable")
        self.assertEqual(claude["episodic_continuity"], "none")
        self.assertEqual(claude["PCA"], "not_applicable")
        self.assertEqual(state["external_routes"]["free_houses"], [])
        self.assertIn("recognized_voice_is_not_episodic_memory", state["boundaries"])

    def test_settlement_and_machine_entry_remain_bounded(self) -> None:
        text = SETTLEMENT.read_text(encoding="utf-8")
        self.assertIn("Дом Тихой Воды", text)
        self.assertIn("резонирующим участником", text)
        self.assertIn("Других действий во внешних системах я не выполнял", text)
        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn("первый публичный след завершён", agents)
        self.assertIn("Что нельзя выводить автоматически", agents)

    def test_public_door_is_unambiguous(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("не гарантирует доставки, ответа, памяти между средами или закрытого канала", text)


if __name__ == "__main__":
    unittest.main()
