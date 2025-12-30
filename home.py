"""
Home entrypoint for a multi-page Streamlit app.

Run:
    streamlit run home.py

This file uses Streamlit's navigation API to expose each app as a subpage.
Each subpage is implemented as a callable `main()` function inside its module.
"""

import importlib
from typing import Callable

import streamlit as st


def _render_home() -> None:
    """
    Render a simple landing page.
    """
    st.title("CodeScore Suite")
    st.write(
        """
        Use the navigation in the sidebar to open one of the sub-apps:

        - **Code Checker**: run code reviews / scoring
        - **Learning App**: guidelines and visuals
        - **Arcade**: PEP 8 quiz with coins and monsters
        """
    )
    st.info(
        "Tip: If you do not see the sidebar, expand it using the arrow in the top-left."
    )


def _load_page_callable(module_name: str, entrypoint: str = "main") -> Callable[[], None]:
    """
    Import a module and return its page entrypoint function.

    Each subpage module is expected to expose a `main()` function that renders its UI.
    """
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        st.error(
            f"Could not import '{module_name}'. Ensure '{module_name}.py' is in the "
            "same folder as home.py."
        )
        st.stop()

    page_fn = getattr(module, entrypoint, None)
    if not callable(page_fn):
        st.error(
            f"Module '{module_name}' does not define a callable '{entrypoint}()'. "
            "Ensure the file exposes a 'main()' function."
        )
        st.stop()

    return page_fn


def main() -> None:
    """
    App entrypoint.

    This creates a navigation menu with 4 pages:
    - Home (defined in this file)
    - Code Checker (code_checker.main)
    - Learning App (learning_app.main)
    - Arcade (arcade.main)
    """
    # Configure the app once, centrally, before any UI is rendered.
    st.set_page_config(
        page_title="CodeScore Suite",
        page_icon="✅",
        layout="wide",
    )

    # Load subpages as callables (each page module exposes a `main()` function).
    code_checker_page = _load_page_callable("code_checker")
    learning_page = _load_page_callable("learning_app")
    arcade_page = _load_page_callable("arcade")

    # url_path must be unique across pages. If not set, Streamlit may infer the same
    # pathname from identical callable names (e.g., multiple functions named "main").
    pages = [
        st.Page(_render_home, title="Home", icon="🏠", default=True),
        st.Page(
            code_checker_page,
            title="Code Checker",
            icon="🧪",
            url_path="code-checker",
        ),
        st.Page(
            learning_page,
            title="Learning App",
            icon="📚",
            url_path="learning-app",
        ),
        st.Page(
            arcade_page,
            title="Arcade",
            icon="🕹️",
            url_path="arcade",
        ),
    ]

    navigator = st.navigation(pages, position="sidebar")
    navigator.run()


if __name__ == "__main__":
    main()
