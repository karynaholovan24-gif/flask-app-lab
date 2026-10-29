from pathlib import Path
from tinydb import TinyDB, Query

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "products.json"

db = TinyDB(DB_PATH)
products_table = db.table("products")

Product = Query()