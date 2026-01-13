import time
import json

from scraper import prepare_articles
from sentence_transformer import generate_opinion
from logger import get_logger
from data_prep import create_run_output_file


logger = get_logger(__name__)

def article_to_dict(article, opinion):
    return {
        "title": article.title,
        "date": article.date.isoformat() if article.date else None,
        "link": article.link,
        "entities": article.entities,
        "opinion": opinion,
    }

def main():
    output_path = create_run_output_file(keep_last=10)

    articles = prepare_articles()
    logger.info("Generating opinions for %d articles", len(articles))

    with open(output_path, "w", encoding="utf-8") as f:
        for i, article in enumerate(articles, 1):
            logger.info("Processing article %d/%d: %s", i, len(articles), article.title)

            opinion = generate_opinion(article)
            time.sleep(4)  # because GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15, so 4*15=60

            record = article_to_dict(article, opinion)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()  # ensure it is still written even if there's a crash

    logger.info("Done. Wrote %d lines to %s", len(articles), output_path)

if __name__ == "__main__":
    main()
