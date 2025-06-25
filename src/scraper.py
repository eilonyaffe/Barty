import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import tiktoken

from config import TOKENS, RETRIES, WAIT_SECS, MAX_ARTICLES

encoding = tiktoken.get_encoding("cl100k_base")

def truncate_to_token_limit(text, max_tokens=TOKENS):
    tokens = encoding.encode(text)
    truncated = encoding.decode(tokens[:max_tokens])
    return truncated


class Article:
    def __init__(self, title, date, link, summary, text=None):
        self.title = title
        self.date = date
        self.link = link
        self.summary = summary
        self.text = text or ""
        self.entities = []

    def __repr__(self):
        return f"{self.title} \n{self.date} \n{self.link}\n{self.entities}\n{self.text}\n"
    

def get_articles():
    try:
        url = "https://www.breitbart.com/politics/"
        res = requests.get(url)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "lxml")

        articles = []

        for article_tag in soup.find_all("article"):
            try:
                title_tag = article_tag.find("h2").find("a")
                title = title_tag.get_text(strip=True)
                link = title_tag["href"]  # <h2><a href=

                time_tag = article_tag.find("time")
                date_str = time_tag["datetime"] if time_tag else None  # <time datetime=
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else None

                summary_tag = article_tag.find("div", class_="excerpt")  # <div class="excerpt">
                summary = summary_tag.get_text(strip=True) if summary_tag else ""

                articles.append(Article(title, date, link, summary, text=None))

            except Exception as inner_e:
                # Skip malformed article entries silently
                continue
        return articles

    except Exception as e:
        print("Error in get_articles:", e)
        return [], False


def filter_articles(articles, json_path="messages.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        keywords = [k.lower() for k in data.keys()]  # the messages strings

        def matches_keywords(article):
            content = f"{article.title} {article.summary}".lower()  # check if a message is in the article
            return any(keyword in content for keyword in keywords)

        matched = [article for article in articles if matches_keywords(article)]

        #  sort by date, newest to oldest
        matched = sorted(
            [a for a in matched if a.date is not None],
            key=lambda x: x.date,
            reverse=True
        )

        # Truncate to top MAX_ARTICLES most recent
        return matched[:MAX_ARTICLES]

    except Exception as e:
        print("Error in filter_articles:", e)
        return []


def get_article_text(article_link):
    content_div = None  # declare outside loop

    for _ in range (RETRIES):  # retries because sometimes gets "503 Backend fetch failed" error upon retrieving the html 
        try:
            time.sleep(WAIT_SECS)
            res = requests.get(article_link)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, "lxml")
            content_div = soup.find("div", class_="entry-content")
            if content_div:
                break
        
        except Exception as e:
            print(f"Error in get_article_text: {e}")
            continue

    if not content_div:
        print("No entry-content div found.")
        return ""

    paragraphs = content_div.find_all("p")
    full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return truncate_to_token_limit(full_text)


def extract_entities(article, keyword_list):
    content = f"{article.title} {article.summary} {article.text}".lower()
    return [k for k in keyword_list if k.lower() in content]


def prepare_articles():  
    all_articles = get_articles()
    print(f"number of articles found before filter: {len(all_articles)}")

    filtered_articles = filter_articles(all_articles)
    print(f"number of articles found after filter: {len(filtered_articles)}")

    with open("messages.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    keyword_list = list(data.keys())

    clean_articles = []
    for art in filtered_articles:
        art.text = get_article_text(art.link)  # updated: removed second arg
        if not art.text.strip():
            continue  # skip articles with no content_div
        art.entities = extract_entities(art, keyword_list)
        clean_articles.append(art)
        print(f"number of extracted articles: {len(clean_articles)}")

    clean_articles.sort(key=lambda e: len(e.entities))  # sorting to first have articles with least entities. more trustworthy output
    return clean_articles
