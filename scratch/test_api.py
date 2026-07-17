import requests
import os

def test_unsplash():
    key = "zRFlykNbtqwtGbs5CPWvvGRLxNK9xOmQwBsQ4X1Io1Q"
    url = "https://api.unsplash.com/search/photos"
    params = {"query": "winter forest", "orientation": "landscape", "per_page": 1, "client_id": key}
    try:
        r = requests.get(url, params=params, timeout=5)
        print("Unsplash Response Code:", r.status_code)
        if r.status_code == 200:
            print("Unsplash Image URL:", r.json()['results'][0]['urls']['raw'])
        else:
            print("Unsplash Content:", r.text)
    except Exception as e:
        print("Unsplash Error:", e)

def test_pexels():
    key = "TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60"
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": key}
    params = {"query": "winter forest", "orientation": "landscape", "per_page": 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        print("Pexels Response Code:", r.status_code)
        if r.status_code == 200:
            print("Pexels Image URL:", r.json()['photos'][0]['src']['original'])
        else:
            print("Pexels Content:", r.text)
    except Exception as e:
        print("Pexels Error:", e)

if __name__ == "__main__":
    test_unsplash()
    test_pexels()
