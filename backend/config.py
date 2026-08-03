import os

def get_database_url():
    mysql_user = os.environ.get("MYSQL_USER", "root")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "password")
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_port = os.environ.get("MYSQL_PORT", "3306")
    mysql_db = os.environ.get("MYSQL_DB", "aegiscr_db")
    
    # Primary MySQL Connection String
    mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    
    # Default to SQLite fallback if MySQL is not configured or for simple local execution
    sqlite_url = "sqlite:///./aegiscr_fallback.db"
    
    return os.environ.get("DATABASE_URL", sqlite_url)

DATABASE_URL = get_database_url()
SECRET_KEY = os.environ.get("SECRET_KEY", "aegiscr-super-secret-key-2026")
ALGORITHM = "HS256"
