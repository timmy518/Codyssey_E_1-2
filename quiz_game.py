"""퀴즈 게임 전체를 관리하는 QuizGame 클래스.

메뉴 표시, 퀴즈 풀기/추가/목록, 점수 확인, 입력 처리를 담당한다.
"""

import random

from default_quizzes import get_default_quizzes
from quiz import Quiz

LINE = "=" * 40
THIN_LINE = "-" * 40


class QuizGame:
    """퀴즈 게임 전체를 관리한다.

    속성(attribute):
        quizzes: 퀴즈 목록 (list[Quiz])
        best_score: 최고 점수 (아직 풀지 않았으면 None)
    """

    MENU = ("퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료")

    def __init__(self) -> None:
        self.quizzes: list[Quiz] = get_default_quizzes()
        self.best_score: int | None = None

    # ------------------------------------------------------------------
    # 실행 흐름
    # ------------------------------------------------------------------
    def run(self) -> None:
        """프로그램의 시작점. 종료를 고를 때까지 메뉴를 반복한다."""
        try:
            self.show_title()
            while True:
                self.show_menu()
                choice = self.ask_number("선택: ", 1, len(self.MENU))
                if choice == 1:
                    self.play()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                else:
                    self.quit()
                    break
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 또는 입력 스트림 종료 시 오류 화면 없이 끝낸다.
            print("\n\n입력이 중단되어 프로그램을 종료합니다.")

    def show_title(self) -> None:
        print(LINE)
        print("            나만의 퀴즈 게임")
        print(LINE)

    def show_menu(self) -> None:
        print()
        print(LINE)
        for number, name in enumerate(self.MENU, start=1):
            print(f"{number}. {name}")
        print(LINE)

    def quit(self) -> None:
        """종료 메시지를 출력한다."""
        print("\n게임을 종료합니다.")

    # ------------------------------------------------------------------
    # 입력 처리
    # ------------------------------------------------------------------
    def parse_number(self, text: str, min_value: int, max_value: int) -> int | None:
        """글자를 숫자로 바꾼다. 빈 입력, 숫자가 아님, 범위 밖이면 안내 메시지를 출력하고 None 을 돌려준다."""
        if text == "":
            print(f"입력값이 없습니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
            return None
        try:
            number = int(text)
        except ValueError:
            print(f"잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
            return None
        if not min_value <= number <= max_value:
            print(f"잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
            return None
        return number

    def ask_number(self, prompt: str, min_value: int, max_value: int) -> int:
        """올바른 숫자를 입력할 때까지 다시 입력받는다. (앞뒤 공백은 지운다)"""
        while True:
            number = self.parse_number(input(prompt).strip(), min_value, max_value)
            if number is not None:
                return number

    def ask_text(self, prompt: str) -> str:
        """빈 값이 아닌 글자를 입력받는다. 빈 입력이면 안내 후 다시 입력받는다."""
        while True:
            text = input(prompt).strip()
            if text != "":
                return text
            print("입력값이 없습니다. 내용을 입력하세요.")

    # ------------------------------------------------------------------
    # 1. 퀴즈 풀기
    # ------------------------------------------------------------------
    def play(self) -> None:
        """풀 문제 수를 고르게 한 뒤 퀴즈를 랜덤 순서로 출제하고, 결과를 보여 준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        total = len(self.quizzes)
        count = self.ask_number(f"\n몇 문제를 풀까요? (1-{total}): ", 1, total)
        selected = random.sample(self.quizzes, count)  # 중복 없이 랜덤 순서로 count 개를 고른다.

        print(f"\n퀴즈를 시작합니다! (총 {count}문제)")
        correct_count = 0
        for number, quiz in enumerate(selected, start=1):
            print()
            print(THIN_LINE)
            quiz.display(number)
            print()
            user_answer = self.ask_number("정답 입력: ", 1, Quiz.CHOICE_COUNT)
            if quiz.is_correct(user_answer):
                correct_count += 1
                print("정답입니다!")
            else:
                print("오답입니다.")

        score = int(correct_count * 100 / count)  # 100점 만점, 소수점 아래는 버린다.
        print()
        print(LINE)
        print(f"결과: {count}문제 중 {correct_count}문제 정답! ({score}점)")
        if self.update_best_score(score):
            print("새로운 최고 점수입니다!")
        print(LINE)

    def update_best_score(self, score: int) -> bool:
        """점수를 최고 점수와 비교해 더 높으면 갱신한다. 갱신했으면 True."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            return True
        return False

    # ------------------------------------------------------------------
    # 2. 퀴즈 추가
    # ------------------------------------------------------------------
    def add_quiz(self) -> None:
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
        print("\n새로운 퀴즈를 추가합니다.")
        question = self.ask_text("문제를 입력하세요: ")
        choices = []
        for number in range(1, Quiz.CHOICE_COUNT + 1):
            choices.append(self.ask_text(f"선택지 {number}: "))
        answer = self.ask_number(f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT)

        self.quizzes.append(Quiz(question, choices, answer))
        print("\n퀴즈가 추가되었습니다!")

    # ------------------------------------------------------------------
    # 3. 퀴즈 목록
    # ------------------------------------------------------------------
    def list_quizzes(self) -> None:
        """등록된 퀴즈의 문제 목록을 보여 준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print(THIN_LINE)

    # ------------------------------------------------------------------
    # 4. 점수 확인
    # ------------------------------------------------------------------
    def show_score(self) -> None:
        """최고 점수를 보여 준다."""
        if self.best_score is None:
            print("\n아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요.")
            return
        print(f"\n최고 점수: {self.best_score}점")
