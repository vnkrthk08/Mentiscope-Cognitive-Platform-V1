import argparse
import json
import sys
import uuid
import random
from datetime import datetime, UTC

from puzzle_engine import AssessmentBuilder
from renderer import SVGRenderer
from scorer import AssessmentScorer
from analytics import AnalyticsEngine
from models import InteractionEvent, EventType
import models

def deterministic_uuid4():
    return uuid.UUID(int=random.getrandbits(128))

models.uuid4 = deterministic_uuid4

def generate_questions():
    try:
        seed = random.randint(0, 999999999)
        random.seed(seed)
        builder = AssessmentBuilder(seed=seed)
        builder.with_progression(5)
        assessment = builder.build()
        
        renderer = SVGRenderer()
        
        questions = []
        for puzzle in assessment.puzzles:
            examples = []
            for ex in puzzle.examples:
                examples.append({
                    "inputSvg": renderer.render_card(ex.input_card, aria_label="Example Input"),
                    "outputSvg": renderer.render_card(ex.output_card, aria_label="Example Output")
                })
                
            options = []
            for opt in puzzle.question.options:
                options.append({
                    "id": opt.option_id,
                    "svgContent": renderer.render_card(opt.card, aria_label="Option Card")
                })
                
            q = {
                "id": puzzle.puzzle_id,
                "text": "Infer the hidden transformation and select the correct output.",
                "story": f"Difficulty: {puzzle.difficulty.value.title()} | Study the examples to learn the rule.",
                "type": "svg-matrix",
                "svgContent": renderer.render_card(puzzle.question.input_card, aria_label="Question Input"),
                "correctAnswer": puzzle.question.correct_option_id,
                "examples": examples,
                "svgOptions": options,
                "hint": "Track positions first, then check whether one visual attribute changes consistently."
            }
            questions.append(q)
            
        print(json.dumps({"status": "success", "seed": seed, "questions": questions}))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}))

def evaluate_assessment(seed, answers_payload):
    try:
        random.seed(seed)
        builder = AssessmentBuilder(seed=seed)
        builder.with_progression(5)
        assessment = builder.build()
        
        responses = {}
        events = []
        for ans in answers_payload:
            responses[ans["questionId"]] = ans["answer"]
            events.append(InteractionEvent(
                event_type=EventType.ANSWER_SUBMITTED,
                assessment_id=assessment.assessment_id,
                participant_id="student",
                puzzle_id=ans["questionId"],
                question_id=ans["questionId"],
                option_id=ans["answer"],
                reaction_time_ms=ans.get("durationMs", 15000),
                timestamp=datetime.now(UTC)
            ))
            
        scorer = AssessmentScorer()
        score_report = scorer.score(assessment, responses, events)
        
        analytics = AnalyticsEngine()
        analytics_report = analytics.analyze(assessment, responses, events)
        
        print(json.dumps({
            "status": "success", 
            "score": score_report.to_dict(),
            "analytics": analytics_report.to_dict()
        }))
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"status": "error", "error": str(e)}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate", type=int, help="Seed to reconstruct the assessment and evaluate")
    args = parser.parse_args()
    
    if args.evaluate is not None:
        payload = sys.stdin.read().strip()
        if not payload:
            print(json.dumps({"status": "error", "error": "No answers provided on stdin"}))
            sys.exit(1)
        try:
            answers = json.loads(payload)
            evaluate_assessment(args.evaluate, answers)
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "error": "Invalid JSON on stdin"}))
    else:
        generate_questions()
