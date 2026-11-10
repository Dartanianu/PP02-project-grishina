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


class ProductCard(QWidget):
    page_title = "Карточка товара"

    def __init__(self, main_window, product):
        super().__init__()
        self.main_window = main_window
        self.product = product
        self.variation = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(30)

        image_lable = QLabel()
        image_lable.setFixedSize(340, 260)
        image_lable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_lable.setPixmap(load_product_image(product['image_path'], 340, 260))

        layout.addWidget(image_lable, 0, Qt.AlignmentFlag.AlignTop)

        info_layout = QVBoxLayout()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.addRow("Наименование:", self._wrapped_label(product['name']))
        form.addRow("Производство:", self._wrapped_label(product['manufacturer']))
        form.addRow("Категория:", self._wrapped_label(f"{product['category']} / {product['subcategory']}"))
        form.addRow("Цена со скидкой:", self._wrapped_label(product['final_price']))
        form.addRow("Состав:", self._wrapped_label(product['compound']))
        form.addRow("Описание:", self._wrapped_label(product['description']))
        self.variation_label = self._wrapped_label("")
        form.addRow("Вариации:", self.variation_label)

        self.variation_combo = QComboBox()
        form.addRow("Доступные вариации:", self.variation_combo)
        self.quantity_input = QLineEdit("1")
        self.quantity_input.setValidator(QIntValidator(1, 999, self))
        self.quantity_input.setPlaceholderText('Целое число больше 0')
        self.quantity_input.setMaximumWidth(150)
        form.addRow("Количество товара:", self.quantity_input)

        info_layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить в заказ")
        self.add_button.setObjectName("accentButton")
        self.add_button.clicked.connect(self.add_to_card)
        buttons_layout.addWidget(self.add_button)

        cart_button = QPushButton("Перейти к заказу")
        cart_button.clicked.connect(self.main_window.open_cart)
        buttons_layout.addWidget(cart_button)
        buttons_layout.addStretch()

        info_layout.addLayout(buttons_layout)
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

    @staticmethod
    def _wrapped_label(text):
        label = QLabel(str(text or "—"))
        label.setWordWrap(True)
        return label
    
    def on_show(self):
        self.load_variations()

    def load_variations(self):
        try:
            self.variations = get_product_variations(self.product['product_id'])
        except DatabaseError as e:
            show_error(self, str(e))
            return
        
        variation_names = [variation['name'] for variation in self.variations]
        self.variation_label.setText(", ".join(variation_names) if variation_names else "нет данных")

        self.variation_combo.clear()
        for variation in self.variations:
            avable = self.get_avable_quantity(variation)
            if avable > 0:
                text = f"{variation['name']} (в наличии: {avable})"
                self.variation_combo.addItem(text, variation)
        is_var = self.variation_combo.count() > 0
        self.add_button.setEnabled(is_var)
        if not is_var:
            self.variation_combo.addItem("Нет доступных размеров")

    def get_avable_quantity(self, variation):
        in_cart = 0
        for item in self.main_window.cart_items:
            if item['product_id'] == self.product['product_id'] and item['variation_id'] == variation['variation_id']:
                in_cart += item['quantity']

        return variation['quantity_available'] - in_cart       


    def add_to_card(self):
        variation = self.variation_combo.currentData()
        if variation is None:
            show_warning(self, "Выберите вариацию из списка доступных.")
            return
        quantity_text = self.quantity_input.text().strip()
        if not quantity_text:
            show_warning(self, "Укажите количество товара(целое число больше 0)")
            self.quantity_input.setFocus()
            return
        quantity = int(quantity_text)
        avaible = self.get_avable_quantity(variation)
        if quantity <= 0:
            show_error(self, "Количество товара должно быть больше 0.")
            return
        if quantity > avaible:
            show_error(
                self,
                f"Нельзя заказать {quantity} товаров. Доступно только {avaible}."
            )
            return
        self._put_into_cart(variation, quantity)
        self.main_window.update_header()
        self.load_variations()
        variation_text = variation['name']
        show_info(self, f"В корзину добаавлен товар: {self.product['name']}, вариация {variation_text}, количество {quantity}")

    def _put_into_cart(self, variation, quantity):
        for item in self.main_window.cart_items:
            if item['product_id'] == self.product['product_id'] and item['variation_id'] == variation['variation_id']:
                item['quantity'] += quantity
                return
        self.main_window.cart_items.append(
            {
                "product_id": self.product['product_id'],
                "product_name": self.product['name'],
                "manufacturer": self.product['manufacturer'],
                "variation_id": variation['variation_id'],
                "variation_name": variation['name'],
                "quantity": quantity,
                "stock_quantity": variation['quantity_available'],
                "price": self.product['final_price']
            }
        )

                    