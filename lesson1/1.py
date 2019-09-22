import requests
import json


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0'
github_api_url = 'https://api.github.com/users/'
user_name = 'KurbakovIS'
repo = []

response = requests.get(f'{github_api_url}{user_name}/repos', headers={'User-Agent': USER_AGENT})

data = response.json()


for key in data:
    repo.append(key['full_name'])

dataRepo = {'nameRepo': repo}

with open('repo.json', 'a', encoding='utf-8') as f:
    json.dump(dataRepo, f, ensure_ascii=False)

