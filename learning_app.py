"""
Streamlit app: Code Quality Guidelines

This module renders:
1) A set of code-quality guidelines with "bad vs good" examples.
2) Two lightweight visuals:
   - A radar chart showing guideline "focus" weights.
   - A heatmap showing guideline impact on broader quality outcomes.
"""

import math
from typing import List, Sequence

import matplotlib.pyplot as plt
import streamlit as st


# -----------------------------
# App configuration and data
# -----------------------------

APP_TITLE = "Code Quality Guidelines"

# These focus weights reflect how a beginner-friendly review might prioritize each guideline.
FOCUS_WEIGHTS: List[int] = [88, 78, 74, 85, 80, 87]

GUIDELINES: List[str] = [
    "Readable naming",
    "Effective comments",
    "No hardcoding",
    "Small functions",
    "Consistent style",
    "Input validation",
]

OUTCOMES: List[str] = ["Readability", "Maintainability", "Flexibility", "Reliability"]

# Impact scale: 0–5 (higher means stronger impact on the outcome).
IMPACT_MAP: List[List[int]] = [
    [5, 4, 2, 2],
    [4, 4, 2, 2],
    [2, 4, 5, 2],
    [4, 5, 3, 3],
    [5, 4, 2, 2],
    [2, 3, 2, 5],
]


# -----------------------------
# Validation helpers
# -----------------------------

def _require_non_empty_labels(labels: Sequence[str], name: str) -> None:
    """
    Ensure a list/sequence of labels is present and non-empty.

    Parameters
    ----------
    labels:
        Label strings.
    name:
        Human-readable name used for error messaging.
    """
    if not labels:
        raise ValueError(f"{name} must not be empty.")
    if any(not isinstance(label, str) or not label.strip() for label in labels):
        raise ValueError(f"{name} must contain non-empty strings.")


def _require_matrix_shape(
    data: Sequence[Sequence[int]],
    expected_rows: int,
    expected_cols: int,
) -> None:
    """
    Validate that a matrix has the expected shape.

    Parameters
    ----------
    data:
        2D matrix-like structure.
    expected_rows:
        Required number of rows.
    expected_cols:
        Required number of columns.
    """
    if len(data) != expected_rows:
        raise ValueError("Data row count must match the number of row labels.")
    for row in data:
        if len(row) != expected_cols:
            raise ValueError("Each data row must match the number of column labels.")


# -----------------------------
# Chart rendering
# -----------------------------

def create_radar_chart(
    labels: Sequence[str],
    values: Sequence[int],
    title: str = "",
) -> plt.Figure:
    """
    Create a radar (spider) chart.

    Parameters
    ----------
    labels:
        Axis labels.
    values:
        Values corresponding to each label.
    title:
        Optional chart title.

    Returns
    -------
    matplotlib.figure.Figure
        The rendered matplotlib figure.
    """
    _require_non_empty_labels(labels, name="Labels")

    if len(labels) != len(values):
        raise ValueError("Labels and values must match in length.")

    # Compute angles around the circle and repeat the first point to close the polygon.
    angles = [2 * math.pi * i / len(labels) for i in range(len(labels))]
    angles.append(angles[0])

    values_list = list(values)
    values_closed = values_list + [values_list[0]]

    fig = plt.figure(figsize=(7.2, 4.8))
    ax = fig.add_subplot(111, polar=True)

    ax.plot(angles, values_closed, linewidth=2)
    ax.fill(angles, values_closed, alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(list(labels), fontsize=10)

    # Polar charts often need extra padding for readable labels.
    ax.tick_params(axis="x", pad=14)

    ax.set_ylim(0, 110)
    ax.set_yticks([20, 40, 60, 80, 100])

    # Subtle grid for readability without overwhelming the chart.
    ax.grid(True, alpha=0.25)

    if title:
        ax.set_title(title, pad=16)

    fig.subplots_adjust(left=0.08, right=0.92, top=0.86, bottom=0.12)
    return fig


def create_heatmap_chart(
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    data: Sequence[Sequence[int]],
    title: str = "",
) -> plt.Figure:
    """
    Create a heatmap chart with cell annotations.

    Parameters
    ----------
    row_labels:
        Labels for each row.
    col_labels:
        Labels for each column.
    data:
        Matrix of values with shape (len(row_labels), len(col_labels)).
    title:
        Optional chart title.

    Returns
    -------
    matplotlib.figure.Figure
        The rendered matplotlib figure.
    """
    _require_non_empty_labels(row_labels, name="Row labels")
    _require_non_empty_labels(col_labels, name="Column labels")
    _require_matrix_shape(
        data,
        expected_rows=len(row_labels),
        expected_cols=len(col_labels),
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    image = ax.imshow(data, aspect="auto", cmap="Blues", vmin=0, vmax=5)

    if title:
        ax.set_title(title, pad=10)

    ax.set_xlabel("Quality outcome")
    ax.set_ylabel("Guideline")

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(list(col_labels), fontsize=10)

    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(list(row_labels), fontsize=10)

    # Annotate each cell with its numeric impact score for quick interpretation.
    for row_idx, row in enumerate(data):
        for col_idx, value in enumerate(row):
            ax.text(col_idx, row_idx, value, ha="center", va="center", fontsize=9)

    # Light gridlines improve scanning across rows/columns.
    ax.set_xticks([x - 0.5 for x in range(1, len(col_labels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(row_labels))], minor=True)
    ax.grid(which="minor", linestyle="-", linewidth=0.6, alpha=0.25)
    ax.tick_params(which="minor", bottom=False, left=False)

    fig.colorbar(image, ax=ax, shrink=0.9, label="Impact (0–5)")
    fig.tight_layout()
    return fig


# -----------------------------
# UI building blocks
# -----------------------------

def render_example_section(
    title: str,
    bullets: Sequence[str],
    bad_code: str,
    good_code: str,
) -> None:
    """
    Render a guideline section with bullet points and side-by-side examples.

    Parameters
    ----------
    title:
        Section title shown as a header.
    bullets:
        Bullet points explaining the guideline intent.
    bad_code:
        Code snippet showing the anti-pattern.
    good_code:
        Code snippet showing the recommended pattern.
    """
    st.markdown(f"### {title}")
    st.markdown("\n".join(f"- {bullet}" for bullet in bullets))

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("**Bad example**")
        st.code(bad_code, language="python")

    with right_col:
        st.markdown("**Good example**")
        st.code(good_code, language="python")


def render_guidelines() -> None:
    """
    Render the guideline overview and the example sections.
    """
    st.markdown("## Overview")

    # Overview cards help users understand the purpose quickly.
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            "<div class='metric-card'><div class='metric-title'>Clarity</div>"
            "<div class='metric-text'>Improve readability and consistency.</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            "<div class='metric-card'><div class='metric-title'>Safety</div>"
            "<div class='metric-text'>Make changes safer and cheaper.</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            "<div class='metric-card'><div class='metric-title'>Prevention</div>"
            "<div class='metric-text'>Avoid common mistakes early.</div></div>",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            "<div class='metric-card'><div class='metric-title'>Collaboration</div>"
            "<div class='metric-text'>Keep code easy to review in a team.</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        render_example_section(
            title="Readable structure",
            bullets=[
                "Use names that communicate intent",
                "Avoid ambiguous shortcuts",
                "Prefer simple flow over clever tricks",
            ],
            bad_code="def f(x):\n    return x * 3.14",
            good_code=(
                "PI = 3.14159\n\n"
                "def calculate_circle_area(radius: float) -> float:\n"
                "    return PI * radius ** 2"
            ),
        )

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        render_example_section(
            title="Meaningful comments",
            bullets=[
                "Add notes for reasoning or constraints",
                "Skip commentary that restates the code",
                "Use docstrings for non-trivial functions",
            ],
            bad_code="total = price + tax  # add tax",
            good_code=(
                "def calculate_total(price: float, tax_rate: float) -> float:\n"
                '    """Return the final price including tax."""\n'
                "    return price * (1 + tax_rate)"
            ),
        )

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        render_example_section(
            title="Avoid hidden rules (no hardcoding)",
            bullets=[
                "Fixed numbers often represent a rule or assumption",
                "Expose rules as parameters or defaults",
                "This makes the code easier to adapt later",
            ],
            bad_code="def discount(price):\n    return price * 0.9",
            good_code=(
                "def discount(price: float, rate: float = 0.1) -> float:\n"
                "    return price * (1 - rate)"
            ),
        )

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        render_example_section(
            title="Small, focused functions",
            bullets=[
                "One function should do one job",
                "Keep logic separate from output / I/O",
                "Smaller pieces are easier to test",
            ],
            bad_code=(
                "def process(items):\n"
                "    for item in items:\n"
                "        print(item * 2)"
            ),
            good_code=(
                "def double_items(items: List[int]) -> List[int]:\n"
                "    return [item * 2 for item in items]"
            ),
        )

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        render_example_section(
            title="Defensive programming",
            bullets=[
                "Validate important inputs",
                "Handle edge cases explicitly",
                "Fail clearly instead of silently",
            ],
            bad_code="def divide(a, b):\n    return a / b",
            good_code=(
                "def divide(a: float, b: float) -> float:\n"
                "    if b == 0:\n"
                "        raise ValueError('b must not be zero')\n"
                "    return a / b"
            ),
        )


def render_visuals() -> None:
    """
    Render the radar and heatmap visuals.
    """
    st.markdown("## Visual summary")
    st.caption(
        "The charts below use placeholder values to illustrate how guidelines can "
        "map to broader quality outcomes."
    )

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        with st.container(border=True):
            st.markdown("<div class='panel-title'>Guideline focus</div>", unsafe_allow_html=True)
            st.caption("Relative emphasis across the guideline set.")
            figure = create_radar_chart(GUIDELINES, FOCUS_WEIGHTS, title="")
            st.pyplot(figure, use_container_width=True)

    with right_col:
        with st.container(border=True):
            st.markdown("<div class='panel-title'>Impact on outcomes</div>", unsafe_allow_html=True)
            st.caption("How each guideline contributes to common quality goals.")
            figure = create_heatmap_chart(GUIDELINES, OUTCOMES, IMPACT_MAP, title="")
            st.pyplot(figure, use_container_width=True)


# -----------------------------
# App entrypoint
# -----------------------------

def _inject_global_css() -> None:
    """
    Inject CSS helpers for spacing and a consistent visual style.

    Streamlit does not provide a dedicated spacing primitive, so a small helper
    class keeps spacing consistent without repeating inline styles.
    """
    st.markdown(
        """
        <style>
        .block-container { padding-top: 2.0rem; padding-bottom: 2.0rem; }
        .spacer { height: 1.0rem; }

        /* Typography */
        h1, h2, h3 { letter-spacing: -0.02em; }
        .stCaption { opacity: 0.85; }

        /* Card-like elements */
        .metric-card {
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 14px;
            padding: 14px 14px 12px 14px;
            background: rgba(255,255,255,0.65);
            box-shadow: 0 1px 10px rgba(0,0,0,0.04);
            min-height: 84px;
        }
        .metric-title {
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 6px;
        }
        .metric-text {
            font-size: 0.90rem;
            line-height: 1.25rem;
            opacity: 0.9;
        }

        .panel-title {
            font-weight: 750;
            font-size: 1.05rem;
            margin-bottom: 0.2rem;
        }

        /* Improve code block readability slightly */
        pre { border-radius: 12px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """
    Render the Code Quality Guidelines page.

    The page is designed to be callable from a multipage router, so page-level
    configuration is applied only for standalone execution.
    """
    _inject_global_css()

    # Header section provides quick context before the detailed examples.
    st.markdown(f"<div class='hero'><h1>{APP_TITLE}</h1></div>", unsafe_allow_html=True)
    st.caption(
        "A compact reference of practical guidelines and visual summaries for code quality."
    )

    tabs = st.tabs(["Guidelines", "Visuals"])
    with tabs[0]:
        render_guidelines()
    with tabs[1]:
        render_visuals()


# Execution support
if __name__ == "__main__":
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    main()
