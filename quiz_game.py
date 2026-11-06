"""퀴즈 게임 전체를 관리하는 QuizGame 클래스.

메뉴 표시, 퀴즈 풀기/추가/목록/삭제, 점수 확인, 입력 처리, 파일 저장/불러오기를 담당한다.
"""

import json
import random
from pathlib import Path

from default_quizzes import get_default_quizzes
from quiz import Quiz

LINE = "=" * 40
THIN_LINE = "-" * 40


class QuizGame:
    """퀴즈 게임 전체를 관리한다.

    속성(attribute):
        state_path: 데이터 파일(state.json) 경로
        quizzes: 퀴즈 목록 (list[Quiz])
        best_score: 최고 점수 (아직 풀지 않았으면 None)
    """

    MENU = ("퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "퀴즈 삭제", "종료")
    HINT_PENALTY = 0.5  # 힌트를 본 문제는 맞혀도 1점에서 0.5점을 뺀다.

    def __init__(self, state_path) -> None:
        self.state_path = Path(state_path)
        self.quizzes: list[Quiz] = []
        self.best_score: int | None = None
        # 데이터를 불러오기 전에 저장하면 빈 목록으로 파일을 덮어쓰게 되므로 막아 둔다.
        self.is_loaded = False

    # ------------------------------------------------------------------
    # 실행 흐름
    # ------------------------------------------------------------------
    def run(self) -> None:
        """프로그램의 시작점. 종료를 고를 때까지 메뉴를 반복한다."""
        try:
            self.show_title()
            self.load_data()
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
                elif choice == 5:
                    self.delete_quiz()
                else:
                    self.quit()
                    break
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 또는 입력 스트림 종료 시 오류 화면 없이 저장하고 끝낸다.
            print("\n\n입력이 중단되어 프로그램을 종료합니다.")
            if self.is_loaded:
                self.save_data()

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
        """데이터를 저장하고 종료 메시지를 출력한다."""
        self.save_data()
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
        """풀 문제 수를 고르게 한 뒤 퀴즈를 랜덤 순서로 출제하고, 결과를 처리한다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        total = len(self.quizzes)
        count = self.ask_number(f"\n몇 문제를 풀까요? (1-{total}): ", 1, total)
        selected = random.sample(self.quizzes, count)  # 중복 없이 랜덤 순서로 count 개를 고른다.

        print(f"\n퀴즈를 시작합니다! (총 {count}문제)")
        correct_count = 0
        points = 0.0
        for number, quiz in enumerate(selected, start=1):
            print()
            print(THIN_LINE)
            quiz.display(number)
            print()
            user_answer, used_hint = self.ask_answer(quiz)
            if quiz.is_correct(user_answer):
                correct_count += 1
                if used_hint:
                    points += 1 - self.HINT_PENALTY
                else:
                    points += 1
                print("정답입니다!")
            else:
                print("오답입니다.")

        score = int(points * 100 / count)  # 100점 만점, 소수점 아래는 버린다.
        self.finish_game(count, correct_count, score)

    def ask_answer(self, quiz: Quiz) -> tuple[int, bool]:
        """정답 번호를 입력받는다. 힌트가 있는 문제에서 h 를 입력하면 힌트를 보여 준다.

        돌려주는 값: (입력한 번호, 힌트를 봤는지 여부)
        """
        used_hint = False
        prompt = "정답 입력 (힌트: h): " if quiz.has_hint() else "정답 입력: "
        while True:
            text = input(prompt).strip()
            if quiz.has_hint() and text.lower() == "h":
                used_hint = True
                print(f"힌트: {quiz.hint}")
                continue
            number = self.parse_number(text, 1, Quiz.CHOICE_COUNT)
            if number is not None:
                return number, used_hint

    def finish_game(self, total: int, correct: int, score: int) -> None:
        """결과를 보여 주고, 최고 점수를 갱신해 저장한다."""
        print()
        print(LINE)
        print(f"결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if self.update_best_score(score):
            print("새로운 최고 점수입니다!")
        print(LINE)
        self.save_data()

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
        """문제, 선택지 4개, 정답 번호, 힌트를 입력받아 새 퀴즈를 등록하고 저장한다."""
        print("\n새로운 퀴즈를 추가합니다.")
        question = self.ask_text("문제를 입력하세요: ")
        choices = []
        for number in range(1, Quiz.CHOICE_COUNT + 1):
            choices.append(self.ask_text(f"선택지 {number}: "))
        answer = self.ask_number(f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT)
        hint = input("힌트 (없으면 Enter): ").strip()

        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save_data()
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

    # ------------------------------------------------------------------
    # 5. 퀴즈 삭제
    # ------------------------------------------------------------------
    def delete_quiz(self) -> None:
        """번호를 골라 퀴즈를 삭제하고 파일에 반영한다."""
        if not self.quizzes:
            print("\n삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        total = len(self.quizzes)
        number = self.ask_number(f"\n삭제할 퀴즈 번호 (1-{total}): ", 1, total)
        removed = self.quizzes.pop(number - 1)
        self.save_data()
        print(f"\n퀴즈를 삭제했습니다: {removed.question}")

    # ------------------------------------------------------------------
    # 파일 저장 / 불러오기
    # ------------------------------------------------------------------
    def load_data(self) -> None:
        """state.json 에서 퀴즈 목록과 최고 점수를 불러온다.

        파일이 없으면 기본 퀴즈를 사용하고, 손상되었으면 안내 후 기본 퀴즈로 복구한다.
        """
        try:
            with open(self.state_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data["quizzes"], list):
                raise ValueError("퀴즈 목록 형식이 올바르지 않습니다.")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            best_score = data.get("best_score")
            if best_score is not None and type(best_score) is not int:
                raise ValueError("최고 점수 형식이 올바르지 않습니다.")
        except FileNotFoundError:
            self.use_default_quizzes()  # 첫 실행: 기본 퀴즈로 시작한다.
        except (ValueError, KeyError, TypeError, RecursionError):
            # json.JSONDecodeError(JSON 문법 오류), UnicodeDecodeError(인코딩 오류)도 ValueError 의 한 종류다.
            # RecursionError 는 괄호가 비정상적으로 깊게 중첩된 파일을 읽을 때 난다.
            self.use_default_quizzes()
            print("데이터 파일이 손상되어 기본 퀴즈 데이터로 복구합니다.")
            self.save_data()
        except OSError:
            self.use_default_quizzes()
            print("데이터 파일을 읽을 수 없어 기본 퀴즈로 시작합니다.")
        else:
            self.quizzes = quizzes
            self.best_score = best_score
            best_text = "없음" if best_score is None else f"{best_score}점"
            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {best_text})")
        self.is_loaded = True

    def use_default_quizzes(self) -> None:
        """기본 퀴즈로 시작한다. (최고 점수도 초기화)"""
        self.quizzes = get_default_quizzes()
        self.best_score = None

    def save_data(self) -> None:
        """퀴즈 목록과 최고 점수를 state.json 에 UTF-8 로 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        try:
            with open(self.state_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except (OSError, ValueError):
            # OSError: 권한·디스크 문제, ValueError: UTF-8 로 저장할 수 없는 글자
            print("데이터를 저장하지 못했습니다.")
