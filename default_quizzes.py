"""기본 퀴즈 데이터 (주제: Python & Git 기초).

[퀴즈를 바꾸는 방법]
1. 아래 get_default_quizzes() 안의 Quiz(...) 목록을 원하는 문제로 바꾼다. (5개 이상)
   - choices 에는 선택지 4개, answer 에는 정답 선택지의 번호(1~4), hint 에는 힌트를 적는다.
2. state.json 을 지우고 다시 실행하면 바꾼 기본 퀴즈로 시작한다.
   (state.json 이 있으면 저장된 퀴즈를 그대로 불러온다)
3. README.md 의 '퀴즈 주제와 선정 이유'도 함께 고친다.
4. python -m unittest discover -s tests 로 확인한다. 테스트는 이 목록에서 퀴즈 수, 정답, 문제 문구를
   읽어 쓰므로, 1번 조건을 지키면 테스트를 고치지 않고 통과한다. 단, 선택지는 숫자도 "4" 처럼
   글자로 적고(숫자 그대로면 다시 실행할 때 손상 파일로 처리된다), 이모지 같은 그림 문자는 쓰지 않는다.
"""

from quiz import Quiz


def get_default_quizzes() -> list[Quiz]:
    """기본 퀴즈 목록을 Quiz 인스턴스로 만들어 돌려준다."""
    return [
        Quiz(
            question="Python에서 x = 10 일 때, type(x)의 결과로 알맞은 자료형은?",
            choices=["str", "int", "float", "bool"],
            answer=2,
            hint="소수점이 없는 '정수(integer)'를 뜻하는 단어의 줄임말이에요.",
        ),
        Quiz(
            question="키(key)와 값(value)을 한 쌍으로 묶어 저장하는 Python 자료형은?",
            choices=["list", "tuple", "dict", "set"],
            answer=3,
            hint="중괄호 { } 안에 '키: 값' 형태로 적어요.",
        ),
        Quiz(
            question="클래스로 객체를 만들 때 자동으로 호출되어 속성을 초기화하는 메서드는?",
            choices=["__init__", "__str__", "__len__", "__main__"],
            answer=1,
            hint="'초기화하다(initialize)'의 앞 글자를 따서 만든 이름이에요.",
        ),
        Quiz(
            question="조건이 참(True)인 동안 계속 반복하며, 반복 횟수를 미리 알기 어려울 때 주로 쓰는 문법은?",
            choices=["if", "for", "def", "while"],
            answer=4,
            hint="영어로 '~하는 동안'이라는 뜻이에요.",
        ),
        Quiz(
            question="오류가 날 수 있는 코드를 실행하고, 오류가 나면 따로 처리할 수 있게 해 주는 문법은?",
            choices=["if / else", "try / except", "for / in", "def / return"],
            answer=2,
            hint="'시도하다'라는 뜻의 단어로 시작해요.",
        ),
        Quiz(
            question="클래스의 메서드에서 '메서드를 호출한 객체 자신'을 가리키는 첫 번째 매개변수의 관례적인 이름은?",
            choices=["this", "me", "cls", "self"],
            answer=4,
            hint="영어로 '자기 자신'이라는 뜻이에요.",
        ),
        Quiz(
            question="JSON 파일을 열어 그 내용을 Python 객체(dict, list 등)로 읽어 오는 함수는?",
            choices=["json.dump()", "json.dumps()", "json.load()", "json.save()"],
            answer=3,
            hint="'불러오다'라는 뜻의 영어 단어예요.",
        ),
        Quiz(
            question="Git에서 변경된 파일을 커밋할 대상(스테이징 영역)에 올리는 명령어는?",
            choices=["git add", "git commit", "git push", "git clone"],
            answer=1,
            hint="'더하다, 추가하다'라는 뜻이에요.",
        ),
        Quiz(
            question="원격 저장소의 최신 변경 사항을 가져와 현재 브랜치에 합치는 Git 명령어는?",
            choices=["git push", "git clone", "git init", "git pull"],
            answer=4,
            hint="'당기다'라는 뜻이에요. 반대말은 push!",
        ),
        Quiz(
            question="새 브랜치를 만들면서 동시에 그 브랜치로 이동하는 Git 명령어는?",
            choices=["git branch", "git checkout -b 브랜치이름", "git merge 브랜치이름", "git status"],
            answer=2,
            hint="'-b'는 branch 의 b 예요.",
        ),
    ]
