from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from config import IMAGES_DIR, PLACEHOLDER_PNG

cache = {}

def _draw_empty_picture(width, height):
    image_lable = QLabel()
    image_lable.setFixedSize(width, height)
    image_lable.setText("НЕТ ФОТО")


def load_product_image(image_path, width, height):
    cache_key = (image_path, width, height)
    if cache_key in cache:
        return cache[cache_key]
    pixmap = QPixmap()
    if image_path:
        pixmap.load(str(IMAGES_DIR / image_path))
    # Если файла нет или он повреждён — показываем заглушку picture.png из ресурсов
    if pixmap.isNull():
        pixmap.load(str(PLACEHOLDER_PNG))
    if pixmap.isNull():
        pixmap = _draw_empty_picture(width, height)
    scaled = pixmap.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    cache[cache_key] = scaled
    return scaled