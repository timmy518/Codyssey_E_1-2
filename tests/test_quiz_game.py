"""(보충) QuizGame 테스트. input() 을 정해 둔 입력으로 바꿔 실제 사용 흐름을 재현한다."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from default_quizzes import get_default_quizzes  # noqa: E402
from quiz import Quiz  # noqa: E402
from quiz_game import QuizGame  # noqa: E402

ANSWERS = [quiz.answer for quiz in get_default_quizzes()]
N = len(ANSWERS)


def run_inputs(func, inputs):
    """inputs 를 차례대로 입력한 것처럼 func 를 실행하고 화면 출력을 돌려준다."""
    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(inputs)), redirect_stdout(out):
        func()
    return out.getvalue()


def in_order(population, k):
    """random.sample 대신 사용: 섞지 않고 앞에서부터 k 개 (결과를 예측하기 위해)."""
    return list(population)[:k]


def wrong(answer):
    return str(answer % 4 + 1)


class GameTestBase(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.path = Path(temp_dir.name) / "state.json"
        patcher = mock.patch("random.sample", side_effect=in_order)
        patcher.start()
        self.addCleanup(patcher.stop)

    def loaded_game(self, quizzes=None, best=None, history=None):
        game = QuizGame(self.path)
        game.quizzes = get_default_quizzes() if quizzes is None else quizzes
        game.best_score = best
        game.history = [] if history is None else history
        game.is_loaded = True
        return game

    def saved(self):
        return json.loads(self.path.read_text(encoding="utf-8"))


class InputTest(GameTestBase):
    def test_ask_number(self):
        out = io.StringIO()
        with mock.patch("builtins.input", side_effect=["", "abc", "9", "  3  "]), redirect_stdout(out):
            self.assertEqual(QuizGame(self.path).ask_number("선택: ", 1, 6), 3)
        self.assertEqual(out.getvalue().count("입력값이 없습니다. 1-6 사이의 숫자를 입력하세요."), 1)
        self.assertEqual(out.getvalue().count("잘못된 입력입니다. 1-6 사이의 숫자를 입력하세요."), 2)

    def test_ask_text(self):
        out = io.StringIO()
        with mock.patch("builtins.input", side_effect=["", "   ", "  내용  "]), redirect_stdout(out):
            self.assertEqual(QuizGame(self.path).ask_text("입력: "), "내용")
        self.assertEqual(out.getvalue().count("입력값이 없습니다. 내용을 입력하세요."), 2)


class MenuTest(GameTestBase):
    def test_first_run_and_quit(self):
        out = run_inputs(QuizGame(self.path).run, ["6"])
        self.assertNotIn("저장된 데이터를 불러왔습니다", out)  # 파일이 없으면 기본 퀴즈로 바로 시작
        for number, name in enumerate(["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "퀴즈 삭제", "종료"], start=1):
            self.assertIn(f"{number}. {name}", out)
        self.assertIn("게임을 종료합니다.", out)
        self.assertEqual(self.saved(), {"quizzes": [q.to_dict() for q in get_default_quizzes()],
                                        "best_score": None, "history": []})

    def test_invalid_menu_inputs(self):
        out = run_inputs(QuizGame(self.path).run, ["abc", "9", "", "0", "   ", " 6 "])
        self.assertEqual(out.count("1-6 사이의 숫자를 입력하세요."), 5)
        self.assertIn("게임을 종료합니다.", out)


class PlayTest(GameTestBase):
    def test_play_all_correct(self):
        game = self.loaded_game()
        out = run_inputs(game.play, [str(N)] + [str(a) for a in ANSWERS])
        self.assertIn(f"퀴즈를 시작합니다! (총 {N}문제)", out)
        self.assertEqual(out.count("정답입니다!"), N)
        self.assertIn(f"결과: {N}문제 중 {N}문제 정답! (100점)", out)
        self.assertIn("새로운 최고 점수입니다!", out)
        data = self.saved()
        self.assertEqual(data["best_score"], 100)
        self.assertEqual(len(data["history"]), 1)
        self.assertEqual(set(data["history"][0]), {"played_at", "total", "score"})
        self.assertEqual((data["history"][0]["total"], data["history"][0]["score"]), (N, 100))

    def test_count_and_answer_validation(self):
        game = self.loaded_game()
        inputs = ["0", str(N + 1), "x", "", "2", "abc", "", "0", "5", str(ANSWERS[0]), wrong(ANSWERS[1])]
        out = run_inputs(game.play, inputs)
        self.assertEqual(out.count(f"1-{N} 사이의 숫자를 입력하세요."), 4)
        self.assertEqual(out.count("1-4 사이의 숫자를 입력하세요."), 4)
        self.assertIn("퀴즈를 시작합니다! (총 2문제)", out)
        self.assertEqual(out.count("오답입니다."), 1)
        self.assertIn("2문제 중 1문제 정답! (50점)", out)

    def test_random_sample_is_used(self):
        with mock.patch("random.sample", side_effect=lambda pop, k: list(reversed(pop))[:k]) as sample:
            game = self.loaded_game()
            out = run_inputs(game.play, ["1", str(ANSWERS[-1])])
        sample.assert_called_once()
        self.assertIn(game.quizzes[-1].question, out)

    def test_hint_halves_points(self):
        game = self.loaded_game()
        out = run_inputs(game.play, ["2", "h", str(ANSWERS[0]), "H", str(ANSWERS[1])])
        self.assertIn(f"힌트: {game.quizzes[0].hint}", out)
        self.assertIn("2문제 중 2문제 정답! (50점)", out)  # (0.5 + 0.5) / 2 * 100

    def test_score_is_floored(self):
        game = self.loaded_game()
        out = run_inputs(game.play, ["3", str(ANSWERS[0]), str(ANSWERS[1]), "h", str(ANSWERS[2])])
        self.assertIn("3문제 중 3문제 정답! (83점)", out)  # 2.5 / 3 * 100 = 83.3 -> 83

    def test_single_quiz_without_hint(self):
        game = self.loaded_game(quizzes=[Quiz("Q?", ["a", "b", "c", "d"], 2)])
        fake_input = mock.Mock(side_effect=["1", "h", "2"])
        out = io.StringIO()
        with mock.patch("builtins.input", fake_input), redirect_stdout(out):
            game.play()
        prompts = [c.args[0] for c in fake_input.call_args_list]
        self.assertEqual(prompts[0], "\n몇 문제를 풀까요? (1-1): ")  # 퀴즈가 1개여도 문제 수를 묻는다.
        self.assertEqual(prompts[1], "정답 입력: ")                   # 힌트가 없으면 h 안내도 없다.
        self.assertIn("잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.", out.getvalue())
        self.assertIn("(100점)", out.getvalue())

    def test_best_score_only_increases(self):
        game = self.loaded_game(best=90, history=[{"played_at": "2026-11-04 10:00:00", "total": 5, "score": 90}])
        out = run_inputs(game.play, ["1", wrong(ANSWERS[0])])
        self.assertNotIn("새로운 최고 점수", out)
        self.assertEqual(self.saved()["best_score"], 90)
        self.assertEqual([record["score"] for record in self.saved()["history"]], [90, 0])

    def test_no_quizzes(self):
        game = self.loaded_game(quizzes=[])
        self.assertIn("등록된 퀴즈가 없습니다", run_inputs(game.play, []))


class AddListScoreDeleteTest(GameTestBase):
    def test_add_quiz(self):
        game = self.loaded_game()
        out = run_inputs(game.add_quiz, ["", "새 문제?", "", "가", "나", "다", "라", "0", "abc", "", "3", "  새 힌트  "])
        self.assertEqual(out.count("입력값이 없습니다. 내용을 입력하세요."), 2)
        self.assertEqual(out.count("1-4 사이의 숫자를 입력하세요."), 3)
        self.assertIn("퀴즈가 추가되었습니다!", out)
        self.assertEqual(self.saved()["quizzes"][-1],
                         {"question": "새 문제?", "choices": ["가", "나", "다", "라"], "answer": 3, "hint": "새 힌트"})

    def test_list(self):
        out = run_inputs(self.loaded_game().list_quizzes, [])
        self.assertIn(f"등록된 퀴즈 목록 (총 {N}개)", out)
        self.assertIn(f"[1] {get_default_quizzes()[0].question}", out)
        self.assertIn("등록된 퀴즈가 없습니다", run_inputs(self.loaded_game(quizzes=[]).list_quizzes, []))

    def test_score(self):
        self.assertIn("아직 퀴즈를 풀지 않았습니다", run_inputs(self.loaded_game().show_score, []))
        history = [{"played_at": "2026-11-04 10:00:00", "total": 5, "score": 80}]
        out = run_inputs(self.loaded_game(best=80, history=history).show_score, [])
        self.assertIn("최고 점수: 80점", out)
        self.assertIn("게임 기록 (총 1회)", out)
        self.assertIn("2026-11-04 10:00:00 | 5문제 | 80점", out)

    def test_delete_quiz(self):
        game = self.loaded_game()
        out = run_inputs(game.delete_quiz, ["0", str(N + 1), "abc", "", "2"])
        self.assertEqual(out.count(f"1-{N} 사이의 숫자를 입력하세요."), 4)
        self.assertIn("퀴즈를 삭제했습니다:", out)
        saved_questions = [quiz["question"] for quiz in self.saved()["quizzes"]]
        self.assertEqual(len(saved_questions), N - 1)
        self.assertNotIn(get_default_quizzes()[1].question, saved_questions)

    def test_delete_when_empty(self):
        self.assertIn("삭제할 퀴즈가 없습니다", run_inputs(self.loaded_game(quizzes=[]).delete_quiz, []))


class DataFileTest(GameTestBase):
    def test_restart_keeps_data(self):
        inputs = ["2", "한글 문제?", "가", "나", "다", "라", "1", "", "1", "1", str(ANSWERS[0]), "6"]
        run_inputs(QuizGame(self.path).run, inputs)
        out = run_inputs(QuizGame(self.path).run, ["3", "4", "6"])
        self.assertIn(f"저장된 데이터를 불러왔습니다. (퀴즈 {N + 1}개, 최고점수 100점)", out)
        self.assertIn(f"[{N + 1}] 한글 문제?", out)
        self.assertIn("게임 기록 (총 1회)", out)
        self.assertIn("한글 문제?", self.path.read_bytes().decode("utf-8"))  # UTF-8 로 한글 그대로 저장

    def test_mission_example_schema_loads(self):
        example = {"quizzes": [{"question": "Python의 창시자는?", "choices": ["Guido", "Linus", "Bjarne", "James"],
                                "answer": 1}], "best_score": 3}
        self.path.write_text(json.dumps(example, ensure_ascii=False), encoding="utf-8")
        out = run_inputs(QuizGame(self.path).run, ["6"])
        self.assertIn("저장된 데이터를 불러왔습니다. (퀴즈 1개, 최고점수 3점)", out)

    def test_corrupted_file_is_backed_up_and_restored(self):
        quiz = {"question": "Q", "choices": ["a", "b", "c", "d"], "answer": 1}
        cases = {
            "깨진 JSON": b'{"quizzes": [',
            "빈 파일": b"",
            "최상위가 목록": b"[1, 2]",
            "quizzes 없음": b'{"best_score": 3}',
            "quizzes 가 목록이 아님": b'{"quizzes": {}}',
            "quizzes 가 빈 문자열": b'{"quizzes": ""}',
            "너무 깊은 중첩": b'{"quizzes": ' + b"[" * 100_000,
            "잘못된 퀴즈": json.dumps({"quizzes": [{"question": "x"}]}).encode(),
            "잘못된 최고 점수": json.dumps({"quizzes": [quiz], "best_score": "80"}).encode(),
            "잘못된 게임 기록": json.dumps({"quizzes": [quiz], "history": [{"played_at": "x"}]}).encode(),
            "UTF-8 아님": '{"quizzes": ["한글"]}'.encode("cp949"),
        }
        for name, content in cases.items():
            with self.subTest(name):
                self.path.write_bytes(content)
                out = run_inputs(QuizGame(self.path).run, ["6"])
                self.assertIn("데이터 파일이 손상되어 기본 퀴즈 데이터로 복구합니다.", out)
                self.assertIn("손상된 파일은 state.json.bak 으로 백업했습니다.", out)
                self.assertEqual(self.path.with_name("state.json.bak").read_bytes(), content)
                self.assertEqual(self.saved(), {"quizzes": [q.to_dict() for q in get_default_quizzes()],
                                                "best_score": None, "history": []})

    def test_backup_failure_is_reported(self):
        self.path.write_text("{broken", encoding="utf-8")
        self.path.with_name("state.json.bak").mkdir()  # 백업 자리에 폴더가 있어 복사할 수 없다.
        out = run_inputs(QuizGame(self.path).run, ["6"])
        self.assertIn("손상된 파일을 백업하지 못했습니다.", out)
        self.assertEqual(len(self.saved()["quizzes"]), N)

    def test_unsavable_text_is_reported(self):
        game = self.loaded_game(quizzes=[Quiz("\ud83d 깨진 글자", ["a", "b", "c", "d"], 1)])
        out = run_inputs(game.save_data, [])  # UTF-8 로 쓸 수 없는 글자가 있어도 멈추지 않는다.
        self.assertIn("데이터를 저장하지 못했습니다.", out)

    def test_failed_save_keeps_previous_file(self):
        # 원자적 저장: 쓰는 도중 실패해도 state.json 은 저장하기 전 그대로이고 임시 파일은 남지 않는다.
        self.path.with_name("state.json.tmp").write_text("{ 강제 종료로 남은 임시 파일", encoding="utf-8")
        game = self.loaded_game()
        run_inputs(game.save_data, [])
        # 남아 있던 임시 파일도 덮어써 state.json 으로 바뀌므로 state.json 하나만 남는다.
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["state.json"])
        before = self.path.read_bytes()
        game.quizzes.append(Quiz("\ud83d 깨진 글자", ["a", "b", "c", "d"], 1))  # 이 글자에서 쓰기가 실패한다.
        out = run_inputs(game.save_data, [])
        self.assertIn("데이터를 저장하지 못했습니다.", out)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(self.saved()["quizzes"]), N)
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["state.json"])

    def test_failed_replace_keeps_previous_file(self):
        # 원자적 저장: 바꿔치기(os.replace)가 실패해도 state.json 은 저장하기 전 그대로이고 임시 파일은 남지 않는다.
        game = self.loaded_game()
        run_inputs(game.save_data, [])
        before = self.path.read_bytes()
        game.quizzes.pop()
        with mock.patch("quiz_game.os.replace", side_effect=PermissionError("다른 프로그램이 사용 중")):
            out = run_inputs(game.save_data, [])
        self.assertIn("데이터를 저장하지 못했습니다.", out)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["state.json"])

    def test_unreadable_file(self):
        self.path.mkdir()  # state.json 자리에 폴더가 있으면 읽기/쓰기 모두 실패한다.
        out = run_inputs(QuizGame(self.path).run, ["6"])
        self.assertIn("데이터 파일을 읽을 수 없어 기본 퀴즈로 시작합니다.", out)
        self.assertIn("데이터를 저장하지 못했습니다.", out)
        self.assertIn("게임을 종료합니다.", out)


class InterruptTest(GameTestBase):
    def test_eof_at_menu(self):
        out = run_inputs(QuizGame(self.path).run, [EOFError()])
        self.assertIn("입력이 중단되어 프로그램을 종료합니다.", out)
        self.assertTrue(self.path.exists())

    def test_interrupt_during_add_does_not_save_partial_quiz(self):
        run_inputs(QuizGame(self.path).run, ["2", "중단 문제", "a", KeyboardInterrupt()])
        questions = [quiz["question"] for quiz in self.saved()["quizzes"]]
        self.assertEqual(len(questions), N)
        self.assertNotIn("중단 문제", questions)

    def test_interrupt_during_play_does_not_record(self):
        run_inputs(QuizGame(self.path).run, ["1", "2", str(ANSWERS[0]), KeyboardInterrupt()])
        self.assertIsNone(self.saved()["best_score"])
        self.assertEqual(self.saved()["history"], [])

    def test_interrupt_before_load_keeps_file(self):
        self.path.write_text('{"quizzes": [], "best_score": 50}', encoding="utf-8")
        with mock.patch.object(QuizGame, "load_data", side_effect=KeyboardInterrupt):
            run_inputs(QuizGame(self.path).run, [])
        self.assertEqual(self.saved(), {"quizzes": [], "best_score": 50})


if __name__ == "__main__":
    unittest.main()
