import time
import json
from typing import Any, Dict

from scraper import prepare_articles, Article
from sentence_transformer import generate_opinion
from logger import get_logger
from data_prep import create_timestamped_output_file

logger = get_logger(__name__)


def article_to_dict(article:Article, opinion:str)-> Dict[str, Any]:
    return {
        "title": article.title,
        "date": article.date.isoformat() if article.date else None,
        "link": article.link,
        "entities": article.entities,
        "opinion": opinion,
        "alignment_score": article.alignment_score,  # NEW
    }


def main()->None:
    output_path = create_timestamped_output_file(keep_last=10)

    articles:list = prepare_articles()
    logger.info("Generating opinions for %d articles", len(articles))

    with open(output_path, "w", encoding="utf-8") as f:
        for i, article in enumerate(articles, 1):
            logger.info("Processing article %d/%d: %s", i, len(articles), article.title)

            opinion:str = generate_opinion(article)
            time.sleep(4)  # because GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15, so 4*15=60

            record:Dict[str, Any] = article_to_dict(article, opinion)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()  # ensure it is still written even if there's a crash

    logger.info("Done. Wrote %d lines to %s", len(articles), output_path)

if __name__ == "__main__":
    main()
