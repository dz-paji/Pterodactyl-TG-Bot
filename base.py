import requests
import json

def parse_response(response, api_key, url):
    if 'errors' in response:
        print('ERROR. Key: ' + api_key + ', URL: ' + url)
        return response
    elif response['object'] == 'list':
        data = [item.get('attributes') for item in response.get('data')]
        return data
        # for item in response.get('data'):
    elif response['object'] == 'stats':
        data = response['attributes']
        return data

    else:
        data = response.get('attributes')
        return data


def react_request(url, api_key):

    contents_raw = requests.get(
        url,
        headers = {
            'Accept': 'Application/vnd.pterodactyl.v1+json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+ api_key
        }
    ).json()
    data = parse_response(contents_raw, url = url, api_key = api_key)
    return data

def post_request(url, api_key):
    contents_raw = requests.post(
        url,
        headers = {
            'Accept': 'Application/vnd.pterodactyl.v1+json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+ api_key
        }
    )
    print(contents_raw)
    try:
        return contents_raw.json()
    except json.decoder.JSONDecodeError:
        return 'success'

def get_curse():
    return requests.get('https://nmsl.shadiao.app/api.php?level=min')