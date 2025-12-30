"""
Streamlit application for LLM-based code quality analysis.

The app allows users to paste source code, configure review settings, and
receive a structured evaluation of code quality along multiple dimensions.
Optionally, it also generates a refactored version of the code.
"""

import json
import textwrap
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from openai import OpenAI

# =============================================================================
# Configuration
# =============================================================================

# Hard-coded OpenAI configuration, so use is only possible in private, not meant for shared code
# We are very aware that this is not best practice, but it is easiest for you to test, so we kept it that way anyway
# You simply need to copy paste the API key we provided in the message here
# The limit for the API is set to a few Euros, so feel free to play around with it as much as you want
OPENAI_API_KEY: str = "PLACEHOLDER -> PLEASE EXCHANGE WITH THE CODE FROM THE MESSAGE ON CODINGXCAMP"

# Model names used for analysis and refactoring
MODEL_NAME_ANALYSIS: str = "gpt-5.2"
MODEL_NAME_REFACTOR: str = "gpt-5-nano"


def get_client():
    """
    Create an OpenAI client instance if an API key is configured

    Returns
    -------
    OpenAI client when the API key is available, otherwise None
    """
    if not OPENAI_API_KEY:
        st.error(
            "No OpenAI API key configured. Please set the OPENAI_API_KEY "
            "environment variable or configure it in the source code."
        )
        return None

    return OpenAI(api_key=OPENAI_API_KEY)


# =============================================================================
# Prompt design
# =============================================================================


def build_analysis_messages(
    code: str,
    language_hint: str,
    review_level: str,
    persona: str,
    explanation_language: str,
) -> List[Dict[str, str]]:
    """
    Build the messages for the analysis request.

    This prompt enforces a single baseline scoring standard (intermediate),
    then applies a fixed overall_score adjustment of +20 or -20 depending on
    the selected review level.
    """
    system_prompt = textwrap.dedent(
        f"""
        You are an experienced software engineer and code-quality reviewer.
        Your job is to evaluate a code snippet and produce a helpful, encouraging review.

        Persona: {persona}
        Review level: {review_level}
        All text language: {explanation_language}
        Code language hint: "{language_hint}" (may be "Auto"; infer from the snippet if needed)

        IMPORTANT OUTPUT RULES
        1) Respond with ONLY valid JSON. No markdown. No extra text.
        2) JSON must match the schema exactly (keys and types).
        3) All scores must be integers.

        GOAL AND TONE
        - Be constructive and friendly.
        - Be lenient with small mistakes and minor style issues.
        - Give credit where credit is due.
        - Reserve low scores for real problems that materially harm correctness, clarity, maintainability, or safety.

        DIMENSIONS TO SCORE (0–10, integers only)
        - readability
        - naming
        - structure
        - comments
        - robustness
        - testability
        - performance
        - security

        ANCHORS (use consistently)
        - 0–2  very poor: broken, unsafe, or extremely difficult to understand/maintain
        - 3–4  poor: major issues that significantly hinder use or safety
        - 5–6  adequate: workable but with clear, meaningful weaknesses
        - 7–8  good: solid quality with only minor issues
        - 9–10 excellent: clean, idiomatic, robust, and well-structured

        LENIENCY CALIBRATION
        - Typical reasonable code should often land around 6–8 per dimension.
        - Scores below 5 should be uncommon and must be justified by concrete issues.
        - Do not penalize for missing “enterprise” practices unless their absence creates real risk.

        REVIEW LEVEL HANDLING (THIS MUST CREATE REAL DIFFERENCES)
        Step 1: Always evaluate the code using ONE baseline standard called "intermediate".
                This means your dimension scores and dimension comments are always written as if the reviewer is intermediate.
                Do NOT change dimension scores based on level.

        Step 2: Compute a BASE overall_score from the dimension scores:
                - base_overall = round(average_dimension_score * 10)
                - Clamp base_overall to 0..100
                - Keep in mind, code from an average university student receives around 70 points

        Step 3: Apply a fixed adjustment to overall_score based on review_level:
                - If review_level is beginner-friendly: overall_score = base_overall + 20
                - If review_level is intermediate: overall_score = base_overall
                - If review_level is senior or very strict: overall_score = base_overall - 20
                - Clamp overall_score to 0..100

        Mapping rules:
        - Map any unknown label to the closest of: beginner-friendly, intermediate, senior or very strict.

        WHAT TO RETURN
        - summary.short_overview: 2–4 sentences
        - summary.key_strengths: 3–5 strings
        - summary.key_issues: 3–5 strings
        - summary.top_recommendation: one sentence

        learning_tips:
        - Provide 2–3 items.
        - Each must include title, description, bad_example, better_example.
        - Tailor the wording complexity to the review level:
          beginner-friendly uses simpler language, senior or very strict uses more professional wording.
          Do not change scores for this, only the phrasing and emphasis.

        JSON SCHEMA (keys and types must match exactly)
        {{
          "language": "string (your best guess, e.g. 'python', 'java')",
          "overall_score": 0,
          "summary": {{
            "short_overview": "string",
            "key_strengths": ["string", "..."],
            "key_issues": ["string", "..."],
            "top_recommendation": "string"
          }},
          "dimensions": {{
            "readability": {{ "score": 0, "comment": "string" }},
            "naming": {{ "score": 0, "comment": "string" }},
            "structure": {{ "score": 0, "comment": "string" }},
            "comments": {{ "score": 0, "comment": "string" }},
            "robustness": {{ "score": 0, "comment": "string" }},
            "testability": {{ "score": 0, "comment": "string" }},
            "performance": {{ "score": 0, "comment": "string" }},
            "security": {{ "score": 0, "comment": "string" }}
          }},
          "learning_tips": [
            {{
              "title": "string",
              "description": "string",
              "bad_example": "string with code",
              "better_example": "string with code"
            }}
          ]
        }}

        Final validation checklist before you respond
        - Valid JSON only, parseable by json.loads
        - All text is in {explanation_language}
        - Dimension scores are integers and reflect the intermediate baseline
        - overall_score equals base_overall plus the fixed level adjustment (+20/0/-20), clamped to 0..100
        """
    ).strip()

    user_prompt = textwrap.dedent(
        f"""
        Review the following code snippet. Provide your response strictly as JSON:

        {code}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_refactor_messages(
    code: str,
    detected_language: str,
    review_level: str,
    persona: str,
) -> List[Dict[str, str]]:
    """
    Build the messages for the refactoring request.

    The system prompt explains how the model should improve the code
    without changing its external behavior.
    """
    system_prompt = textwrap.dedent(
        f"""
        You are a senior software engineer.
        Your task is to rewrite the user's code to improve code quality
        while preserving behavior.

        Perspective / persona: {persona}
        Strictness level: {review_level}

        Requirements:
        - Keep the same programming language (detected: "{detected_language}", adjust only if obviously wrong).
        - Improve readability, naming, structure, comments, robustness, and testability as appropriate.
        - Do NOT change external behavior or public interfaces unless strictly necessary.
        - Prefer small, clear functions and meaningful names.
        - Add minimal but helpful comments / docstrings, not excessive noise.
        - Do not invent new functionality.

        OUTPUT FORMAT:
        - Return ONLY the improved code.
        - Do NOT include explanations, markdown, or commentary outside the code itself.
        """
    )

    user_prompt = f"Please refactor the following code:\n\n```code\n{code}\n```"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# =============================================================================
# OpenAI wrapper functions
# =============================================================================

def run_analysis(
    client: OpenAI,
    code: str,
    language_hint: str,
    review_level: str,
    persona: str,
    explanation_language: str,
) -> Dict[str, Any]:
    """
    Send the analysis request to the OpenAI API and return the parsed JSON.

    On error, an empty dictionary is returned and an error message is shown
    in the Streamlit interface.
    """
    messages = build_analysis_messages(
        code=code,
        language_hint=language_hint,
        review_level=review_level,
        persona=persona,
        explanation_language=explanation_language,
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME_ANALYSIS,
            messages=messages,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        return json.loads(content)
    except Exception as error:  # noqa: BLE001
        st.error(f"Error during analysis: {error}")
        return {}


def run_refactor(
    client: OpenAI,
    code: str,
    detected_language: str,
    review_level: str,
    persona: str,
) -> str:
    """
    Send the refactoring request to the OpenAI API and return the new code.

    On error, an empty string is returned and an error message is shown
    in the Streamlit interface.
    """
    messages = build_refactor_messages(
        code=code,
        detected_language=detected_language,
        review_level=review_level,
        persona=persona,
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME_REFACTOR,
            messages=messages,
        )
        return completion.choices[0].message.content
    except Exception as error:  # noqa: BLE001
        st.error(f"Error during refactoring: {error}")
        return ""


# =============================================================================
# Scoring helpers for UI (traffic light)
# =============================================================================

def get_quality_level(score: int) -> Tuple[str, str, str]:
    """
    Map an overall score (0–100) to a label and a color for the traffic light.

    Returns
    -------
    Tuple[str, str, str]
        (label, description, hex_color)
    """
    if score < 40:
        return (
            "Poor",
            "Code quality is poor. Serious refactoring is strongly recommended "
            "before using this code in production or teaching.",
            "#c0392b",
        )
    if score < 60:
        return (
            "Below average",
            "Code is usable but has significant weaknesses. It should be improved "
            "to meet common best practices.",
            "#e67e22",
        )
    if score < 80:
        return (
            "Acceptable",
            "Code quality is acceptable. It follows some best practices, but there "
            "is still clear potential for improvement.",
            "#f1c40f",
        )
    if score < 90:
        return (
            "Good",
            "Code quality is good. It follows most relevant best practices with "
            "only minor improvement opportunities.",
            "#27ae60",
        )
    return (
        "Excellent",
        "Code quality is excellent. It is clear, well-structured, robust and "
        "close to what an experienced engineer would write.",
        "#2ecc71",
    )


# =============================================================================
# Streamlit UI
# =============================================================================

def main() -> None:
    """
    Render the Code Quality Checker page.
    """
    st.title("🔍 Code Quality Checker")
    st.write(
        "Paste your source code below to obtain an automatic, LLM-based review "
        "along multiple code quality dimensions."
    )

    # Explanation of scoring and the traffic light system
    with st.expander("How the scoring and traffic light system work"):
        st.markdown(
            """
            **Overall score (0–100)** is derived from eight dimensions (0–10 each):

            - **Readability** – clarity of control flow, formatting, and structure.
            - **Naming** – meaningful and consistent names for variables, functions, and classes.
            - **Structure** – modularity, separation of concerns, and function size.
            - **Comments** – useful, accurate comments and/or docstrings that explain intent.
            - **Robustness** – basic input validation, error handling, and defensive checks.
            - **Testability** – how easily core logic can be tested independently of I/O.
            - **Performance** – absence of obvious inefficiencies for the given task.
            - **Security** – absence of obvious unsafe patterns (e.g. unsafe eval, raw SQL string concatenation).

            **Score interpretation and traffic light:**

            - **0–39**   → Poor (red): serious problems, not recommended as-is.
            - **40–59**  → Below average (orange): significant refactoring required.
            - **60–79**  → Acceptable (yellow): usable, but still clear improvement potential.
            - **80–89**  → Good (green): follows most best practices with only minor issues.
            - **90–100** → Excellent (bright green): very good, idiomatic, and robust code.
            """
        )

    # Sidebar configuration controls
    with st.sidebar:
        st.header("Configuration")

        language_hint = st.selectbox(
            "Programming language (hint)",
            [
                "Auto",
                "python",
                "java",
                "javascript",
                "typescript",
                "c++",
                "c",
                "csharp",
                "go",
                "rust",
                "php",
                "ruby",
            ],
            index=0,
        )

        review_level = st.selectbox(
            "Review level",
            ["Beginner-friendly", "Intermediate", "Senior / very strict"],
            index=0,
        )

        persona = st.selectbox(
            "Reviewer persona",
            [
                "Balanced senior engineer",
                "Strict clean-code purist",
                "Performance-focused engineer",
                "Beginner-friendly code coach",
            ],
            index=0,
        )

        explanation_language_ui = st.selectbox(
            "Feedback language",
            ["English", "Deutsch"],
            index=0,
        )
        explanation_language = (
            "German" if explanation_language_ui == "Deutsch" else "English"
        )

        selected_dimensions = st.multiselect(
            "Dimensions to display",
            [
                "readability",
                "naming",
                "structure",
                "comments",
                "robustness",
                "testability",
                "performance",
                "security",
            ],
            default=["readability", "naming", "structure", "comments"],
        )

        generate_refactor = st.checkbox("Generate refactored code", value=True)

        st.markdown("---")
        st.caption("OpenAI model used for analysis:")
        st.text(MODEL_NAME_ANALYSIS)

    # Main input area for the code to be analyzed
    code_input = st.text_area(
        "Paste your code here:",
        height=300,
        placeholder="Paste your code snippet here for analysis...",
    )

    analyze_button = st.button("🔎 Analyze code")

    if not analyze_button:
        return

    if not code_input.strip():
        st.warning("Please paste some code before running the analysis.")
        return

    openai_client = get_client()
    if openai_client is None:
        return

    # Run the analysis step and display a spinner while waiting
    with st.spinner("Running code quality analysis..."):
        analysis_result = run_analysis(
            client=openai_client,
            code=code_input,
            language_hint=language_hint,
            review_level=review_level,
            persona=persona,
            explanation_language=explanation_language,
        )

    if not analysis_result:
        return

    detected_language = analysis_result.get("language", language_hint or "text")

    # Generate refactored code if selected
    refactored_code = ""
    if generate_refactor:
        with st.spinner("Generating refactored code..."):
            refactored_code = run_refactor(
                client=openai_client,
                code=code_input,
                detected_language=detected_language,
                review_level=review_level,
                persona=persona,
            )

    # Tabs to separate the main views of the analysis
    tab_overview, tab_details, tab_refactor, tab_learning = st.tabs(
        ["Overview", "Detailed review", "Refactored code", "Learning mode"]
    )

    # ----------------------- Overview tab ---------------------------
    with tab_overview:
        overall_score = int(analysis_result.get("overall_score", 0))
        summary = analysis_result.get("summary", {})
        short_overview = summary.get("short_overview", "")
        key_strengths = summary.get("key_strengths", [])
        key_issues = summary.get("key_issues", [])
        top_recommendation = summary.get("top_recommendation", "")

        quality_label, quality_description, quality_color = get_quality_level(
            overall_score
        )

        col_metric, col_summary = st.columns([1, 3])
        with col_metric:
            st.metric("Overall score", f"{overall_score}/100")

            # Traffic light style element
            st.markdown(
                f"""
                <div style="
                    margin-top: 0.5rem;
                    padding: 0.4rem 0.8rem;
                    border-radius: 0.6rem;
                    background-color: {quality_color};
                    color: #ffffff;
                    font-weight: 600;
                    text-align: center;
                    ">
                    Quality level: {quality_label}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_summary:
            st.write(f"**Summary:** {short_overview}")
            st.caption(quality_description)

        dimensions = analysis_result.get("dimensions", {})
        filtered_dimensions = {
            name: data
            for name, data in dimensions.items()
            if name in selected_dimensions
        }

        st.divider()

        if filtered_dimensions:
            st.subheader("Dimension scores")
            df_scores = pd.DataFrame(
                {
                    "Dimension": list(filtered_dimensions.keys()),
                    "Score (0–10)": [
                        dim.get("score", 0) for dim in filtered_dimensions.values()
                    ],
                }
            ).set_index("Dimension")
            st.bar_chart(df_scores)

        st.divider()

        col_strengths, col_issues = st.columns(2)
        with col_strengths:
            st.subheader("Key strengths")
            if key_strengths:
                for strength in key_strengths:
                    st.markdown(f"- {strength}")
            else:
                st.write("No specific strengths identified.")

        with col_issues:
            st.subheader("Key issues")
            if key_issues:
                for issue in key_issues:
                    st.markdown(f"- {issue}")
            else:
                st.write("No specific issues identified.")

        st.divider()

        st.subheader("Top recommendation")
        st.write(top_recommendation)

    # --------------------- Detailed review tab ----------------------
    with tab_details:
        st.write("Detailed feedback by dimension:")

        dimensions = analysis_result.get("dimensions", {})
        for dimension_name, dimension_data in dimensions.items():
            if selected_dimensions and dimension_name not in selected_dimensions:
                continue

            score = dimension_data.get("score", 0)
            comment = dimension_data.get("comment", "")
            expander_label = f"{dimension_name} (Score: {score}/10)"
            with st.expander(expander_label, expanded=False):
                st.write(comment)

    # --------------------- Refactored code tab ----------------------
    with tab_refactor:
        if generate_refactor and refactored_code:
            st.write("Proposed refactored version of your code:")
            st.code(refactored_code, language=detected_language or "text")
        elif generate_refactor:
            st.warning("No refactored code could be generated.")
        else:
            st.info(
                "Refactoring is disabled. Enable it in the configuration sidebar."
            )

    # ----------------------- Learning mode tab ----------------------
    with tab_learning:
        st.write(
            "The following learning tips are derived from the analysis. "
            "They are intended to support targeted improvement of your code."
        )
        learning_tips = analysis_result.get("learning_tips", [])
        if not learning_tips:
            st.info("No specific learning tips were provided by the model.")
            return

        for index, tip in enumerate(learning_tips, start=1):
            title = tip.get("title", "")
            description = tip.get("description", "")
            bad_example = tip.get("bad_example", "").strip()
            better_example = tip.get("better_example", "").strip()

            st.markdown(f"### Tip {index}: {title}")
            st.write(description)

            if bad_example:
                st.markdown("**Example of weaker code:**")
                st.code(bad_example, language=detected_language or "text")

            if better_example:
                st.markdown("**Improved example:**")
                st.code(better_example, language=detected_language or "text")


# Execution support
if __name__ == "__main__":
    st.set_page_config(page_title="Code Quality Checker", layout="wide")
    main()
