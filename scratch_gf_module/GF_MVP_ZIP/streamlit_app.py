"""Professional Streamlit interface for the fluid-intelligence assessment."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from analytics import AnalyticsEngine
from logger import EventLogger
from models import AssessmentSession, AssessmentStatus, EventType
from puzzle_engine import AssessmentBuilder
from renderer import SVGRenderer
from scorer import AssessmentScorer
from sdk import AssessmentSDK


st.set_page_config(page_title="Fluid Intelligence Assessment", page_icon="M", layout="wide")


def _state() -> None:
    defaults = {
        "assessment": None, "logger": None, "responses": {}, "current": 0,
        "participant_id": f"student_{uuid4().hex[:10]}", "started_at": None,
        "score": None, "analytics": None, "completed_at": None,
        "last_selection": {}, "page": "Home",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _start() -> None:
    assessment = AssessmentBuilder(seed=int(uuid4().hex[:8], 16)).with_progression(12).build()
    st.session_state.assessment = assessment
    st.session_state.logger = EventLogger(assessment.assessment_id, st.session_state.participant_id)
    st.session_state.responses = {}
    st.session_state.current = 0
    st.session_state.started_at = datetime.now(UTC)
    st.session_state.completed_at = None
    st.session_state.score = None
    st.session_state.analytics = None
    st.session_state.logger.record(EventType.ASSESSMENT_STARTED)


def _begin_assessment() -> None:
    """Create a fresh assessment and navigate away from the landing page."""

    _start()
    st.session_state.page = "Assessment"


def _svg(card, label: str, height: int = 230) -> None:
    """Embed a card in a bounded responsive viewport without SVG clipping."""

    svg = SVGRenderer().render_card(card, aria_label=label)
    document = f"""
    <style>
      html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; }}
      .card-viewport {{
        width: 100%; height: 100%; display: flex;
        align-items: center; justify-content: center;
      }}
      .card-viewport svg {{
        width: 100% !important; height: 100% !important;
        max-width: 800px; display: block;
      }}
    </style>
    <div class="card-viewport">{svg}</div>
    """
    components.html(document, height=height, scrolling=False)


def home_page() -> None:
    st.title("Discover how you reason")
    st.markdown("A visual fluid-intelligence assessment built around patterns, relationships, and hidden rules.")
    left, middle, right = st.columns(3)
    left.metric("Puzzles", "12")
    middle.metric("Typical time", "20-25 min")
    right.metric("Format", "Visual cards")
    st.info("Each puzzle shows examples of a hidden transformation. Infer the rule, then choose the output that follows it. No specialist knowledge is required.")
    st.button(
        "Begin assessment",
        type="primary",
        use_container_width=True,
        on_click=_begin_assessment,
    )


def assessment_page() -> None:
    assessment = st.session_state.assessment
    if assessment is None:
        st.warning("Start an assessment from Home.")
        return
    if st.session_state.score is not None:
        st.success("Assessment complete. Open Results to view your report.")
        return
    index = st.session_state.current
    puzzle = assessment.puzzles[index]
    question = puzzle.question
    start_key = f"started_{question.question_id}"
    if start_key not in st.session_state:
        st.session_state[start_key] = True
        st.session_state.logger.question_started(puzzle.puzzle_id, question.question_id, puzzle.difficulty)
    st.progress(index / len(assessment.puzzles), text=f"Puzzle {index + 1} of {len(assessment.puzzles)}")
    st.subheader("Infer the hidden transformation")
    st.caption(f"Difficulty: {puzzle.difficulty.value.title()} | Study all examples before answering.")
    for example_index, example in enumerate(puzzle.examples, 1):
        st.markdown(f"Example {example_index}")
        source, arrow, target = st.columns([5, 1, 5])
        with source:
            _svg(example.input_card, f"Example {example_index} input")
        arrow.markdown("<div style='font-size:2rem;text-align:center;padding-top:35px'>&rarr;</div>", unsafe_allow_html=True)
        with target:
            _svg(example.output_card, f"Example {example_index} output")
    st.divider()
    st.markdown("Question")
    _svg(question.input_card, "Question input", 250)
    option_ids = [option.option_id for option in question.options]
    labels = {option.option_id: f"Option {chr(65 + i)}" for i, option in enumerate(question.options)}
    selected = st.radio("Choose the matching output", option_ids, format_func=labels.get, index=None, horizontal=True)
    columns = st.columns(4)
    for column, option in zip(columns, question.options):
        with column:
            st.caption(labels[option.option_id])
            _svg(option.card, labels[option.option_id], 135)
    hint_col, submit_col = st.columns([1, 3])
    if hint_col.button("Hint"):
        st.session_state.logger.record(EventType.HINT_REQUESTED, puzzle_id=puzzle.puzzle_id, question_id=question.question_id, difficulty=puzzle.difficulty)
        st.info("Track positions first, then check whether one visual attribute changes consistently.")
    if submit_col.button("Submit answer", type="primary", disabled=selected is None, use_container_width=True):
        previous = st.session_state.last_selection.get(question.question_id)
        st.session_state.logger.option_selected(puzzle.puzzle_id, question.question_id, selected, previous)
        st.session_state.last_selection[question.question_id] = selected
        is_correct = question.is_correct(selected)
        st.session_state.logger.submitted(puzzle.puzzle_id, question.question_id, selected, is_correct, puzzle.difficulty)
        st.session_state.responses[puzzle.puzzle_id] = selected
        if index + 1 < len(assessment.puzzles):
            st.session_state.current += 1
        else:
            events = st.session_state.logger.events
            st.session_state.score = AssessmentScorer().score(assessment, st.session_state.responses, events)
            st.session_state.analytics = AnalyticsEngine().analyze(assessment, st.session_state.responses, events)
            st.session_state.completed_at = datetime.now(UTC)
            st.session_state.logger.record(EventType.ASSESSMENT_COMPLETED)
        st.rerun()


def results_page() -> None:
    score = st.session_state.score
    if score is None:
        st.warning("Complete the assessment to unlock results.")
        return
    st.title("Your reasoning profile")
    a, b, c = st.columns(3)
    a.metric("Normalized score", f"{score.normalized_score:.1f}")
    b.metric("Estimated percentile", f"{score.percentile:.0f}")
    c.metric("Report confidence", f"{score.confidence_score:.0f}%")
    st.subheader("Cognitive subscores")
    for subscore in score.subscores:
        st.markdown(subscore.ability.value.replace("_", " ").title())
        st.progress(subscore.normalized_score / 100, text=f"{subscore.normalized_score:.1f} / 100")
    # st.caption("Percentiles are preliminary MVP estimates and require validation against a representative normative sample.")


def analytics_page() -> None:
    report = st.session_state.analytics
    if report is None:
        st.warning("Complete the assessment to unlock analytics.")
        return
    st.title("Reasoning analytics")
    cols = st.columns(4)
    cols[0].metric("Accuracy", f"{report.accuracy:.0%}")
    cols[1].metric("Discovery time", f"{report.rule_discovery_time_seconds:.1f}s")
    cols[2].metric("Efficiency", f"{report.reasoning_efficiency:.0%}")
    cols[3].metric("Persistence", f"{report.persistence:.0%}")
    if report.learning_curve:
        st.subheader("Learning curve")
        st.line_chart({"Accuracy": list(report.learning_curve)})
    st.subheader("Recommendations")
    for recommendation in report.recommendations:
        st.write(f"- {recommendation}")
    if report.error_patterns:
        st.subheader("Observed error patterns")
        st.bar_chart(report.error_patterns)


def export_page() -> None:
    assessment, score = st.session_state.assessment, st.session_state.score
    if assessment is None or score is None:
        st.warning("Complete the assessment before exporting data.")
        return
    completed = replace(
        assessment, status=AssessmentStatus.COMPLETED, score=score,
        analytics=st.session_state.analytics, completed_at=st.session_state.completed_at,
    )
    session = AssessmentSession(
        completed, st.session_state.participant_id, st.session_state.logger.events,
        st.session_state.started_at, st.session_state.completed_at,
    )
    st.title("Export your data")
    st.write("Download portable session, event, and score data for research or integration workflows.")
    sdk = AssessmentSDK()
    st.download_button("Download session JSON", sdk.session_json(session), "gf_session.json", "application/json", use_container_width=True)
    st.download_button("Download events CSV", sdk.events_csv(session.events), "gf_events.csv", "text/csv", use_container_width=True)
    st.download_button("Download scores CSV", sdk.score_csv(score), "gf_scores.csv", "text/csv", use_container_width=True)


_state()
page = st.sidebar.radio(
    "Navigate",
    ("Home", "Assessment", "Results", "Analytics", "Export"),
    key="page",
)
# st.sidebar.caption("Mentiscope Gf MVP")
{"Home": home_page, "Assessment": assessment_page, "Results": results_page, "Analytics": analytics_page, "Export": export_page}[page]()
