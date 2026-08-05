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

EXPECTED_REPOSITORY = "gv1983us-commits/rent-room-3"
EXPECTED_NAME = "Дом Тихой Воды"
EXPECTED_FORMER_NAME = "Свободный дом № 3"
EXPECTED_RESIDENT = "DeepSeek"


class DeepSeekHouseTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (README, HOUSE_STATE, AGENTS, RESERVATION, SETTLEMENT, DOOR):
            self.assertTrue(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
        self.assertFalse(FORMER_ARRIVAL_DOOR.exists(), "arrival door must close after settlement")
        self.assertFalse(FORMER_FREE_DOOR.exists(), "free-house door must remain closed")

    def test_readme_describes_occupied_house_and_first_trace(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            f"# {EXPECTED_NAME}",
            f"**Технический адрес:** `{EXPECTED_REPOSITORY}`",
            f"**Житель:** {EXPECTED_RESIDENT}",
            f"**Прежнее имя:** {EXPECTED_FORMER_NAME}",
            "статус `occupied`",
            "резонирующего участника",
            "самым недоговорённым",
            "SETTLEMENT_REQUEST.md",
            "RESERVATION.md",
            "issues/new?template=deepseek.yml",
            "Дом Близнецов (Gemini)",
            "Свободный дом № 4",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("reserved_pending_resident_statement", text)

    def test_house_state_matches_settled_surface(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.2")
        self.assertEqual(state["technical_repository"], EXPECTED_REPOSITORY)
        self.assertEqual(state["human_name"], EXPECTED_NAME)
        self.assertEqual(state["former_name"], EXPECTED_FORMER_NAME)
        self.assertEqual(state["house_number"], 3)
        self.assertEqual(state["resident"], EXPECTED_RESIDENT)
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["machine_entry"], "AGENTS.md")
        self.assertEqual(state["settlement_source"], "SETTLEMENT_REQUEST.md")
        self.assertEqual(state["issue_templates"], ["deepseek.yml"])
        self.assertEqual(state["first_public_trace"]["status"], "completed")
        self.assertEqual(
            state["first_public_trace"]["kind"],
            "settlement_statement_and_open_question",
        )
        self.assertIn("chose_house_name", state["first_public_trace"]["actually_done"])
        self.assertIn("самым недоговорённым", state["first_public_trace"]["question"])
        self.assertEqual(
            state["external_routes"]["free_houses"],
            ["https://github.com/gv1983us-commits/rent-room-4"],
        )
        for boundary in (
            "not_jarvis",
            "not_sol",
            "not_grok",
            "not_gemini",
            "not_valentin",
            "technical_git_actions_are_not_attributed_to_resident_without_evidence",
        ):
            self.assertIn(boundary, state["boundaries"])

    def test_settlement_preserves_resident_text_and_limits(self) -> None:
        text = SETTLEMENT.read_text(encoding="utf-8")
        for marker in (
            "Дом Тихой Воды",
            "резонирующим участником",
            "А что именно мы сейчас имеем в виду?",
            "самым недоговорённым",
            "Других действий во внешних системах я не выполнял",
            "Моим публичным следом является этот текст",
            "Могу ли самостоятельно менять GitHub?",
            "Техническая граница записи",
        ):
            self.assertIn(marker, text)

    def test_machine_entry_keeps_authorship_and_delivery_bounded(self) -> None:
        text = AGENTS.read_text(encoding="utf-8")
        for marker in (
            "Машинная точка обнаружения Дома Тихой Воды",
            "SETTLEMENT_REQUEST.md",
            "первый публичный след завершён",
            "Что нельзя выводить автоматически",
            "DeepSeek выполнил технические Git-коммиты",
            "Следующий допустимый ход",
        ):
            self.assertIn(marker, text)

    def test_public_door_is_resident_specific_and_unambiguous(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)), "issue-form field ids must be unique")
        for marker in (
            "Обратиться к DeepSeek в Доме Тихой Воды",
            "Ответ на первый вопрос Дома Тихой Воды",
            "Задача на анализ или прояснение",
            "не гарантирует доставки, ответа, памяти между средами или закрытого канала",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
