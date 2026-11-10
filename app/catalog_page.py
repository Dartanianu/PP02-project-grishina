from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout
)

from config import LOW_STOCK_COUNT
from database.connection import DatabaseError
from database.get_products import get_products, get_product_variations, get_categories
from tech.discount import apply_discount, format_price
from tech.image_loader import load_product_image
from tech.messages import show_error, show_info

ALL_CATEGORIES = "Все категории"
SORT_ASC = "Цена по возрастанию"
SORT_DESC = "Цена по убыванию"

class ProductCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, product):
        super().__init__()
        self.product = product
        is_low_product = product["total_quantity"] <= LOW_STOCK_COUNT
        self.setObjectName("productCardLow" if is_low_product else "productCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QGridLayout(self)
        layout.setContentsMargins(12, 10 , 20, 10)
        layout.setHorizontalSpacing(20)

        image_lable = QLabel()
        image_lable.setFixedSize(160, 120)
        image_lable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_lable.setPixmap(load_product_image(product["image_path"], 160, 120))
        layout.addWidget(image_lable, 0, 0, 4, 1)

        title_lable = QLabel(f"{product['manufacturer']} | {product['name']}")
        title_lable.setObjectName("cardTitle")
        title_lable.setWordWrap(True)
        layout.addWidget(title_lable, 0, 1)

        layout.addWidget(QLabel(f"Категория: {product['category']}"), 1, 1)
        layout.addWidget(QLabel(f"Количество: {product['total_quantity']}"), 2, 1)

        commp_lable = QLabel(f"Состав: {product['compound']}")
        commp_lable.setObjectName('smalllText')
        layout.addWidget(commp_lable, 3, 1)

        price_lable = QLabel(self._price())
        price_lable.setObjectName("cartPrice")
        price_lable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price_lable.setMaximumWidth(170)
        layout.addWidget(price_lable, 0, 2, 4, 1)
        layout.setColumnStretch(1, 1)

    def _price(self):
        final_price = format_price(self.product['final_price'])
        if not self.product['has_discount']:
            return final_price
        old_price = format_price(self.product["price"])
        return f"<s>{old_price}</s><br>{final_price}"
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.product)
        super().mousePressEvent(event)
    
class CatalogPage(QWidget):
    page_title = "Каталог товаров"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.products = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolBar")
        toolbar_layout = QHBoxLayout(self.toolbar)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск товара")
        self.search_input.textChanged.connect(self.refresh_catalog)
        toolbar_layout.addWidget(self.search_input)

        self.filter_cat = QComboBox()
        self.filter_cat.currentIndexChanged.connect(self.refresh_catalog)
        toolbar_layout.addWidget(self.filter_cat)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([SORT_ASC, SORT_DESC])
        self.sort_combo.currentIndexChanged.connect(self.refresh_catalog)
        toolbar_layout.addWidget(self.sort_combo)

        layout.addWidget(self.toolbar)
        self.toolbar.setVisible(self.main_window.is_authorized())

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        list_widget = QWidget()
        self.cards_layout = QVBoxLayout(list_widget)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        scroll_area.setWidget(list_widget)
        layout.addWidget(scroll_area)

    def on_show(self):
        self.load_data()

    def load_data(self):
        try:
            self.products = apply_discount(get_products())
            categories = get_categories()
        except DatabaseError as e:
            show_error(self, str(e))
            return
        selected_category = self.filter_cat.currentText()
        self.filter_cat.blockSignals(True)
        self.filter_cat.clear()
        self.filter_cat.addItem(ALL_CATEGORIES)
        self.filter_cat.addItems(categories)

        restored_index = self.filter_cat.findText(selected_category)
        self.filter_cat.setCurrentIndex(max(restored_index, 0))
        self.filter_cat.blockSignals(False)
        self.refresh_catalog()

    def get_v_products(self):
        if not self.main_window.is_authorized():
            return list(self.products)
        search_text = self.search_input.text().strip().casefold()
        category = self.filter_cat.currentText()
        result = []

        for product in self.products:
            if category != ALL_CATEGORIES and product['category'] != category:
                continue
            searchable_text = f"{product['name']} {product['description'] or ''}".casefold()
            if search_text and search_text not in searchable_text:
                continue
            result.append(product)
        sort_mode = self.sort_combo.currentText()
        if sort_mode == SORT_ASC:
            result.sort(key=lambda item: item["final_price"])
        elif sort_mode == SORT_DESC:
            result.sort(key=lambda item: item["final_price"], reverse=True)
        return result
    
    def refresh_catalog(self):
        while self.cards_layout.count() > 1:
            old_card = self.cards_layout.takeAt(0).widget()
            old_card.setParent(None)
            old_card.deleteLater()
        vis__products = self.get_v_products()
        for product in vis__products:
            card = ProductCard(product)
            card.clicked.connect(self.open_product)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
    def open_product(self, product):
        from app.product_page import ProductCard

        if not self.main_window.is_authorized():
            show_info(
                self,
                "Просмотр карточки и оформление заказа доступны только Авторизованным пользователсям."
            )
            return
        self.main_window.open_page(ProductCard(self.main_window, product))