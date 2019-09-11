import requests
import json

app_id = 'sjkT6Tyvisvw0lRKCpBdVw'
access_token = '1bKNig6B_pFhjiJTglDk0-2Bh45QSDgvTdvgdonfnBZXUEl5CpKZcTKz-j_0OLI6n2eQnOh_U2eATjDcu2cLBEzR-4M0V60O3etWbwRf6ctXUihQ7Oek1-CJLmR5XXYx'

url = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'bearer %s' % access_token}
params = {'location': 'San Bruno',
          'term': 'Japanese Restaurant',
          'pricing_filter': '1, 2',
          'sort_by': 'rating'
          }

resp = requests.get(url=url, params=params, headers=headers)

with open('yelp.json', 'a', encoding='utf-8') as f:
    json.dump(resp.json(), f, ensure_ascii=False)
