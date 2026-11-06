"""나만의 퀴즈 게임 실행 파일.

실행 방법:
    python main.py
"""

from pathlib import Path

from quiz_game import QuizGame

# 데이터 파일은 프로젝트 루트(이 파일이 있는 폴더)의 state.json 을 사용한다.
STATE_FILE = Path(__file__).resolve().parent / "state.json"


def main() -> None:
    game = QuizGame(STATE_FILE)
    game.run()


if __name__ == "__main__":
    main()
