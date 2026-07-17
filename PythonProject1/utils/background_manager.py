import os
import time
import random
import requests
import base64
from datetime import datetime
import streamlit as st

class BackgroundManager:
    """
    Manages the dynamic, intelligent nature backgrounds using the Unsplash and Pexels APIs
    integrated with Weather, Time of Day, and Season detection.
    """
    def __init__(self):
        # Fallback environment setup for out-of-the-box execution using user-provided API keys
        if "UNSPLASH_ACCESS_KEY" not in os.environ or not os.environ["UNSPLASH_ACCESS_KEY"].strip():
            os.environ["UNSPLASH_ACCESS_KEY"] = "zRFlykNbtqwtGbs5CPWvvGRLxNK9xOmQwBsQ4X1Io1Q"
        if "PEXELS_API_KEY" not in os.environ or not os.environ["PEXELS_API_KEY"].strip():
            os.environ["PEXELS_API_KEY"] = "TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60"

        self.unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
        self.pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
        self.fallback_path = "assets/loan_background_image.jpeg"
        
    def get_time_of_day_bucket(self, time_str):
        """
        Categorizes current time into specific time-of-day buckets.
        """
        try:
            hour = int(time_str.split(":")[0])
        except Exception:
            hour = datetime.now().hour
            
        if 5 <= hour < 6:
            return "Dawn"
        elif 6 <= hour < 7:
            return "Sunrise"
        elif 7 <= hour < 11:
            return "Morning"
        elif 11 <= hour < 13:
            return "Noon"
        elif 13 <= hour < 16:
            return "Afternoon"
        elif 16 <= hour < 18:
            return "Golden Hour"
        elif 18 <= hour < 19:
            return "Sunset"
        elif 19 <= hour < 21:
            return "Evening"
        elif 21 <= hour < 23:
            return "Night"
        else:
            return "Midnight"
            
    def get_season_bucket(self, day_of_year):
        """
        Maps the day of the year to spring, summer, monsoon, autumn, or winter.
        """
        try:
            doy = int(day_of_year)
        except Exception:
            doy = datetime.now().timetuple().tm_yday
            
        if 60 <= doy < 120:
            return "Spring"
        elif 120 <= doy < 181:
            return "Summer"
        elif 181 <= doy < 273:
            return "Monsoon"
        elif 273 <= doy < 334:
            return "Autumn"
        else:
            return "Winter"

    def get_weather_keyword(self, weather_main):
        """
        Maps OpenWeather main status to landscape nature search keywords.
        """
        weather_keywords = {
            "Clear": ["sunrise mountains", "green valley", "crystal lake", "alpine meadow", "golden meadow", "sunny beach"],
            "Clouds": ["cloudy mountains", "cloudy forest", "cloudy valley", "misty pine forest"],
            "Rain": ["rainy forest", "rainy mountains", "rainforest", "waterfall jungle", "waterfall"],
            "Drizzle": ["rainy forest", "rainy mountains", "rainforest", "waterfall"],
            "Thunderstorm": ["lightning landscape", "storm clouds", "dramatic sky"],
            "Snow": ["snowy mountains", "winter forest", "frozen lake"],
            "Mist": ["misty forest", "fog valley", "mountain fog", "misty pine forest"],
            "Haze": ["hazy hills", "soft landscape"]
        }
        options = weather_keywords.get(weather_main, ["mountains", "green valley", "crystal lake", "forest"])
        return random.choice(options)

    def generate_intelligent_query(self, weather_main, time_of_day, season):
        """
        Builds a query combination that maximizes landscape nature relevance.
        We append negative tags to avoid people, structures, and buildings.
        """
        weather_kw = self.get_weather_keyword(weather_main)
        
        if time_of_day in ["Night", "Midnight"]:
            base_query = f"night stars {weather_kw}"
        elif time_of_day in ["Sunset", "Sunrise", "Dawn", "Golden Hour"]:
            base_query = f"{season.lower()} {time_of_day.lower()} {weather_kw}"
        else:
            base_query = f"{season.lower()} {weather_kw}"
            
        return f"{base_query} -people -person -interior -buildings -architecture"

    def _get_local_fallback(self):
        """
        Converts the bundled local image to base64 for reliable offline performance.
        """
        try:
            if os.path.exists(self.fallback_path):
                with open(self.fallback_path, "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode()
                return f"data:image/jpeg;base64,{encoded}"
        except Exception as e:
            print(f"Fallback reading error: {e}")
            
        return "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1973"

    def _fetch_unsplash_images(self, query):
        """
        Queries Unsplash Search API with retries and timeouts.
        """
        if not self.unsplash_key:
            return None
            
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 15,
            "client_id": self.unsplash_key
        }
        
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        return results
                elif response.status_code == 403:
                    print("Unsplash API Rate limit reached.")
                    break
            except requests.RequestException as e:
                print(f"Unsplash API attempt {attempt+1} failed: {e}")
                time.sleep(0.3)
                
        return None

    def _fetch_pexels_images(self, query):
        """
        Queries Pexels Search API with retries and timeouts.
        """
        if not self.pexels_key:
            return None
            
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": self.pexels_key
        }
        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 15
        }
        
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    photos = data.get("photos", [])
                    if photos:
                        normalized_results = []
                        for photo in photos:
                            normalized_results.append({
                                "id": f"pexels_{photo.get('id')}",
                                "urls": {
                                    "raw": photo.get("src", {}).get("original", ""),
                                    "regular": photo.get("src", {}).get("large2x", "")
                                }
                            })
                        return normalized_results
            except requests.RequestException as e:
                print(f"Pexels API attempt {attempt+1} failed: {e}")
                time.sleep(0.3)
                
        return None

    def get_background_url(self, weather_main, time_info):
        """
        Returns the optimized background URL based on weather/time/season,
        utilizing state caching and preloading strategies. Fallback sequence:
        Unsplash -> Pexels -> Local Image. Forces a refresh if showing the fallback
        and valid keys are present.
        """
        current_time = time.time()
        time_of_day = self.get_time_of_day_bucket(time_info.get("time", ""))
        season = self.get_season_bucket(time_info.get("day_of_year", ""))
        
        if "bg_current_url" not in st.session_state:
            st.session_state["bg_current_url"] = ""
            st.session_state["bg_next_url"] = ""
            st.session_state["bg_last_weather"] = ""
            st.session_state["bg_last_time_bucket"] = ""
            st.session_state["bg_last_refresh_time"] = 0.0
            st.session_state["bg_recent_ids"] = []

        # Check if the current cached background is a fallback
        is_showing_fallback = (
            not st.session_state["bg_current_url"] or
            st.session_state["bg_current_url"].startswith("data:image") or
            "images.unsplash.com/photo-1560518883-ce09059eeffa" in st.session_state["bg_current_url"]
        )

        weather_changed = st.session_state["bg_last_weather"] != weather_main
        time_changed = st.session_state["bg_last_time_bucket"] != time_of_day
        time_expired = (current_time - st.session_state["bg_last_refresh_time"]) >= 1800
        first_launch = not st.session_state["bg_current_url"]

        # Force a refresh attempt if showing the fallback and we have valid API keys
        has_keys = bool(self.unsplash_key or self.pexels_key)
        force_keys_refresh = is_showing_fallback and has_keys and (current_time - st.session_state["bg_last_refresh_time"] > 8)

        should_refresh = weather_changed or time_changed or time_expired or first_launch or force_keys_refresh

        if should_refresh:
            query = self.generate_intelligent_query(weather_main, time_of_day, season)
            
            # Fetch from Unsplash first
            results = self._fetch_unsplash_images(query)
            
            # Fallback to Pexels if Unsplash failed/limited/unauthorized
            if not results:
                results = self._fetch_pexels_images(query)
            
            if results:
                recent_ids = st.session_state.get("bg_recent_ids", [])
                valid_images = [img for img in results if img.get("id") not in recent_ids]
                
                if not valid_images:
                    valid_images = results
                    
                selected_current = random.choice(valid_images)
                
                # Append standard Unsplash/Pexels dynamic query optimization for 4K / High Res
                curr_url = selected_current["urls"]["raw"]
                if "unsplash.com" in curr_url:
                    curr_url += "&auto=format&fit=crop&w=3840&q=85"
                elif "pexels.com" in curr_url:
                    if "?" in curr_url:
                        curr_url += "&auto=compress&cs=tinysrgb&fit=crop&w=3840&q=85"
                    else:
                        curr_url += "?auto=compress&cs=tinysrgb&fit=crop&w=3840&q=85"
                    
                curr_id = selected_current.get("id")
                
                # Update recent photo cache
                recent_ids.append(curr_id)
                if len(recent_ids) > 10:
                    recent_ids.pop(0)
                st.session_state["bg_recent_ids"] = recent_ids
                
                # Select a separate preloaded image
                remaining_images = [img for img in valid_images if img.get("id") != curr_id]
                if remaining_images:
                    selected_next = random.choice(remaining_images)
                    next_url = selected_next["urls"]["raw"]
                    if "unsplash.com" in next_url:
                        next_url += "&auto=format&fit=crop&w=3840&q=85"
                    elif "pexels.com" in next_url:
                        if "?" in next_url:
                            next_url += "&auto=compress&cs=tinysrgb&fit=crop&w=3840&q=85"
                        else:
                            next_url += "?auto=compress&cs=tinysrgb&fit=crop&w=3840&q=85"
                else:
                    next_url = curr_url
                
                st.session_state["bg_current_url"] = curr_url
                st.session_state["bg_next_url"] = next_url
                st.session_state["bg_last_weather"] = weather_main
                st.session_state["bg_last_time_bucket"] = time_of_day
                st.session_state["bg_last_refresh_time"] = current_time
            else:
                # Fallback to local base64 if both APIs failed
                if not st.session_state["bg_current_url"]:
                    fallback_url = self._get_local_fallback()
                    st.session_state["bg_current_url"] = fallback_url
                    st.session_state["bg_next_url"] = fallback_url
                    
        return st.session_state.get("bg_current_url")
