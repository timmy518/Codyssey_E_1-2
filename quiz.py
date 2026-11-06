"""퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """퀴즈 한 문제.

    속성(attribute):
        question: 문제 (str)
        choices: 선택지 4개 (list[str])
        answer: 정답 번호 (int, 1~4)
        hint: 힌트 (str, 없으면 빈 문자열)
    """

    CHOICE_COUNT = 4  # 선택지는 4개

    def __init__(self, question: str, choices: list[str], answer: int, hint: str = "") -> None:
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

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

    def has_hint(self) -> bool:
        """힌트가 있으면 True 를 돌려준다."""
        return self.hint != ""

    def to_dict(self) -> dict:
        """state.json 에 저장할 수 있도록 dict 로 바꾼다."""
        return {"question": self.question, "choices": self.choices, "answer": self.answer, "hint": self.hint}

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        """state.json 에서 읽은 dict 로 Quiz 를 만든다.

        형식이 틀리면 ValueError, 항목이 없으면 KeyError, dict 가 아니면 TypeError 가 발생한다.
        """
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        hint = data.get("hint", "")  # 힌트가 없는 데이터도 읽을 수 있게 한다.
        if not isinstance(question, str) or question == "":
            raise ValueError("문제 형식이 올바르지 않습니다.")
        if not isinstance(choices, list) or len(choices) != cls.CHOICE_COUNT:
            raise ValueError("선택지는 4개의 목록이어야 합니다.")
        for choice in choices:
            if not isinstance(choice, str) or choice == "":
                raise ValueError("선택지 형식이 올바르지 않습니다.")
        # type(...) is int: True/False(bool)는 정답 번호로 인정하지 않는다.
        if type(answer) is not int or not 1 <= answer <= cls.CHOICE_COUNT:
            raise ValueError("정답 번호는 1~4 사이의 정수여야 합니다.")
        if not isinstance(hint, str):
            raise ValueError("힌트 형식이 올바르지 않습니다.")
        return cls(question, choices, answer, hint)
