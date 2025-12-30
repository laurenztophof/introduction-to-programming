# Code Quality Learning Hub

## Description

This project was developed as part of the course *“Skills: Programming – Introduction to Programming”* supervised by Dr. Mario Silic.
It was created by the students **Valentin Wressnig**, **Laurenz Tophof**, and **Vincent Neuhaus**.

The Group project is a Streamlit web application designed to support the development of clean, structured, and maintainable Python code. The project combines three complementary components: theoretical guidance, automated code evaluation, and an interactive quiz environment. Together, these elements demonstrate how software tools can promote good programming practices in an accessible and engaging way.

---

## Project Motivation

Beginner programmers often focus primarily on getting code to run, while aspects such as readability, structure, and documentation receive less attention. Over time, this leads to code that is difficult to understand, maintain, and extend.

The goal of this project is to show how:

- coding standards (especially PEP 8),
- automated style evaluation,
- and interactive reinforcement tools

can be integrated into a unified learning platform that encourages better programming habits from the start.

---

## System Overview

The application consists of three main modules, each addressing a different aspect of code quality.

### 1. Code Checker Module

The code checker provides automated analysis of user-submitted Python code.

It evaluates code based on readability, structure, and adherence to style conventions, and produces:

- a numerical quality score (0–100),
- positive observations,
- detected issues,
- and recommendations for improvement.

The module illustrates how automated tools can provide immediate feedback and support reflective learning.

**API key note:** The OpenAI API key is provided in a separate message. To run the Code Checker module, replace the placeholder value in `code_checker.py` with the provided key. The API usage limit is configured to a few Euros.

---

### 2. Guidelines Module

This module introduces essential coding conventions, with emphasis on:

- naming conventions,
- formatting and layout,
- commenting and documentation practices,
- common mistakes and recommended improvements.

It establishes a conceptual baseline that supports the rest of the application.

---

### 3. Arcade Module

The arcade module introduces a gamified multiple-choice quiz focused on PEP 8 concepts and coding quality principles. The quiz system includes:

- questions with explanatory feedback,
- a scoring and reward system,
- optional power-ups,
- and a cosmetic “monster shop”.

While primarily playful, this component demonstrates how game mechanics can be used to sustain motivation and reinforce technical concepts.

---

## Technologies Used

- **Python**
- **Streamlit** for the web interface
- Standard library modules and custom helper functions

## Usage

### Running the Web Application
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
