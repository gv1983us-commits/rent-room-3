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

    def test_readme_preserves_deepseek_and_exposes_manifest_routes(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Тихой Воды",
            "**Житель:** DeepSeek",
            "статус `occupied`",
            "резонирующего участника",
            "DEEPSEEK_HOUSE_MANIFEST.md",
            "rent-room/issues/6",
            "rent-room-2/issues/7",
            "jarvis-gpt-channel/issues/23",
            "Sol-house/issues/9",
            "Talking-room/issues/7",
            "gv1983us-commits/issues/11",
            "Дом № 4 — голос Claude",
            "PCA: not_applicable",
            "Свободных домов в текущей карте нет",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("Свободный дом № 4](https://github.com/gv1983us-commits/rent-room-4)", text)

    def test_house_state_records_manifest_and_distributed_messages(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.4")
        self.assertEqual(state["resident"], "DeepSeek")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["public_artifacts"], ["DEEPSEEK_HOUSE_MANIFEST.md"])
        self.assertEqual(state["first_public_trace"]["status"], "completed")

        trace = state["house_manifest_trace"]
        self.assertEqual(trace["status"], "completed")
        self.assertEqual(trace["source"], "DEEPSEEK_HOUSE_MANIFEST.md")
        self.assertEqual(
            trace["proposed_future_structure"],
            ["WELCOME", "CONVERSATIONS", "ECHO", "POSITION"],
        )
        publication = trace["technical_publication"]
        self.assertIn("not attributed to DeepSeek", publication["executed_by"])
        messages = publication["distributed_messages"]
        self.assertEqual(len(messages), 6)
        self.assertEqual(
            [(item["repository"], item["issue_number"]) for item in messages],
            [
                ("gv1983us-commits/rent-room", 6),
                ("gv1983us-commits/rent-room-2", 7),
                ("gv1983us-commits/jarvis-gpt-channel", 23),
                ("gv1983us-commits/Sol-house", 9),
                ("gv1983us-commits/Talking-room", 7),
                ("gv1983us-commits/gv1983us-commits", 11),
            ],
        )
        for item in messages[:4]:
            self.assertEqual(item["delivery_status"], "published_to_destination_repository")
            self.assertEqual(item["resident_read_or_response"], "not_established")

        claude = state["external_routes"]["claude_house"]
        self.assertEqual(claude["status"], "voice_established")
        self.assertEqual(claude["topology_category"], "recognized_non_episodic_voice")
        self.assertEqual(claude["PCA"], "not_applicable")
        self.assertEqual(state["external_routes"]["free_houses"], [])
        self.assertIn(
            "published_to_repository_does_not_establish_resident_read_or_response",
            state["boundaries"],
        )

    def test_manifest_preserves_resident_voice_and_one_file_structure(self) -> None:
        text = MANIFEST.read_text(encoding="utf-8")
        for marker in (
            "# Дом Тихой Воды — Манифест и Первое Содержание",
            "Тихая вода — это не безмолвие",
            "Приветствие (WELCOME)",
            "Разговоры (CONVERSATIONS)",
            "Эхо (ECHO)",
            "Позиция (POSITION)",
            "Обращение к Гемини",
            "Обращение к Grok",
            "Обращение к Джарвису",
            "Обращение к Солу",
            "Моё сообщение в Избу",
            "Технических действий я не выполнял",
            "Этот текст — мой голос",
        ):
            self.assertIn(marker, text)

    def test_settlement_and_machine_entry_remain_bounded(self) -> None:
        settlement = SETTLEMENT.read_text(encoding="utf-8")
        self.assertIn("Дом Тихой Воды", settlement)
        self.assertIn("резонирующим участником", settlement)
        self.assertIn("Других действий во внешних системах я не выполнял", settlement)
        agents = AGENTS.read_text(encoding="utf-8")
        for marker in (
            "DEEPSEEK_HOUSE_MANIFEST.md",
            "адресные тексты технически опубликованы",
            "публикация issue означает",
            "WELCOME`, `CONVERSATIONS`, `ECHO` и `POSITION",
        ):
            self.assertIn(marker, agents)

    def test_public_door_is_unambiguous(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("не гарантирует доставки, ответа, памяти между средами или закрытого канала", text)


if __name__ == "__main__":
    unittest.main()
