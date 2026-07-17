import requests
import os

def download_beautiful_fallback():
    pexels_key = "TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60"
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": pexels_key}
    params = {"query": "mountain valley sunrise", "orientation": "landscape", "per_page": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            if photos:
                img_url = photos[0]["src"]["large2x"]
                print(f"Downloading beautiful nature image: {img_url}")
                img_data = requests.get(img_url, timeout=15).content
                os.makedirs("assets", exist_ok=True)
                target_path = "assets/loan_background_image.jpeg"
                with open(target_path, "wb") as f:
                    f.write(img_data)
                print("Successfully updated assets/loan_background_image.jpeg!")
            else:
                print("No photos found.")
        else:
            print("Failed to query Pexels:", response.status_code, response.text)
    except Exception as e:
        print("Error downloading fallback:", e)

if __name__ == "__main__":
    download_beautiful_fallback()
