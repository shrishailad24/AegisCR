import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure local import paths are loaded correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PythonProject1")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.routers import auth, property, valuation, loan, documents, reports, gold, vehicle, applications, audit
from backend.database.database import engine, Base

# Auto-create MySQL / SQLite tables on startup
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"Database table creation notice: {e}")

def load_env():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key_val = line.split("=", 1)
                        if len(key_val) == 2:
                            key = key_val[0].strip()
                            val = key_val[1].strip()
                            if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                                val = val[1:-1]
                            os.environ[key] = val
        except Exception as e:
            print(f"Error loading env manually in main.py: {e}")

load_env()

app = FastAPI(
    title="🛡️ AegisCR Decisions Platform Backend",
    description="Enterprise AI Banking & Multi-Product Loan Underwriting API backed by MySQL & SQLAlchemy.",
    version="2.5.0"
)

from fastapi.middleware.gzip import GZipMiddleware

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable GZip Compression Middleware (Compress responses larger than 1000 bytes)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register routers
app.include_router(auth.router)
app.include_router(property.router)
app.include_router(valuation.router)
app.include_router(loan.router)
app.include_router(documents.router)
app.include_router(reports.router)
app.include_router(gold.router)
app.include_router(vehicle.router)
app.include_router(applications.router)
app.include_router(audit.router)

@app.get("/gold-price")
def get_gold_price_root():
    """Direct root GET /gold-price endpoint mapping to live GoldAPI feed."""
    return gold.fetch_live_gold_price()

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
