from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

class AbstractBaseClient:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

class GithubClient(AbstractBaseClient):
    def get_today_trending_repositories(self):
        r = requests.get('https://github.com/trending?since=daily', headers=self.headers)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        repos = soup.select('article.Box-row')
        data = []

        for repo in repos:
            repo_data = {}
            repo_data['name'] = repo.h2.a.get('href').strip()

            description_tag = repo.find('p')  # Description
            repo_data['description'] = description_tag.text.strip() if description_tag else ''

            lang_tag = repo.find(attrs={'itemprop': 'programmingLanguage'})  # Language
            repo_data['language'] = lang_tag.text.strip() if lang_tag else ''

            # Find the <a> tag with the star data
            star_link = repo.find('a', href=lambda href: href and 'stargazers' in href)
            if star_link:
                star_data = star_link.get_text(strip=True).replace(',', '')
                repo_data['stars'] = int(star_data) if star_data.isdigit() else 0
            else:
                repo_data['stars'] = 0

            # Find the <a> tag with the fork data
            fork_link = repo.find('a', href=lambda href: href and 'forks' in href)
            if fork_link:
                fork_data = fork_link.get_text(strip=True).replace(',', '')
                repo_data['forks'] = int(fork_data) if fork_data.isdigit() else 0
            else:
                repo_data['forks'] = 0

            # Check for open issues and add them if present
            issues_text = repo.find(text=re.compile(r'\d+ open issues'))  # Open issues count
            if issues_text:
                issues_numbers_only = re.findall(r'\d+', issues_text)
                repo_data['open_issues'] = int(issues_numbers_only[0]) if issues_numbers_only else 0
            else:
                # If open issues are not present, do not add them to the data
                pass

            data.append(repo_data)

        return data

@app.get("/trending")
def read_trending_repositories():
    client = GithubClient()
    return client.get_today_trending_repositories()

# To run the app, use the command: uvicorn filename:app --reload
