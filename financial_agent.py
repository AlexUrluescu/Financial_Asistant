from langchain_google_genai import ChatGoogleGenerativeAI
from google.oauth2 import service_account
import json
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
import os

load_dotenv()

json_string = """
{
  "type": "service_account",
  "project_id": "gen-lang-client-0588309521",
  "private_key_id": "bb9c74146c3b6452f72abf8d4d83f83adbe52a8e",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDDCX0Pf+TOol+I\\nOsgLtqbMvUWnDXXgljtfVSrVQX59LSXAUteMolJZa9Ve2UhT5CXz+SnwoMaC4VxH\\nIyyjzoZAb6pFwDUUEiVvpNdU0s1KvPozJTMk6hQXo5WYMYIW0Hoaq0zdwd+Qw2uJ\\nlQD127gfgQEKzvO73MLU9t9SV5sc0OTZ2jeZv6cyh/q/oinYIeXc2pxX+gK5uaWC\\nSMTn0MP3P88wr4egDbixn6WjLM4dyHCDODyqYUKocC4ulMCTDjsPzoPcml1mo1ak\\nXhdDTbRs9q8kYhK3+nXhIUKC00RLQehKZ26AIQqeQzPo8iF0bvxoR6fszQxTdPZW\\nUENzntkFAgMBAAECggEAXXRve3zR+31sf0+DSbGUzWgoNvrJL/tsqaqaoqMGZB69\\nByHq7RVelkCIdjFxadlZokUTJp0zYcVwvRmKq1crlzaqhU+rX1munIeFMrzr59MT\\npGw/zIFpbUZSSSH37syopZzNcTkT0j8BiWRfmG9XE6lyAWbW/X6z0O4WZlNaHPzY\\nbxLgovU0CP0osz3Bycu+vr00ChwfX2PwHKWBBlvhA4A7d+Iq8kGe/9H/snHRG+sX\\nKr1ZhOUPxXsD6Mynf1n7Fjvfns898q1EvjAWr6inGbj91YozUrfoq5xCCW65tqh6\\nQpMB6ALlDw3aSfYKONJq0cLX8vF8S4ampmvhCo845QKBgQD2gwxLamTXdNiQBjdY\\nThVtlNiU53hUa9DfrLoePLpKYp0Y4O36R5enBjY1Yf0yUnge5TUjbqtk+8mB8nqv\\n6uCzw50YcZCQXEOFThYLv9w3KEcSYNhhhmpILRhIQYAdKMt3jn75kvB3/6KBZN+R\\nHMktlkM7GeXOx9HlnAic7Gbo1wKBgQDKiz6Fhu8U6wJd7i6XNOEnRSFy8lfyR8jW\\nQ5jkizSs5Rg9tWhL2zt8bPuy846/P/GsIZlQogGX54kLgGdP09H6HCDv8OejNGWD\\nOmkq/Z/BH4tY6vYI1l0o20/6GlGrAf/eccM6+ziaGopI0UUlY1tmCDDOsxUHW8Kc\\ny9XNhjKFgwKBgQDOvCSpcrbTgqjEUJJFumZ6GiRw7Jabpjfr/f2wshlBnOZHIQwz\\no6rpZmo75svjUgpvTqZ76qpO7GKYWnTN59s+p0SuZT9p8hamS1Bt1h+nGl5QaWvO\\njl2/3iHJJzV8PuQ0hgqy36pP2NG+VoywNEX7t1L208dI3YeIWo1WnWPIzQKBgQC2\\nFBUhblrRIC8hh7PkhEn/xnq6XbfH+tZGH8B7e9TftJdlKgZXYv8H7OUcSy1BKle0\\nWQP9Y5YxG5iseULmlVIHGHBXouZpZfn3zXOrjRKnRxc62QZSjXpz9yvfdveB1qtR\\nKk3KYPrSNheoPFB/uuD4SVavCnhWBBxgXjGWsBQMxwKBgQDrGFnleJ3DRsbmkNMJ\\nVMGvjNbCWx6OUqlHEQdqTj0LO1bSDZmjTW5UkwpUzKjYvHbsKcGjOE9PwLokxw0s\\nHmMOOKOvR5lMTnj440GVSZ3vB6xrbrGDBLTswKjMQJHg8Se2XgudI9aIUZKnvBvN\\nXqOt1PNAi4LTn938iUrWkGl08A==\\n-----END PRIVATE KEY-----\\n",
  "client_email": "gemini-langchain-service@gen-lang-client-0588309521.iam.gserviceaccount.com",
  "client_id": "103946725384589893375",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gemini-langchain-service%40gen-lang-client-0588309521.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

# credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

credentials_info = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(credentials_info)


def initialize_summarization_agent():
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", credentials=credentials)
    summarization_agent = initialize_agent(
        tools=[scrape_tool],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )
    return summarization_agent


def format_pub_date(pub_date: str) -> str:
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S GMT")
    
    # Reformat the date into the desired format: "Sun, 13 Apr 2025"
    formatted_date = date_obj.strftime("%a, %d %b %Y")
    return formatted_date


def summarize_article(agent, title, link, pub_date, article_text):
    # Summarization prompt
    prompt = f"""
    You are analyzing a CNBC article. Your task is twofold:

    1. Write a concise summary in 6–7 sentences focusing on key <strong>financial</strong>, <strong>political</strong>, or <strong>economic</strong> implications.
    2. After the summary, include a separate section titled <strong>Key Takeaways</strong> with 2-3 short bullet points, each using <strong> tags to highlight the most important concepts or statistics.

    IMPORTANT INSTRUCTIONS:
    - The output MUST be clean, valid HTML.
    - NEVER include markdown, code blocks, or triple backticks (e.g. ```html).
    - Do NOT wrap anything in quotation marks or escape characters.
    - Return only the final HTML content that can be rendered directly in a browser.

    <strong>Title:</strong> {title}<br>
    <strong>Link:</strong> <a href="{link}" target="_blank">{link}</a><br>
    <strong>Published:</strong> {format_pub_date(pub_date)}<br><br>

    Article:
    {article_text}
    """
    # Running the agent to generate a summary
    summary = agent.run(prompt)
    summary = summary.replace("```html", "").replace("```", "").strip()
    return summary.strip()

def format_article_to_html(title, pub_date, summary, link):
    # Convert the summary into a structured HTML format
    html_output = f"""
    <div style='margin-bottom: 30px;'>
        <div style="margin-bottom: 5px;">
            <h2 style="margin: 0; font-size: 18px;">{title}</h2>
            <p style="margin: 5px 0 0 0;"><strong>Published:</strong> {format_pub_date(pub_date)}</p>
        </div>

        {summary}

        <p><a href="{link}" target="_blank">Read full article</a></p>
    </div>
    <hr>
    """
    return html_output

import requests
from bs4 import BeautifulSoup

def scrape_cnbc_article(url: str) -> str:
    # Check if the URL is valid
    if not url or not url.startswith("http"):
        raise ValueError("Invalid URL: URL must be a non-empty string and start with 'http'.")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error while making request: {e}")
        return ""  # Return empty string in case of error (could also raise an exception)
    
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.select("div.ArticleBody-articleBody p")
    
    # Fallback if no paragraphs found
    if not paragraphs:
        paragraphs = soup.select("div.group p")
    
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    
    return text[:4000]  # Optional length cap


# --- Create LangChain Tool ---
scrape_tool = Tool(
    name="CNBCArticleScraper",
    func=scrape_cnbc_article,
    description="Scrapes CNBC article text from a given URL."
)

def financial_agent():

    url = 'https://www.cnbc.com/id/100003114/device/rss/rss.html'
    feed = feedparser.parse(url)

    # Step 2: Init LangChain Agent with Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", credentials=credentials)
    agent = initialize_agent(
        tools=[scrape_tool],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )

    html_output = "<html><body>"
    summarization_agent = initialize_summarization_agent()

    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        pub_date = entry.published

           # Scrape the article content
        article_text = scrape_cnbc_article(link)

        # 1. Summarize the article using the summarization agent
        summary = summarize_article(summarization_agent, title, link, pub_date, article_text)

        # 2. Format the summary into HTML using the formatting agent
        article_html = format_article_to_html(title, pub_date, summary, link)

        # Append the formatted HTML to the final output
        html_output += article_html


    html_output += "</body></html>"

    print(html_output)
    return html_output

# financial_agent()

