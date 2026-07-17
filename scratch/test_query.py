import requests

def test_query(q):
    key = "TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60"
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": key}
    params = {"query": q, "orientation": "landscape", "per_page": 5}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            print(f"Query: '{q}' -> Results count: {len(photos)}")
            if photos:
                print("First image:", photos[0]['src']['original'])
        else:
            print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_query("night stars cloudy mountains -people -person -interior -buildings -architecture")
    test_query("night stars cloudy mountains")
