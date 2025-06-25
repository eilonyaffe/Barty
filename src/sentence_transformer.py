import dspy
from dspy import InputField, OutputField
from dotenv import load_dotenv
import os
import json 

from config import TONE
from scraper import Article

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

lm = dspy.LM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    max_tokens=400,
    temperature=0.7,
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
    stance_mapping: dict = InputField(desc="Mapping of entities to stances (True = support, False = oppose)")
    tone: str = InputField(desc="The tone to use: neutral, general, heated, or humoristic")
    opinion: str = OutputField(desc="A personal, expressive opinion reflecting all the stances")

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
        tone=tone
    )

    return result.opinion