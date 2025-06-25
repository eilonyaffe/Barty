# Barty: an article opinion generator, which conforms to a predefined set of biases and interest points

This project scrapes political articles from [Breitbart](https://www.breitbart.com/politics/), filters them based on relevant entities, and uses the Gemini 1.5 Flash language model (via DSPy) to generate expressive opinions about the articles. The tone and stance toward each entity are customizable.

---

## Features

- **Web Scraping**: Automatically fetches and parses recent political articles.
- **Entity Filtering**: Selects articles containing specific keywords/entities listed in `messages.json`.
- **Text Truncation**: Limits article content to a token threshold for optimal LLM input.
- **Opinion Generation**: Produces LLM-driven commentary in one of four configurable tones (neutral, general, heated, humoristic) using Gemini Flash via DSPy.
- **Stance Control**: Aligns opinions with a pre-defined stance toward each entity (`True = support`, `False = oppose`).

---
