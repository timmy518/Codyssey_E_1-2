"""나만의 퀴즈 게임 실행 파일.

실행 방법:
    python main.py
"""

import sys

# (보충) 다른 파일은 Python 3.10 문법(int | None 등)을 쓰므로, 불러오기 전에 버전을 먼저 확인한다.
if sys.version_info < (3, 10):
    print(f"Python 3.10 이상이 필요합니다. (현재 버전: {sys.version.split()[0]})")
    sys.exit(1)

from pathlib import Path  # noqa: E402  (버전 확인 뒤에 불러온다)

from quiz_game import QuizGame  # noqa: E402

# 데이터 파일은 프로젝트 루트(이 파일이 있는 폴더)의 state.json 을 사용한다.
STATE_FILE = Path(__file__).resolve().parent / "state.json"


def main() -> None:
    game = QuizGame(STATE_FILE)
    game.run()


if __name__ == "__main__":
    main()
