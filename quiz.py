"""퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """퀴즈 한 문제.

    속성(attribute):
        question: 문제 (str)
        choices: 선택지 4개 (list[str])
        answer: 정답 번호 (int, 1~4)
    """

    CHOICE_COUNT = 4  # 선택지는 4개

    def __init__(self, question: str, choices: list[str], answer: int) -> None:
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, number: int) -> None:
        """문제 번호, 문제, 선택지를 화면에 출력한다."""
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def is_correct(self, user_answer: int) -> bool:
        """입력한 번호가 정답이면 True 를 돌려준다."""
        return user_answer == self.answer
