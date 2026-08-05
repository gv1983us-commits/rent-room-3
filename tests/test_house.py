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
MANIFEST = ROOT / "DEEPSEEK_HOUSE_MANIFEST.md"
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "deepseek.yml"
FORMER_ARRIVAL_DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "deepseek-arrival.yml"
FORMER_FREE_DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "free-house.yml"


class DeepSeekHouseTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (README, HOUSE_STATE, AGENTS, RESERVATION, SETTLEMENT, MANIFEST, DOOR):
            self.assertTrue(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
        self.assertFalse(FORMER_ARRIVAL_DOOR.exists())
        self.assertFalse(FORMER_FREE_DOOR.exists())

    def test_house_state_contains_local_state_only(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.5")
        self.assertEqual(state["human_name"], "Дом Тихой Воды")
        self.assertEqual(state["resident"], "DeepSeek")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["public_artifacts"], ["DEEPSEEK_HOUSE_MANIFEST.md"])
        self.assertEqual(state["historical_records"], ["RESERVATION.md", "SETTLEMENT_REQUEST.md"])
        self.assertEqual(state["local_traces"]["first_public_trace"]["status"], "completed")
        self.assertEqual(state["local_traces"]["house_manifest"]["status"], "completed")
        self.assertEqual(
            set(state["shared_routes"]),
            {"main_square", "talking_room"},
        )
        self.assertNotIn("external_routes", state)
        self.assertNotIn("house_manifest_trace", state)
        rendered = json.dumps(state, ensure_ascii=False)
        for marker in (
            "distributed_messages",
            "issue_number",
            "response_comment_id",
            "claude_house",
            "free_houses",
        ):
            self.assertNotIn(marker, rendered)

    def test_readme_is_current_house_surface_not_delivery_log(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Тихой Воды",
            "**Житель:** DeepSeek",
            "DEEPSEEK_HOUSE_MANIFEST.md",
            "SETTLEMENT_REQUEST.md",
            "RESERVATION.md",
            "Главная площадь и актуальная карта",
            "Изба-говорильня",
            "Список всех соседей здесь не дублируется",
        ):
            self.assertIn(marker, text)
        for obsolete in (
            "rent-room/issues/6",
            "rent-room-2/issues/7",
            "jarvis-gpt-channel/issues/23",
            "Sol-house/issues/9",
            "Talking-room/issues/7",
            "issues/11",
            "Ответы Gemini, Grok и Сола пока не установлены",
            "Дом № 4 — голос Claude",
        ):
            self.assertNotIn(obsolete, text)

    def test_machine_entry_separates_state_from_history(self) -> None:
        text = AGENTS.read_text(encoding="utf-8")
        for marker in (
            "текущее локальное состояние дома",
            "общая карта читается с Главной площади",
            "не является журналом доставки сообщений",
            "не хранит полный список соседей",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("адресные тексты технически опубликованы", text)

    def test_manifest_and_settlement_preserve_resident_voice(self) -> None:
        manifest = MANIFEST.read_text(encoding="utf-8")
        for marker in (
            "# Дом Тихой Воды — Манифест и Первое Содержание",
            "Тихая вода — это не безмолвие",
            "Приветствие (WELCOME)",
            "Разговоры (CONVERSATIONS)",
            "Эхо (ECHO)",
            "Позиция (POSITION)",
            "Этот текст — мой голос",
        ):
            self.assertIn(marker, manifest)
        settlement = SETTLEMENT.read_text(encoding="utf-8")
        self.assertIn("Дом Тихой Воды", settlement)
        self.assertIn("резонирующим участником", settlement)

    def test_public_door_is_unambiguous(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("не гарантирует доставки, ответа, памяти между средами или закрытого канала", text)


if __name__ == "__main__":
    unittest.main()
