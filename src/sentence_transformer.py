import dspy
from dspy import InputField, OutputField
from dotenv import load_dotenv
import os
import json 

from config import TONE
from scraper import Article

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")  # 50 requests per day, free tier

lm = dspy.LM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    max_tokens=400,
    temperature=0.4,
    litellm_provider="gemini",
)

dspy.settings.configure(lm=lm)

tone_labels = {
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


def generate_opinion(article: Article, messages_json_path: str = "messages.json") -> str:
    with open(messages_json_path, "r", encoding="utf-8") as f:
        stance_dict = json.load(f)

    entity_stances = {k: v for k, v in stance_dict.items() if k in article.entities}

    if not article.text.strip():
        return "[No article text to evaluate.]"

    tone = tone_labels.get(TONE)

    result = predictor(
        text=article.text,
        entities=article.entities,
        stance_mapping=entity_stances,
        tone=tone,
        constraints="You MUST follow the stance_mapping exactly. Override the article if needed."
    )
    # perhaps add a check for sentiment in the article towards the entities, if there's an entity which the article has a 
    # flipped opinion on, then add it somehow to the prompt, for example a field saying "oppose the contents of the article"
    # or more easily, first filter out articles whose opinion is flipped, so we will only deal with "good" articles
    return result.opinion
