import re
import os
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

#scrape huggingface
url = "https://huggingface.co/papers/trending"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

matches = []
for a in soup.select('a'):
    a = str(a)
    search = re.search(r"\/papers\/\d+\.\d+", a)
    if search:
        matches.append(search.group())

matches = np.array(matches)
matches = np.unique(matches)
matches = np.random.choice(matches, 10, replace=False)  # pick 10 random papers

urls = ["https://huggingface.co" + m for m in matches]

# get paper titles
paper_entries = []
for u in urls:
    try:
        r = requests.get(u, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        page = BeautifulSoup(r.text, "html.parser")
        title_el = page.find("h1")
        title = title_el.get_text(strip=True) if title_el else "Unknown Title"

        paper_entries.append((title, u))
    except Exception as e:
        paper_entries.append(("Error fetching title", u))


# get date
today = date.today()
monday = today - timedelta(days=today.weekday())  # start of week
sunday = monday + timedelta(days=6)               # end of week
week_range = f"{monday.strftime('%B %d, %Y')} – {sunday.strftime('%B %d, %Y')}"

# Prepare Jekyll frontmatter
jekyll_date = today.strftime("%Y-%m-%d")
month = today.strftime("%m")
week = today.strftime("%W")
jekyll_frontmatter = f"---\ntitle: \"Trending ML/AI Papers\"\ndate: {jekyll_date}\npermalink: /posts/2025/{month}/blog-post-{week}/\ntags: [ml, ai, papers, trending]\n---\n\n"

# Build markdown
markdown_output = jekyll_frontmatter
markdown_output += f"Trending ML/AI Papers from the week of {week_range}\n\n"
for i, (title, link) in enumerate(paper_entries, 1):
    title = re.sub('\n', ' ', title)
    markdown_output += f"{i}. [{title}]({link})\n\n"
   

# _posts folder
posts_dir = "_posts"
os.makedirs(posts_dir, exist_ok=True)

filename = os.path.join(posts_dir, f"{today.strftime('%Y-%m-%d')}-trending-ml-papers.md")
with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_output)
