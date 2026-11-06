"""(보충) main.py 를 실제 프로세스로 실행하는 테스트. 파일을 임시 폴더에 복사해서 실행한다."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILES = ["main.py", "quiz.py", "quiz_game.py", "default_quizzes.py"]


def find_emoji(text):
    """이모지(그림 문자)만 골라 돌려준다."""
    return [ch for ch in text if ord(ch) >= 0x1F000 or 0x2600 <= ord(ch) <= 0x27BF or ch == "️"]


class MainProcessTest(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.project = Path(temp_dir.name) / "project"
        self.project.mkdir()
        for name in SOURCE_FILES:
            shutil.copy(PROJECT_ROOT / name, self.project / name)

    def run_main(self, stdin_text, cwd=None):
        env = dict(os.environ, PYTHONUTF8="1")  # 파이프로 한글을 주고받기 위해 UTF-8 모드로 실행
        return subprocess.run([sys.executable, str(self.project / "main.py")], input=stdin_text,
                              capture_output=True, text=True, encoding="utf-8", cwd=cwd or self.project,
                              timeout=60, env=env)

    def test_end_of_input_exits_safely(self):
        for stdin_text in ("", "2\n문제\n", "1\n2\n", "5\n"):
            with self.subTest(stdin_text=stdin_text):
                result = self.run_main(stdin_text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("입력이 중단되어 프로그램을 종료합니다.", result.stdout)

    def test_state_file_is_next_to_main_py(self):
        result = self.run_main("6\n", cwd=self.project.parent)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "state.json").exists())
        self.assertFalse((self.project.parent / "state.json").exists())

    def test_full_session_and_restart(self):
        first = self.run_main("abc\n2\n재시작 문제?\n가\n나\n다\n라\n2\n힌트\n3\n1\n3\nh\n1\nh\n1\nh\n1\n4\n5\n11\n6\n")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("결과: 3문제 중", first.stdout)
        self.assertIn("퀴즈를 삭제했습니다: 재시작 문제?", first.stdout)
        second = self.run_main("3\n4\n6\n")
        self.assertIn("저장된 데이터를 불러왔습니다. (퀴즈 10개, 최고점수 ", second.stdout)
        self.assertIn("게임 기록 (총 1회)", second.stdout)
        self.assertEqual(find_emoji(first.stdout + second.stdout), [])

    def test_corrupted_file_backup(self):
        (self.project / "state.json").write_text("{ broken", encoding="utf-8")
        result = self.run_main("6\n")
        self.assertIn("손상된 파일은 state.json.bak 으로 백업했습니다.", result.stdout)
        self.assertEqual((self.project / "state.json.bak").read_text(encoding="utf-8"), "{ broken")

    def test_python_version_check(self):
        code = ("import runpy, sys; sys.version_info = (3, 9, 18); "
                f"runpy.run_path(r'{self.project / 'main.py'}', run_name='__main__')")
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8",
                                env=dict(os.environ, PYTHONUTF8="1"), timeout=60)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Python 3.10 이상이 필요합니다.", result.stdout)

    def test_sources_have_no_emoji(self):
        for name in SOURCE_FILES:
            with self.subTest(name):
                self.assertEqual(find_emoji((PROJECT_ROOT / name).read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
