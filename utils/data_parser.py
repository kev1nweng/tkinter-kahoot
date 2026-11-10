"""
Parse Question data to data structures
"""

from types import *

class Question:
    def __init__(self, type: str, text: str, options: list[str], answer: str, res: list[str] = [], layout: str = "vertical"):
        self.type = type
        self.text = text
        self.options = options
        self.answer = answer
        self.response = None
        self.res = []
        self.layout = layout

    def load_question(self, question_data: dict):
        self.type = question_data.get("type", "")
        self.text = question_data.get("text", "")
        self.options = question_data.get("options", [])
        self.answer = question_data.get("answer", "")
        self.res = question_data.get("res", [])
        self.layout = question_data.get("layout", "vertical")


    def answer_question(self, response: str):
        self.response = response

class Exercise:
    def __init__(self, name: str, questions: list[Question], is_retryable: bool = False, is_reshowable: bool = False, is_reorderable: bool = False):
        self.is_retryable = is_retryable
        self.is_reshowable = is_reshowable
        self.is_reorderable = is_reorderable
        self.name = name
        self.questions = questions

    def load_exercise(self, exercise_data: dict):
        self.is_retryable = exercise_data.get("is_retryable", False)
        self.is_reshowable = exercise_data.get("is_reshowable", False)
        self.is_reorderable = exercise_data.get("is_reorderable", False)
        self.name = exercise_data.get("name", "")
        questions_data = exercise_data.get("questions", [])
        self.questions = [Question(**q) for q in questions_data]
