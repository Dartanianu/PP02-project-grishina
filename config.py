from pathlib import Path

APP_NAME = "Сумки и аксессуары"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "database",
    "user": "postgres",
    "password": "123"
}

DISCOUNT_PRECENT = 25
LOW_STOCK_COUNT = 3

BASE_DIR = Path(__file__).resolve().parent

RESOURCES_DIR = BASE_DIR / "resources"
IMAGES_DIR = RESOURCES_DIR / "Images"
LOGO_PATH = RESOURCES_DIR / "logo.png"
ICON_PATH = RESOURCES_DIR / "icon.ico"
PLACEHOLDER_PNG = RESOURCES_DIR / "picture.png"