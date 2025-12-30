"""
PEP 8 Quiz Arcade

An Arcade page that quizzes users on PEP 8 and basic coding best practices.
Users earn coins for correct answers and can unlock monsters.
"""

import random
import textwrap
from typing import Any, Dict, List, Optional, TypedDict

import streamlit as st

# -----------------------------------------------------------------------------
# Quiz & game configuration constants
# -----------------------------------------------------------------------------
DEFAULT_NUM_QUESTIONS: int = 7
MIN_QUESTIONS_PER_GAME: int = 3
MAX_QUESTIONS_PER_GAME: int = 10

BASE_COIN_REWARD: int = 5
MAX_STREAK_BONUS: int = 5

HINT_COST: int = 3
SKIP_COST: int = 4
FIFTY_FIFTY_COST: int = 5

BADGE_SCORE_APPRENTICE: int = 5
BADGE_SCORE_PRO: int = 7
BADGE_STREAK_THRESHOLD: int = 3

BADGE_MONSTER_COLLECTOR: str = "✨ Monster Collector"


class Question(TypedDict):
    """
    Typed representation of a quiz question.

    Using TypedDict allows static type checkers (e.g. mypy) to validate
    that all question dictionaries have the expected keys and types.
    """

    id: str
    prompt: str
    code: Optional[str]
    options: List[str]
    answer_idx: int
    explanation: str
    topic: str


class Monster(TypedDict):
    """
    Typed representation of a cosmetic monster shown in the UI.
    """

    id: str
    name: str
    emoji: str
    price: int
    description: str
    image: str


# -----------------------------------------------------------------------------
# Question pool (20 questions)
# -----------------------------------------------------------------------------
# This is a static question bank. Each question has:
# - a unique id
# - a prompt
# - optional code snippet (for display)
# - multiple-choice options with answer index
# - an explanation and topic (used for hints)
QUESTION_POOL: List[Question] = [
    {
        "id": "line_length",
        "prompt": "What is the recommended maximum line length in PEP 8?",
        "code": None,
        "options": ["79 characters", "99 characters", "120 characters", "60 characters"],
        "answer_idx": 0,
        "explanation": (
            "PEP 8 recommends limiting all lines to a maximum of 79 characters."
        ),
        "topic": "Formatting",
    },
    {
        "id": "imports_order",
        "prompt": "Which import order is PEP 8 compliant?",
        "code": textwrap.dedent(
            """
            # Option A
            import numpy as np
            import os
            from my_app import utils
            """
        ).strip(),
        "options": [
            "Standard library -> third-party -> local application imports",
            "Third-party -> standard library -> local application imports",
            "Local -> third-party -> standard library imports",
            "Any order is fine",
        ],
        "answer_idx": 0,
        "explanation": (
            "PEP 8 recommends: standard library imports first, then third-party, "
            "then local imports."
        ),
        "topic": "Imports",
    },
    {
        "id": "naming_functions",
        "prompt": "Which function name follows PEP 8 naming conventions?",
        "code": None,
        "options": [
            "calculateTotal()",
            "calculate_total()",
            "CalculateTotal()",
            "calculate-Total()",
        ],
        "answer_idx": 1,
        "explanation": (
            "Functions should be lowercase with words separated by underscores: "
            "'calculate_total'."
        ),
        "topic": "Naming",
    },
    {
        "id": "whitespace",
        "prompt": (
            "Which snippet is more PEP 8 compliant regarding whitespace "
            "around operators?"
        ),
        "code": textwrap.dedent(
            """
            # Version 1
            x=1+2*3

            # Version 2
            x = 1 + 2 * 3
            """
        ).strip(),
        "options": ["Version 1", "Version 2", "Both are equally recommended", "Neither"],
        "answer_idx": 1,
        "explanation": (
            "PEP 8 recommends spaces around operators to improve readability."
        ),
        "topic": "Formatting",
    },
    {
        "id": "docstring",
        "prompt": "Where should a function docstring be placed?",
        "code": textwrap.dedent(
            """
            def add(a, b):
                # Adds two numbers
                return a + b
            """
        ).strip(),
        "options": [
            "As a comment above the function",
            "As the first statement inside the function (triple quotes)",
            "In a separate README file only",
            "Docstrings are only for classes, not functions",
        ],
        "answer_idx": 1,
        "explanation": (
            "A docstring is placed as the first statement inside the function "
            "using triple quotes."
        ),
        "topic": "Docstrings",
    },
    {
        "id": "comparisons",
        "prompt": "PEP 8 recommends comparing to None using:",
        "code": None,
        "options": ["== None", "!= None", "is None", "equals(None)"],
        "answer_idx": 2,
        "explanation": "Use 'is None' and 'is not None' for comparisons with None.",
        "topic": "Best practices",
    },
    {
        "id": "trailing_whitespace",
        "prompt": "What does PEP 8 say about trailing whitespace?",
        "code": None,
        "options": [
            "It is recommended for alignment",
            "It is allowed only in comments",
            "It should be avoided",
            "It should be used after commas",
        ],
        "answer_idx": 2,
        "explanation": (
            "Trailing whitespace should be avoided because it is unnecessary and "
            "creates noise in diffs."
        ),
        "topic": "Formatting",
    },
    {
        "id": "indentation",
        "prompt": "What is the preferred indentation style in PEP 8?",
        "code": None,
        "options": ["2 spaces", "4 spaces", "Tabs only", "Mix of tabs and spaces"],
        "answer_idx": 1,
        "explanation": "PEP 8 recommends using 4 spaces per indentation level.",
        "topic": "Formatting",
    },
    {
        "id": "tabs_vs_spaces",
        "prompt": "What does PEP 8 recommend for indentation characters?",
        "code": None,
        "options": [
            "Tabs only",
            "Spaces only",
            "Either tabs or spaces, mixing is fine",
            "Mixing tabs and spaces is recommended",
        ],
        "answer_idx": 1,
        "explanation": "PEP 8 recommends using spaces rather than tabs for indentation.",
        "topic": "Formatting",
    },
    {
        "id": "class_naming",
        "prompt": "Which class name follows PEP 8 conventions?",
        "code": None,
        "options": ["myclass", "MyClass", "my_class", "MYCLASS"],
        "answer_idx": 1,
        "explanation": "Classes normally use CapWords (PascalCase) convention: 'MyClass'.",
        "topic": "Naming",
    },
    {
        "id": "constant_naming",
        "prompt": "How should constants be named according to PEP 8?",
        "code": None,
        "options": ["maxValue", "MAX_VALUE", "MaxValue", "max_value"],
        "answer_idx": 1,
        "explanation": (
            "Constants are typically written in all caps with underscores: "
            "'MAX_VALUE'."
        ),
        "topic": "Naming",
    },
    {
        "id": "blank_lines",
        "prompt": (
            "How many blank lines should typically separate top-level function "
            "definitions?"
        ),
        "code": None,
        "options": ["0", "1", "2", "4"],
        "answer_idx": 2,
        "explanation": (
            "Two blank lines are recommended between top-level function and class "
            "definitions."
        ),
        "topic": "Layout",
    },
    {
        "id": "spaces_after_comma",
        "prompt": "Which list formatting is more PEP 8 compliant?",
        "code": textwrap.dedent(
            """
            # Version 1
            nums = [1,2,3,4]

            # Version 2
            nums = [1, 2, 3, 4]
            """
        ).strip(),
        "options": ["Version 1", "Version 2", "Both are fine", "Neither"],
        "answer_idx": 1,
        "explanation": (
            "A space after each comma in lists and tuples improves readability."
        ),
        "topic": "Formatting",
    },
    {
        "id": "boolean_singleton",
        "prompt": "How should you check if a value is True according to PEP 8?",
        "code": None,
        "options": [
            "if x == True:",
            "if x is True:",
            "if x:",
            "if bool(x) == True:",
        ],
        "answer_idx": 2,
        "explanation": "Use 'if x:' rather than explicit comparisons to True.",
        "topic": "Best practices",
    },
    {
        "id": "imports_at_top",
        "prompt": "Where should imports generally be placed according to PEP 8?",
        "code": None,
        "options": [
            "Spread throughout the file where needed",
            "Inside functions only",
            "At the top of the file, after any module comments and docstrings",
            "At the bottom of the file",
        ],
        "answer_idx": 2,
        "explanation": (
            "Imports should be placed at the top of the file, after module comments "
            "and docstrings."
        ),
        "topic": "Imports",
    },
    {
        "id": "inline_comments",
        "prompt": "Which inline comment is more PEP 8 compliant?",
        "code": textwrap.dedent(
            """
            # Version 1
            x = x + 1 #increment x

            # Version 2
            x = x + 1  # increment x
            """
        ).strip(),
        "options": ["Version 1", "Version 2", "Both are fine", "Neither"],
        "answer_idx": 1,
        "explanation": (
            "Inline comments should be separated from code by at least two spaces "
            "and start with a single space."
        ),
        "topic": "Comments",
    },
    {
        "id": "docstring_quotes",
        "prompt": "What is the recommended quoting style for docstrings?",
        "code": None,
        "options": [
            "Single quotes: '''docstring'''",
            'Double quotes: """docstring"""',
            "Either, but triple double quotes are recommended",
            "Single line comments instead of docstrings",
        ],
        "answer_idx": 2,
        "explanation": "Triple double quotes are recommended for docstrings.",
        "topic": "Docstrings",
    },
    {
        "id": "module_naming",
        "prompt": "Which module name best follows PEP 8?",
        "code": None,
        "options": ["MyModule.py", "mymodule.py", "myModule.py", "MYMODULE.py"],
        "answer_idx": 1,
        "explanation": (
            "Modules should have short, lowercase names, optionally with underscores "
            "if necessary."
        ),
        "topic": "Naming",
    },
    {
        "id": "complicated_expressions",
        "prompt": "What does PEP 8 suggest for very complicated expressions?",
        "code": None,
        "options": [
            "Write them on one line, no matter the length",
            "Add more comments, but keep them as one expression",
            "Break them into smaller, named variables or helper functions",
            "Avoid using them at all",
        ],
        "answer_idx": 2,
        "explanation": (
            "Complicated expressions should be split into smaller parts or helper "
            "functions to improve readability."
        ),
        "topic": "Readability",
    },
    {
        "id": "shebang_encoding",
        "prompt": (
            "Where should encoding declarations (if needed) appear in a Python file?"
        ),
        "code": None,
        "options": [
            "Anywhere in the file",
            "At the bottom of the file",
            "On the first or second line",
            "Inside the main() function",
        ],
        "answer_idx": 2,
        "explanation": (
            "Encoding declarations must be placed on the first or second line of "
            "the file."
        ),
        "topic": "Encoding",
    },
]

# -----------------------------------------------------------------------------
# Monster shop configuration
# -----------------------------------------------------------------------------
# “monsters” that users can purchase with coins. They do not
# affect gameplay logic and are purely visual.
MONSTER_SHOP: List[Monster] = [
    {
        "id": "pep_snek",
        "name": "PEP Snek",
        "emoji": "🐍",
        "price": 20,
        "description": "Monster associated with short, readable lines of code.",
        "image": "1.jpg",
    },
    {
        "id": "lint_lizard",
        "name": "Lint Lizard",
        "emoji": "🦎",
        "price": 35,
        "description": "Monster associated with finding style issues in code.",
        "image": "2.jpg",
    },
    {
        "id": "docstring_dragon",
        "name": "Docstring Dragon",
        "emoji": "🐲",
        "price": 50,
        "description": (
            "Monster associated with well-documented functions and modules."
        ),
        "image": "3.jpg",
    },
    {
        "id": "whitespace_wraith",
        "name": "Whitespace Wraith",
        "emoji": "👻",
        "price": 60,
        "description": "Monster associated with clean spacing and layout in code.",
        "image": "4.jpg",
    },
]


def get_monster(monster_id: str) -> Optional[Monster]:
    """
    Return the monster dictionary for a given monster identifier.

    This helper encapsulates the lookup logic so we don't duplicate it in
    multiple UI sections.

    Parameters
    ----------
    monster_id:
        Identifier of the monster.

    Returns
    -------
    Monster | None
        Monster entry if the identifier exists, otherwise None.
    """
    return next(
        (monster for monster in MONSTER_SHOP if monster["id"] == monster_id),
        None,
    )


# -----------------------------------------------------------------------------
# State and scoring helpers
# -----------------------------------------------------------------------------
def init_state() -> None:
    """
    Initialize Streamlit session state with default values for the quiz and shop.

    We centralize state initialization to avoid KeyError and to keep the
    default values in a single place.
    """
    defaults: Dict[str, Any] = {
        "started": False,
        "num_questions": DEFAULT_NUM_QUESTIONS,
        "question_ids": [],
        "q_index": 0,
        "score": 0,
        "coins": 0,
        "streak": 0,
        "answered": False,
        "last_correct": None,
        "used_5050": False,
        "eliminated_options": set(),
        "hints_used": 0,
        "skips_used": 0,
        "badges": set(),
        "shop_buys": [],
        "show_hint": False,
        "monsters_owned": [],
        "selected_monster": None,
    }

    # Only set defaults if the key is missing, so we don't overwrite state
    # across reruns (which is how Streamlit apps work).
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_new_game() -> None:
    """
    Start a new quiz game by resetting relevant state and selecting questions.

    All per-game counters (score, coins, streak, etc.) are reset, but we keep
    long-term things like owned monsters.
    """
    st.session_state.started = True
    st.session_state.score = 0
    st.session_state.coins = 0
    st.session_state.streak = 0
    st.session_state.q_index = 0
    st.session_state.answered = False
    st.session_state.last_correct = None
    st.session_state.used_5050 = False
    st.session_state.eliminated_options = set()
    st.session_state.hints_used = 0
    st.session_state.skips_used = 0
    st.session_state.badges = set()
    st.session_state.shop_buys = []
    st.session_state.show_hint = False

    # Limit the number of questions to the size of the pool.
    num_questions = min(st.session_state.num_questions, len(QUESTION_POOL))

    # Randomly sample question IDs so each game feels different.
    picked_ids = random.sample(
        [question["id"] for question in QUESTION_POOL],
        k=num_questions,
    )
    st.session_state.question_ids = picked_ids


def get_question_by_id(question_id: str) -> Question:
    """
    Retrieve a question dictionary from the pool by its identifier.

    Keeping this in a dedicated function makes error handling easier and
    avoids duplicating the search logic.

    Parameters
    ----------
    question_id:
        Identifier of the question.

    Returns
    -------
    Question
        Question entry corresponding to the identifier.

    Raises
    ------
    KeyError
        If no question with the given identifier exists.
    """
    try:
        return next(
            question for question in QUESTION_POOL if question["id"] == question_id
        )
    except StopIteration as exc:
        # Fail fast with a clear error message if the ID is invalid.
        raise KeyError(f"Unknown question id: {question_id}") from exc


def award_badges() -> None:
    """
    Award badges at the end of the quiz based on the user's performance.

    Badges are derived from score, streak and power-up usage and are stored
    in session state for display in the result screen.
    """
    if st.session_state.score >= BADGE_SCORE_APPRENTICE:
        st.session_state.badges.add("🏅 PEP Apprentice")

    if st.session_state.score >= BADGE_SCORE_PRO:
        st.session_state.badges.add("🥇 PEP Pro")

    if st.session_state.streak >= BADGE_STREAK_THRESHOLD:
        st.session_state.badges.add("🔥 Streak Master (3+)")

    # Only award the no-hint badge if the player completed all questions.
    if (
        st.session_state.hints_used == 0
        and st.session_state.q_index == len(st.session_state.question_ids)
    ):
        st.session_state.badges.add("🧠 No-Hint Hero")

    # Badge that shows the player tried the 50/50 power-up at least once.
    if st.session_state.used_5050:
        st.session_state.badges.add("🪓 50/50 User")


def reset_question_powerups() -> None:
    """
    Reset state variables related to per-question power-ups.

    This is called when moving to a new question so that effects like
    50/50 or hints do not accidentally carry over.
    """
    st.session_state.answered = False
    st.session_state.used_5050 = False
    st.session_state.eliminated_options = set()
    st.session_state.show_hint = False
    st.session_state.shop_buys = []


def apply_5050(question: Question) -> None:
    """
    Apply a 50/50 reduction to the current multiple-choice options.

    Two incorrect options are removed from the available choices. This
    modifies the session state so the UI can hide those options.

    Parameters
    ----------
    question:
        Question entry containing the answer index and options.
    """
    wrong_indices = [
        index
        for index in range(len(question["options"]))
        if index != question["answer_idx"]
    ]

    # Guard in case a question has fewer than three options in the future.
    num_to_eliminate = min(2, len(wrong_indices))

    # Randomly choose which incorrect answers to remove.
    eliminated = set(random.sample(wrong_indices, k=num_to_eliminate))

    st.session_state.eliminated_options = eliminated
    st.session_state.used_5050 = True


def get_visible_option_indices(question: Question) -> List[int]:
    """
    Return the indices of options that should be displayed to the user.

    If 50/50 has been used, only the remaining options are shown. Otherwise,
    all options are visible.

    Parameters
    ----------
    question:
        Question entry containing available options.

    Returns
    -------
    list[int]
        Indices of options that are currently available for selection.
    """
    if not st.session_state.used_5050:
        return list(range(len(question["options"])))

    return [
        index
        for index in range(len(question["options"]))
        if index not in st.session_state.eliminated_options
    ]


def coins_for_correct() -> int:
    """
    Compute the number of coins awarded for a correct answer.

    The reward scales with the current streak but is capped to avoid
    extreme growth.

    Returns
    -------
    int
        Number of coins earned based on a base value and the current streak.
    """
    streak_bonus = min(st.session_state.streak, MAX_STREAK_BONUS)
    return BASE_COIN_REWARD + streak_bonus


# -----------------------------------------------------------------------------
# Main user interface
# -----------------------------------------------------------------------------

def main() -> None:
    """
    Render the PEP Quiz Arcade page.

    Important: Do not call st.set_page_config() here because this module is
    used as a subpage in a multipage router that sets page config centrally.
    """
    # Initialize all required session state variables before rendering any UI.
    init_state()

    current_monster = (
        get_monster(st.session_state.selected_monster)
        if st.session_state.selected_monster
        else None
    )

    # Main app title and subtitle.
    st.title("🐍 PEP Quiz Arcade")
    st.caption("Answer PEP 8 questions, collect coins, and unlock cosmetic monsters.")

    # If the user has selected a monster, show it in a small header card.
    if current_monster:
        top_col_img, top_col_info = st.columns([1, 3])
        with top_col_img:
            if current_monster.get("image"):
                st.image(current_monster["image"], width=80)
        with top_col_info:
            st.info(
                f"Current monster: {current_monster['emoji']} "
                f"{current_monster['name']} – {current_monster['description']}"
            )

    # Split the upper area into quiz settings and the power-up shop.
    settings_col, shop_col = st.columns([2, 1])

    with settings_col:
        st.subheader("Quiz settings")

        # Slider allows the user to choose how many questions the game will have.
        st.session_state.num_questions = st.slider(
            "Questions per game",
            MIN_QUESTIONS_PER_GAME,
            min(MAX_QUESTIONS_PER_GAME, len(QUESTION_POOL)),
            st.session_state.num_questions,
        )

        # Button to start a new game and reset the state.
        if st.button("New game"):
            start_new_game()
            st.rerun()

    with shop_col:
        st.subheader("Power-up shop")
        st.write(f"Coins: {st.session_state.coins} 🪙")

        col_left, col_right = st.columns(2)

        with col_left:
            # Hint reveals the topic of the current question to guide the user.
            if st.button(
                f"Hint ({HINT_COST})",
                disabled=(
                    st.session_state.coins < HINT_COST
                    or not st.session_state.started
                    or st.session_state.answered
                ),
            ):
                st.session_state.coins -= HINT_COST
                st.session_state.hints_used += 1
                st.session_state.shop_buys.append("Hint")
                st.session_state.show_hint = True

            # Skip allows moving on without affecting the score, but resets the streak.
            if st.button(
                f"Skip ({SKIP_COST})",
                disabled=(
                    st.session_state.coins < SKIP_COST
                    or not st.session_state.started
                    or st.session_state.answered
                ),
            ):
                st.session_state.coins -= SKIP_COST
                st.session_state.skips_used += 1
                st.session_state.shop_buys.append("Skip")
                st.session_state.last_correct = None
                st.session_state.streak = 0
                st.session_state.answered = True

        with col_right:
            # 50/50 removes two incorrect options on the current question.
            if st.button(
                f"50/50 ({FIFTY_FIFTY_COST})",
                disabled=(
                    st.session_state.coins < FIFTY_FIFTY_COST
                    or not st.session_state.started
                    or st.session_state.answered
                    or st.session_state.used_5050
                ),
            ):
                st.session_state.coins -= FIFTY_FIFTY_COST
                st.session_state.shop_buys.append("50/50")

    st.markdown("---")

    # If the game has not started yet, prompt the user to start it.
    if not st.session_state.started:
        st.info("Start a new game using the controls above.")
    else:
        total_questions = len(st.session_state.question_ids)
        current_index = st.session_state.q_index

        # Handle the case where the user used "Skip":
        # we mark the question as answered with no correctness and then
        # automatically advance to the next question.
        if (
            st.session_state.answered
            and st.session_state.last_correct is None
            and current_index < total_questions
        ):
            st.session_state.q_index += 1
            reset_question_powerups()
            st.rerun()

        # If we've exhausted all questions, show the results screen.
        if current_index >= total_questions:
            award_badges()
            st.success("Quiz finished.")

            st.subheader("Results")
            st.write(f"Score: {st.session_state.score} / {total_questions}")
            st.write(f"Coins: {st.session_state.coins} 🪙")
            st.write(f"Best streak: {st.session_state.streak}")

            score_ratio = st.session_state.score / total_questions
            if score_ratio <= 0.4:
                st.write("Summary: Basic familiarity with PEP 8.")
            elif score_ratio <= 0.75:
                st.write("Summary: Solid understanding of PEP 8.")
            else:
                st.write("Summary: Very strong understanding of PEP 8.")

            if st.session_state.badges:
                st.subheader("Badges")
                st.write(" • " + "\n • ".join(sorted(st.session_state.badges)))

            st.divider()
            if st.button("Play again", use_container_width=True):
                start_new_game()
                st.rerun()
        else:
            # Retrieve the current question based on the stored ID order.
            question_id = st.session_state.question_ids[current_index]
            question = get_question_by_id(question_id)

            # If the user bought 50/50 for this question, apply it once.
            if "50/50" in st.session_state.shop_buys and not st.session_state.used_5050:
                st.session_state.shop_buys.remove("50/50")
                apply_5050(question)

            # Heads-up display with basic game stats.
            hud1, hud2, hud3, hud4 = st.columns(4)
            hud1.metric("Question", f"{current_index + 1}/{total_questions}")
            hud2.metric("Score", st.session_state.score)
            hud3.metric("Coins", f"{st.session_state.coins} 🪙")
            hud4.metric("Streak", st.session_state.streak)

            st.subheader(question["prompt"])

            # Optional code snippet that illustrates the question.
            if question.get("code"):
                st.code(question["code"], language="python")

            # When a hint is activated, show the question topic.
            if st.session_state.show_hint:
                st.warning(f"Topic: {question['topic']}")

            # Filter visible options depending on whether 50/50 was used.
            option_indices = get_visible_option_indices(question)
            visible_options = [question["options"][i] for i in option_indices]

            # We store the selected index in Streamlit state using a unique key
            # per question to avoid collisions across reruns.
            selected_index = st.radio(
                "Choose an answer:",
                options=list(range(len(visible_options))),
                format_func=lambda i: visible_options[i],
                key=f"radio_{question_id}",
                disabled=st.session_state.answered,
            )

            submit_col, next_col = st.columns([1, 1])

            with submit_col:
                # The Submit button locks in the current choice.
                if st.button(
                    "Submit",
                    use_container_width=True,
                    disabled=st.session_state.answered,
                ):
                    chosen_original_idx = option_indices[selected_index]
                    is_correct = chosen_original_idx == question["answer_idx"]
                    st.session_state.answered = True
                    st.session_state.last_correct = is_correct

                    if is_correct:
                        st.session_state.score += 1
                        st.session_state.streak += 1
                        coins_earned = coins_for_correct()
                        st.session_state.coins += coins_earned
                    else:
                        # Wrong answers reset the streak.
                        st.session_state.streak = 0

            with next_col:
                # The Next button moves to the next question after submission.
                if st.button(
                    "Next",
                    use_container_width=True,
                    disabled=not st.session_state.answered,
                ):
                    st.session_state.q_index += 1
                    reset_question_powerups()
                    st.rerun()

            # After submission, provide feedback and explanation.
            if st.session_state.answered:
                if st.session_state.last_correct:
                    st.success("Answer is correct.")
                    st.write(f"Coins earned for this question: {coins_for_correct()}")
                else:
                    st.error("Answer is not correct.")

                st.write(f"Explanation: {question['explanation']}")

    st.divider()

    # -----------------------------------------------------------------------------
    # Monster shop user interface
    # -----------------------------------------------------------------------------
    # This section lets players spend coins on purely cosmetic monsters that are
    # shown at the top of the quiz screen.
    st.subheader("Monster shop")

    st.write(
        "Coins can be used to unlock and select cosmetic monsters that are "
        "displayed during the quiz."
    )
    st.write(f"Current coins: {st.session_state.coins} 🪙")

    monster_columns = st.columns(2)

    for index, monster in enumerate(MONSTER_SHOP):
        column = monster_columns[index % 2]
        with column:
            if monster.get("image"):
                st.image(monster["image"], width=140)
            st.markdown(f"### {monster['emoji']} {monster['name']}")
            st.write(f"Price: {monster['price']} 🪙")
            st.caption(monster["description"])

            owned = monster["id"] in st.session_state.monsters_owned

            if owned:
                # If already owned, either show that it is selected or allow selection.
                if st.session_state.selected_monster == monster["id"]:
                    st.button(
                        "Selected",
                        key=f"sel_{monster['id']}",
                        disabled=True,
                    )
                else:
                    if st.button("Select", key=f"sel_{monster['id']}"):
                        st.session_state.selected_monster = monster["id"]
                        st.rerun()
            else:
                # If not owned, allow the user to buy the monster if they have enough coins.
                not_enough_coins = st.session_state.coins < monster["price"]
                button_label = "Not enough coins" if not_enough_coins else "Buy"
                if st.button(
                    button_label,
                    key=f"buy_{monster['id']}",
                    disabled=not_enough_coins,
                ):
                    st.session_state.coins -= monster["price"]
                    st.session_state.monsters_owned.append(monster["id"])
                    st.session_state.selected_monster = monster["id"]
                    st.session_state.badges.add(BADGE_MONSTER_COLLECTOR)
                    st.rerun()


# Execution support
if __name__ == "__main__":
    st.set_page_config(
        page_title="PEP Quiz Arcade",
        page_icon="🐍",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()
