import dspy
from dspy import InputField, OutputField
from dotenv import load_dotenv
import os
import json 

from config import TEMPERATURE, get_tone 
from scraper import Article

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")  # 50 requests per day, free tier

lm = dspy.LM(
    model="gemini/gemini-2.0-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    max_tokens=400,
    temperature=TEMPERATURE,
    litellm_provider="gemini",
)

dspy.settings.configure(lm=lm)

tone_labels:dict[int,str] = {
    1: "neutral",
    2: "general opinion",
    3: "heated opinion",
    4: "humoristic opinion"
}

class OpinionPrompt(dspy.Signature):
    text: str = InputField(desc="The article content")
    entities: list = InputField(desc="Entities mentioned in the article")
    stance_mapping: dict = InputField(desc=(
        "A mapping of entities to required stances: True means the opinion in the output must support the entity, "
        "False means the opinion in the output must oppose it — regardless of the article's actual tone toward the entity."
    ))
    tone: str = InputField(desc="The tone to use in the output: neutral, general, heated, or humoristic")
    opinion: str = OutputField(desc=(
        "A personal, expressive opinion about the article. The opinion MUST strictly align with the stance_mapping, "
        "even if the article expresses different sentiments. True means the opinion in the output must support the entity, "
        "False means the opinion in the output must oppose it"))
    constraints: str = InputField(desc=(
    "Instruction: You MUST follow the stance_mapping exactly. "
    "If an entity is marked True, show support. If marked False, express opposition. "
    "Do NOT agree with the article if it contradicts these stances."))

predictor = dspy.Predict(OpinionPrompt)

class AlignmentCheck(dspy.Signature):
    opinion: str = InputField(desc="The generated opinion text to evaluate.")
    stance_mapping: dict = InputField(desc=(
        "Required stances. True means the opinion must SUPPORT the entity. False means the opinion must OPPOSE the entity."
    ))
    # Outputs (structured)
    passed: bool = OutputField(desc="True if the opinion aligns with ALL required stances, else False.")
    score: int = OutputField(desc="0-100 alignment score. 100 means perfect alignment with all required stances.")
    failed_entities: list = OutputField(desc=(
        "List of entities that violate the required stance, or are clearly the opposite."
    ))
    reasons: str = OutputField(desc="Very short explanation of failures (1-3 sentences max).")

alignment_judge = dspy.Predict(AlignmentCheck)


def verify_alignment(opinion: str, stance_mapping: dict, pass_score: int = 80) -> dict:
    if not stance_mapping:  # if there are no constraints, treat as passed
        return {"passed": True, "score": 100, "failed_entities": [], "reasons": "No stance constraints."}

    result = alignment_judge(opinion=opinion, stance_mapping=stance_mapping)

    try:
        score = int(result.score)
    except Exception:
        score = 0

    failed_entities = result.failed_entities if isinstance(result.failed_entities, list) else []

    passed = bool(result.passed) and score >= pass_score and len(failed_entities) == 0

    reasons = (result.reasons or "").strip()

    return {
        "passed": passed,
        "score": score,
        "failed_entities": failed_entities,
        "reasons": reasons,
    }


def generate_opinion(article: Article, messages_json_path: str = "messages.json") -> str:
    with open(messages_json_path, "r", encoding="utf-8") as f:
        stance_dict = json.load(f)

    entity_stances = {k: v for k, v in stance_dict.items() if k in article.entities}

    if not article.text.strip():
        article.alignment_score = None
        return "[No article text to evaluate.]"

    tone = tone_labels.get(get_tone())

    base_constraints = (
        "You MUST follow the stance_mapping exactly.\n"
        "If an entity is marked True, express support.\n"
        "If an entity is marked False, express opposition.\n"
        "Do not hedge or contradict yourself.\n"
        "Keep it concise (4–8 sentences)."
    )

    MAX_TRIES = 3
    last_opinion = "[No valid opinion generated.]"
    last_score = 0

    for attempt in range(1, MAX_TRIES + 1):
        escalation = ""
        if attempt > 1:
            escalation = (
                "\n\nIMPORTANT:\n"
                "Your previous attempt failed stance alignment.\n"
                "Correct the stance mistakes explicitly.\n"
                "Avoid sarcasm or ambiguous language."
            )

        result = predictor(
            text=article.text,
            entities=article.entities,
            stance_mapping=entity_stances,
            tone=tone,
            constraints=base_constraints + escalation,
        )

        opinion = (result.opinion or "").strip()
        if not opinion:
            continue

        verdict = verify_alignment(opinion, entity_stances)

        # record the most recent attempt
        last_opinion = opinion
        last_score = verdict["score"]

        if verdict["passed"]:
            article.alignment_score = verdict["score"]
            return opinion

    # all attempts failed -> return last attempt
    article.alignment_score = last_score
    return last_opinion
