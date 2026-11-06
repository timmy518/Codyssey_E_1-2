"""(보충) Quiz 클래스와 기본 퀴즈 데이터 테스트."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from default_quizzes import get_default_quizzes  # noqa: E402
from quiz import Quiz  # noqa: E402


class QuizTest(unittest.TestCase):
    def test_to_dict_and_from_dict(self):
        quiz = Quiz("Q?", ["a", "b", "c", "d"], 3, "힌트")
        self.assertEqual(quiz.to_dict(), {"question": "Q?", "choices": ["a", "b", "c", "d"], "answer": 3, "hint": "힌트"})
        self.assertEqual(Quiz.from_dict(quiz.to_dict()).to_dict(), quiz.to_dict())

    def test_hint_is_optional_in_data(self):
        quiz = Quiz.from_dict({"question": "Q", "choices": ["a", "b", "c", "d"], "answer": 1})
        self.assertEqual(quiz.hint, "")
        self.assertFalse(quiz.has_hint())

    def test_is_correct_and_display(self):
        quiz = Quiz("Q?", ["a", "b", "c", "d"], 3)
        self.assertTrue(quiz.is_correct(3))
        self.assertFalse(quiz.is_correct(1))
        out = io.StringIO()
        with redirect_stdout(out):
            quiz.display(2)
        for text in ("[문제 2]", "Q?", "1. a", "4. d"):
            self.assertIn(text, out.getvalue())

    def test_from_dict_rejects_bad_data(self):
        good = {"question": "Q", "choices": ["a", "b", "c", "d"], "answer": 1}
        bad_cases = [
            {"choices": ["a", "b", "c", "d"], "answer": 1},
            {**good, "question": ""},
            {**good, "choices": ["a", "b", "c"]},
            {**good, "choices": ["a", "", "c", "d"]},
            {**good, "answer": 0},
            {**good, "answer": 5},
            {**good, "answer": "1"},
            {**good, "answer": True},
            {**good, "hint": 3},
            "문자열",
            None,
        ]
        for data in bad_cases:
            with self.subTest(data=data):
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    Quiz.from_dict(data)


class DefaultQuizzesTest(unittest.TestCase):
    def test_at_least_five_quiz_instances(self):
        quizzes = get_default_quizzes()
        self.assertGreaterEqual(len(quizzes), 5)
        for quiz in quizzes:
            self.assertIsInstance(quiz, Quiz)
            self.assertEqual(len(quiz.choices), 4)
            self.assertIn(quiz.answer, (1, 2, 3, 4))
            self.assertTrue(quiz.has_hint())


if __name__ == "__main__":
    unittest.main()
