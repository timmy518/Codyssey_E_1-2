"""퀴즈 게임 전체를 관리하는 QuizGame 클래스.

입력 처리를 담당한다.
"""


class QuizGame:
    """퀴즈 게임 전체를 관리한다."""

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
