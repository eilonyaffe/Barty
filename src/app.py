from scraper import prepare_articles
from sentence_transformer import generate_opinion
import time


def main():
    articles = prepare_articles()
    print(f"\nGenerating opinions for {len(articles)} articles...\n")

    for i, article in enumerate(articles, 1):
        print(f"--- Article {i} ---")
        print(f"Title: {article.title}")
        print(f"Date: {article.date}")
        print(f"Entities: {article.entities}")
        print()

        opinion = generate_opinion(article)
        time.sleep(4)  # because GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15, so 4*15=60
        print(f"Opinion:\n{opinion}")
        print("-" * 40 + "\n")

if __name__ == "__main__":
    main()
