import sqlite3

from tkquiz.models import QuestionSet, Question, PlayerScore, Round
from tkquiz.rules import check_question, check_set

SCHEMA = """
    CREATE TABLE IF NOT EXISTS sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        time_limit INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        set_id INTEGER NOT NULL,
        prompt TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_index INTEGER NOT NULL,
        FOREIGN KEY (set_id) REFERENCES sets (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        set_id INTEGER,
        set_title TEXT NOT NULL,
        played_at DATETIME NOT NULL,
        total_questions INTEGER NOT NULL,
        FOREIGN KEY (set_id) REFERENCES sets (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        score INTEGER NOT NULL,
        FOREIGN KEY (round_id) REFERENCES rounds (id) ON DELETE CASCADE
    );
"""


class Storage:
    def __init__(self, path: str = "tkquiz.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_schema()

    def create_schema(self):
        self.conn.executescript(SCHEMA)

    # set methods
    def add_set(self, title: str, time_limit: int) -> int:
        _require_valid_set(title, time_limit)
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sets (title, time_limit) VALUES (?, ?)",
            (title, time_limit),
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise StorageError("Failed to insert new set")
        return cursor.lastrowid

    def get_set(self, set_id: int) -> QuestionSet | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sets WHERE id = ?", (set_id,))
        row = cursor.fetchone()
        if row:
            return QuestionSet(
                title=row["title"], time_limit=row["time_limit"], id=row["id"]
            )
        return None

    def list_sets(self) -> list[QuestionSet]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sets ORDER BY title COLLATE NOCASE")
        rows = cursor.fetchall()
        return [
            QuestionSet(
                title=row["title"], time_limit=row["time_limit"], id=row["id"]
            )
            for row in rows
        ]

    def update_set(self, set_id: int, title: str, time_limit: int) -> None:
        _require_valid_set(title, time_limit)
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE sets SET title = ?, time_limit = ? WHERE id = ?",
            (title, time_limit, set_id),
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            raise StorageError(f"Set with id {set_id} not found")

    def delete_set(self, set_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sets WHERE id = ?", (set_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            raise StorageError(f"Set with id {set_id} not found")

    # question methods
    def add_question(self, question: Question) -> int:
        _require_valid_question(question)
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO questions (set_id, prompt, option_a, option_b, "
            "option_c, option_d, correct_index) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                question.set_id,
                question.prompt,
                *question.options,
                question.correct_index,
            ),
        )
        self.conn.commit()
        if cursor.lastrowid is None:
            raise StorageError("Failed to insert new question")
        return cursor.lastrowid

    def update_question(self, question: Question) -> None:
        _require_valid_question(question)
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE questions SET prompt = ?, option_a = ?, "
            "option_b = ?, option_c = ?, option_d = ?, "
            "correct_index = ? WHERE id = ?",
            (
                question.prompt,
                *question.options,
                question.correct_index,
                question.id,
            ),
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            raise StorageError(f"Question with id {question.id} not found")

    def delete_question(self, question_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            raise StorageError(f"Question with id {question_id} not found")

    def list_questions(self, set_id: int) -> list[Question]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM questions WHERE set_id = ? ORDER BY id", (set_id,)
        )
        rows = cursor.fetchall()
        return [
            Question(
                set_id=row["set_id"],
                prompt=row["prompt"],
                options=[
                    row["option_a"],
                    row["option_b"],
                    row["option_c"],
                    row["option_d"],
                ],
                correct_index=row["correct_index"],
                id=row["id"],
            )
            for row in rows
        ]

    # round methods
    def save_round(self, round_: Round) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO rounds (set_id, set_title, played_at, "
            "total_questions) VALUES (?, ?, ?, ?)",
            (
                round_.set_id,
                round_.set_title,
                round_.played_at,
                round_.total_questions,
            ),
        )
        round_id = cursor.lastrowid
        if round_id is None:
            raise StorageError("Failed to insert new round")
        for player in round_.players:
            cursor.execute(
                "INSERT INTO players (round_id, name, score) VALUES (?, ?, ?)",
                (round_id, player.name, player.score),
            )
        self.conn.commit()
        return round_id

    def list_rounds(self) -> list[Round]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rounds ORDER BY played_at DESC, id DESC")
        rounds_rows = cursor.fetchall()
        rounds = []
        for round_row in rounds_rows:
            cursor.execute(
                "SELECT name, score FROM players WHERE round_id = ?",
                (round_row["id"],),
            )
            players_rows = cursor.fetchall()
            players = [
                PlayerScore(name=row["name"], score=row["score"])
                for row in players_rows
            ]
            rounds.append(
                Round(
                    set_id=round_row["set_id"],
                    set_title=round_row["set_title"],
                    played_at=round_row["played_at"],
                    total_questions=round_row["total_questions"],
                    players=players,
                    id=round_row["id"],
                )
            )
        return rounds

    def list_players(self, round_id: int) -> list[PlayerScore]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, score FROM players WHERE round_id = ?", (round_id,)
        )
        rows = cursor.fetchall()
        return [
            PlayerScore(name=row["name"], score=row["score"]) for row in rows
        ]

    def delete_round(self, round_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM rounds WHERE id = ?", (round_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            raise StorageError(f"Round with id {round_id} not found")

    def close(self) -> None:
        self.conn.close()


class StorageError(Exception):
    pass


def _require_valid_question(question: Question) -> None:
    problems = check_question(question)
    if problems:
        raise ValueError("; ".join(problems))


def _require_valid_set(title: str, time_limit: int) -> None:
    problems = check_set(QuestionSet(title=title, time_limit=time_limit))
    if problems:
        raise ValueError("; ".join(problems))
