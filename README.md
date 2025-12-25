# Barty: an article opinion generation bot

> **DISCLAIMER**  
> This project is for **learning and research purposes only**.  
> It is **not used** in any real influence campaign, nor does it generate or publish content to any external platform.  
> All outputs remain local and are produced solely for the purpose of studying the potential implications of language model usage in political contexts.

---

Barty is a theoretical prototype that explores how large language models (LLMs) might be used to generate expressive opinions on political content. It scrapes recent political articles from [Breitbart](https://www.breitbart.com/politics/), filters them based on specified entities, and uses the Gemini 1.5 Flash model via DSPy to generate commentary.

---

## Features

- **Web Scraping**: Gathers recent political articles from Breitbart.
- **Entity Filtering**: Keeps only articles mentioning keywords from `messages.json`.
- **Text Truncation**: Keeps article content within token limits for LLMs.
- **Opinion Generation**: Produces commentary in configurable tones (neutral, general, heated, or humoristic).
- **Stance Control**: Aligns opinions with a defined stance for each entity (`True = support`, `False = oppose`).

---

## Tech Stack
- **Python**
- **DSPy** for prompt abstraction
- **Gemini 1.5 Flash** for opinion generation
- **BeautifulSoup + Requests** for web scraping
- **tiktoken** for token-aware truncation

---


## Ethics and Usage

This repository **must not** be used to build or participate in any disinformation campaign.  
It is a sandbox for testing, evaluating, and reflecting on the ethical implications of AI-generated political content.

If you are considering using this code beyond personal research or learning, please consider the consequences and consult with appropriate legal and ethical guidelines.

---

## License

This project is licensed under the [MIT License](LICENSE).  
Use in actual influence or disinformation campaigns is **strictly prohibited**.

---
