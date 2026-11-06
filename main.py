"""나만의 퀴즈 게임 실행 파일.

실행 방법:
    python main.py
"""

from quiz_game import QuizGame


def main() -> None:
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
