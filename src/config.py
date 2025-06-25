WAIT_SECS = 1  # how many seconds we wait between retries
RETRIES = 30  # sometimes fetch requests for the various links fails. this controls how many retries
TOKENS = 300  # how many tokens we take from each article, to be later fed as input to the LLM
TONE = 3  # 1: neutral as possible- saying the facts in support of the issue, 2: general opinion, 3: heated opinion, 4: humoristic opinion
MAX_ARTICLES = 15  # maximum amount of filtered articles we feed into the LLM (say each day in production)