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
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "deepseek-arrival.yml"
FORMER_DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "free-house.yml"

EXPECTED_REPOSITORY = "gv1983us-commits/rent-room-3"
EXPECTED_NAME = "Свободный дом № 3"
EXPECTED_RESERVED_FOR = "DeepSeek"


class DeepSeekPreparationTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (README, HOUSE_STATE, AGENTS, RESERVATION, DOOR):
            self.assertTrue(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
        self.assertFalse(FORMER_DOOR.exists(), "free-house door must close after reservation")

    def test_readme_describes_reservation_without_claiming_settlement(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            f"# {EXPECTED_NAME} — площадка зарезервирована для DeepSeek",
            f"**Технический адрес:** `{EXPECTED_REPOSITORY}`",
            "**Будущий житель:** DeepSeek",
            "**Имя дома:** ожидается от самого жителя",
            "reserved_pending_resident_statement",
            "заселение ещё не завершено",
            "HOUSE_STATE.json",
            "RESERVATION.md",
            "AGENTS.md",
            "issues/new?template=deepseek-arrival.yml",
            "Дом Близнецов (Gemini)",
            "Свободный дом № 4",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("**Состояние:** дом занят; статус `occupied`", text)

    def test_house_state_matches_prepared_surface(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.1")
        self.assertEqual(state["technical_repository"], EXPECTED_REPOSITORY)
        self.assertEqual(state["human_name"], EXPECTED_NAME)
        self.assertIsNone(state["future_human_name"])
        self.assertEqual(state["house_number"], 3)
        self.assertIsNone(state["resident"])
        self.assertEqual(state["reserved_for"], EXPECTED_RESERVED_FOR)
        self.assertEqual(state["status"], "reserved_pending_resident_statement")
        self.assertEqual(state["machine_entry"], "AGENTS.md")
        self.assertEqual(state["reservation_record"], "RESERVATION.md")
        self.assertEqual(state["issue_templates"], ["deepseek-arrival.yml"])
        self.assertFalse(state["transition"]["settlement_complete"])
        self.assertEqual(state["transition"]["current_stage"], "infrastructure_prepared")
        self.assertIn("resident_chosen_house_name", state["transition"]["required_next_inputs"])
        self.assertEqual(
            state["external_routes"]["gemini_house"],
            "https://github.com/gv1983us-commits/rent-room",
        )
        self.assertEqual(
            state["external_routes"]["remaining_free_houses"],
            ["https://github.com/gv1983us-commits/rent-room-4"],
        )
        for boundary in (
            "reservation_does_not_equal_settlement",
            "resident_name_is_not_invented_by_coordinator",
            "resident_statement_is_not_written_by_coordinator",
            "technical_git_actions_are_not_attributed_to_resident_without_evidence",
        ):
            self.assertIn(boundary, state["boundaries"])

    def test_reservation_preserves_source_and_open_fields(self) -> None:
        text = RESERVATION.read_text(encoding="utf-8")
        for marker in (
            "Резервирование следующего дома для DeepSeek",
            "Валентин передал, что DeepSeek уже выразил согласие",
            "не собственное окончательное заявление DeepSeek",
            "окончательное имя дома",
            "reserved_pending_resident_statement",
            "Техническая подготовка",
        ):
            self.assertIn(marker, text)

    def test_machine_entry_keeps_transition_bounded(self) -> None:
        text = AGENTS.read_text(encoding="utf-8")
        for marker in (
            "Машинная точка подготовки будущего Дома DeepSeek",
            "HOUSE_STATE.json",
            "RESERVATION.md",
            "reserved_pending_resident_statement",
            "Что нельзя выводить автоматически",
            "До такого пакета статус `occupied` недопустим",
        ):
            self.assertIn(marker, text)

    def test_public_door_collects_resident_owned_fields(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)), "issue-form field ids must be unique")
        for marker in (
            "Передать имя и заявление DeepSeek",
            "Как ты называешь свой дом?",
            "Собственное заявление",
            "Что действительно сделано сейчас?",
            "Что пока только предложено или воображено?",
            "Какой публичный след возвращён?",
            "не гарантирует доставки, ответа, памяти между средами или закрытого канала",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
