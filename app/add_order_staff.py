from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QPushButton
)

from database.connection import DatabaseError
from database.get_products import get_products, get_product_variations
from tech.discount import apply_discount, format_price
from tech.image_loader import load_product_image
from tech.messages import show_error, show_info, show_warning

class AddOrderStaff(QWidget):
    page_title = "Создание заказа"
    
    def __init__(main_window):
        