from tkquiz.models import Question, QuestionSet


def check_question(question: Question) -> list[str]:
    problems = []
    if not question.prompt.strip():
        problems.append("the prompt is empty")
    options = question.options
    if not isinstance(options, list):
        problems.append("options must be a list of four strings")
        return problems
    if len(options) != 4:
        problems.append("a question needs exactly four options")
        return problems
    seen = []
    for option in options:
        if not isinstance(option, str):
            problems.append("options must be a list of four strings")
            return problems
        text = option.strip()
        if not text:
            problems.append("every option needs text")
            return problems
        if text.casefold() in seen:
            problems.append("the options must not repeat")
            return problems
        seen.append(text.casefold())
    if not isinstance(question.correct_index, int):
        problems.append("the correct answer must be one of the four options")
        return problems
    if question.correct_index not in range(4):
        problems.append("the correct answer must be one of the four options")
    return problems


def check_set(question_set: QuestionSet) -> list[str]:
    problems = []
    if not question_set.title.strip():
        problems.append("the set needs a title")
    if question_set.time_limit < 1:
        problems.append("the time limit must be at least one second")
    return problems
