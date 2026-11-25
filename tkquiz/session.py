from dataclasses import dataclass

from tkquiz.models import PlayerScore, Question, QuestionSet, Round


@dataclass
class Turn:
    question: Question
    player: str
    answered: bool = False
    chosen: int | None = None
    correct: bool = False


class SessionError(Exception):
    pass


class QuizSession:
    def __init__(
        self,
        question_set: QuestionSet,
        questions: list[Question],
        player_names: list[str],
    ) -> None:
        self.question_set = question_set
        self.questions = questions
        self.player_names = player_names
        self.current_question_index = 0
        self.answered = False
        self.chosen: int | None = None
        self.totals: dict[str, int] = {}
        for name in player_names:
            self.totals[name] = 0

    def total_questions(self) -> int:
        return len(self.questions)

    def index(self) -> int:
        return self.current_question_index

    def is_finished(self) -> bool:
        return self.current_question_index >= len(self.questions)

    def current(self) -> Turn | None:
        if self.is_finished():
            return None
        player = self.current_player()
        if player is None:
            return None
        question = self.questions[self.current_question_index]
        correct = False
        if self.answered:
            correct = self.chosen == question.correct_index
        return Turn(
            question=question,
            player=player,
            answered=self.answered,
            chosen=self.chosen,
            correct=correct,
        )

    def current_player(self) -> str | None:
        if self.is_finished():
            return None
        if not self.player_names:
            return None
        position = self.current_question_index % len(self.player_names)
        return self.player_names[position]

    def answer(self, option_index: int) -> bool:
        if self.is_finished():
            raise SessionError("The quiz session is already finished")
        if self.answered:
            raise SessionError("This question is already answered")
        question = self.questions[self.current_question_index]
        self.answered = True
        self.chosen = option_index
        correct = option_index == question.correct_index
        player = self.current_player()
        if correct and player is not None:
            self.totals[player] += 1
        return correct

    def advance(self) -> None:
        if self.is_finished():
            return
        self.current_question_index += 1
        self.answered = False
        self.chosen = None

    def scores(self) -> list[PlayerScore]:
        return [
            PlayerScore(name=name, score=self.totals[name])
            for name in self.player_names
        ]

    def to_round(self, played_at: str) -> Round:
        set_id = self.question_set.id
        if set_id is None:
            raise SessionError(
                "Cannot save a round for an unsaved question set"
            )
        return Round(
            set_id=set_id,
            set_title=self.question_set.title,
            played_at=played_at,
            total_questions=len(self.questions),
            players=self.scores(),
        )
