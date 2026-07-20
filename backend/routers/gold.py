import os
import requests
from datetime import datetime

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter(
        prefix="/api",
        tags=["Gold Price & Loan Appraisal"]
    )
except ImportError:
    router = None
    APIRouter = None
    HTTPException = None

def fetch_live_gold_price():
    api_key = os.environ.get("GOLD_API_KEY", "goldapi-85cf9ed73967f99a65d1e16204a9ccac-io")
    url = "https://www.goldapi.io/api/XAU/INR"
    
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            data = response.json()
            price_ounce = data.get("price", 198500.0)
            price_gram_24k = data.get("price_gram_24k")
            if not price_gram_24k:
                price_gram_24k = price_ounce / 31.1034768
            
            price_gram_22k = data.get("price_gram_22k")
            if not price_gram_22k:
                price_gram_22k = price_gram_24k * (22.0 / 24.0)
                
            price_gram_18k = data.get("price_gram_18k")
            if not price_gram_18k:
                price_gram_18k = price_gram_24k * (18.0 / 24.0)
                
            ts = data.get("timestamp", int(datetime.now().timestamp()))
            dt_str = datetime.fromtimestamp(ts).strftime("%d %b %Y, %I:%M %p IST")

            return {
                "timestamp": ts,
                "last_updated": dt_str,
                "metal": data.get("metal", "XAU"),
                "currency": data.get("currency", "INR"),
                "price": round(price_ounce, 2),
                "price_gram_24k": round(price_gram_24k, 2),
                "price_gram_22k": round(price_gram_22k, 2),
                "price_gram_18k": round(price_gram_18k, 2),
                "ch": round(data.get("ch", 0.0), 2),
                "chp": round(data.get("chp", 0.0), 2),
                "fallback": False
            }
        else:
            print(f"[GoldAPI Error Response] Status {response.status_code}: {response.text}")
            raise ValueError("Non-200 response code from GoldAPI")
    except Exception as e:
        print(f"[GoldAPI Fetch Exception] Triggering local fallback: {e}")
        ts = int(datetime.now().timestamp())
        dt_str = datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        return {
            "timestamp": ts,
            "last_updated": dt_str,
            "metal": "XAU",
            "currency": "INR",
            "price": 198500.00,
            "price_gram_24k": 6382.63,
            "price_gram_22k": 5850.75,
            "price_gram_18k": 4786.97,
            "ch": 120.50,
            "chp": 0.06,
            "fallback": True
        }

if router:
    @router.get("/gold-price")
    def get_gold_price():
        """
        GET /api/gold-price
        Fetches the live price of gold (XAU) in INR from GoldAPI.io.
        Falls back to realistic current pricing when the API limit or access key is invalid.
        """
        return fetch_live_gold_price()

