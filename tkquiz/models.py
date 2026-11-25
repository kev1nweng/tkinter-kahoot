from dataclasses import dataclass


@dataclass
class QuestionSet:
    title: str
    time_limit: int
    id: int | None = None


@dataclass
class Question:
    set_id: int
    prompt: str
    options: list[str]
    correct_index: int
    id: int | None = None


@dataclass
class PlayerScore:
    name: str
    score: int


@dataclass
class Round:
    set_id: int
    set_title: str
    played_at: str
    total_questions: int
    players: list[PlayerScore]
    id: int | None = None
