from dataclasses import dataclass

from tkquiz.models import Question, QuestionSet, Round, PlayerScore


@dataclass
class Turn:
    question: Question
    player: str
    answered: bool = False
    chosen: int | None = None
    correct: bool | None = None


class QuizSession:
    def __init__(
        self,
        question_set: QuestionSet,
        questions: list[Question],
        player_names: list[str],
    ):
        self.question_set = question_set
        self.questions = questions
        self.current_question_index = 0
        self.scores: dict[str, int] = {}
        for name in player_names:
            self.scores[name] = 0

    def total_questions(self) -> int:
        return len(self.questions)

    def index(self) -> int:
        return self.current_question_index

    def is_finished(self) -> bool:
        return self.current_question_index >= len(self.questions)

    def current(self) -> Turn | None:
        if self.is_finished():
            return None
        question = self.questions[self.current_question_index]
        return Turn(question=question, player="", answered=False)

    def current_player(self) -> str | None:
        if self.is_finished():
            return None
        player_names = list(self.scores.keys())
        return player_names[self.current_question_index % len(player_names)]

    def answer(self, option_index: int) -> bool:
        if self.is_finished():
            raise SessionError("The quiz session is already finished")
        question = self.questions[self.current_question_index]
        correct = option_index == question.correct_index
        player_name = self.current_player()
        if player_name is not None:
            if correct:
                self.scores[player_name] += 1
        self.current_question_index += 1
        return correct

    def advance(self) -> None:
        if self.is_finished():
            raise SessionError("The quiz session is already finished")
        self.current_question_index += 1

    def get_scores(self) -> dict[str, int]:
        return self.scores

    def to_round(self, played_at: str) -> "Round":
        set_id = self.question_set.id
        if set_id is None:
            raise SessionError(
                "Cannot save a round for an unsaved question set"
            )
        players = [
            PlayerScore(name=name, score=score)
            for name, score in self.scores.items()
        ]
        return Round(
            set_id=set_id,
            set_title=self.question_set.title,
            played_at=played_at,
            total_questions=len(self.questions),
            players=players,
        )


class SessionError(Exception):
    pass
