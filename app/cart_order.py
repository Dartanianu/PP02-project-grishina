from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QWidget,
    QLabel,
    QHBoxLayout,
    QInputDialog,
    QPushButton,
    QVBoxLayout
)

from database.connection import DatabaseError
from database.get_orders import create_order, get_status
from database.get_users import get_all_users, get_full_name
from tech.discount import format_price
from tech.messages import show_confirm, show_error, show_info, show_warning
from tech.table_helper import create_table, fill_table, selected_row


class CartPage(QWidget):
    page_title = "Оформление заказа"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        
        client_layount = QHBoxLayout()
        self.client_lable = QLabel("Клиент:")
        client_layount.addWidget(self.client_lable)
        
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(320)
        client_layount.addWidget(self.client_combo)
        client_layount.addStretch()
        layout.addLayout(client_layount)

        status_layout = QHBoxLayout()
        self.status_lable = QLabel("Статус:")
        status_layout.addWidget(self.status_lable)
        
        self.status_combo = QComboBox()
        self.status_combo.setMinimumWidth(320)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        self.table = create_table(['Товар', 'Вариация', 'Количество', 'Цена за ед.', 'Сумма'])
        layout.addWidget(self.table)

        self.total_lable = QLabel()
        self.total_lable.setObjectName("totalLabel")
        layout.addWidget(self.total_lable)

        buttons_layout = QHBoxLayout()
        
        change_button = QPushButton("Изменить количество")
        change_button.clicked.connect(self.change_quantity)
        buttons_layout.addWidget(change_button)

        remove_button = QPushButton("Удалить позицию")
        remove_button.clicked.connect(self.remove_product)
        buttons_layout.addWidget(remove_button)

        add_more_button = QPushButton("Добавить товар")
        add_more_button.clicked.connect(self.add_product)
        buttons_layout.addWidget(add_more_button)

        buttons_layout.addStretch()

        cancel_button = QPushButton("Отказаться от заказа")
        cancel_button.clicked.connect(self.cancel_order)
        buttons_layout.addWidget(cancel_button)

        confirm_button = QPushButton("Подтвердить заказ")
        confirm_button.setObjectName("confirmButton")
        confirm_button.clicked.connect(self.confirm_order)
        buttons_layout.addWidget(confirm_button)
        layout.addLayout(buttons_layout)
        
        self.load_clients()
        self.load_status()

    def load_clients(self):
        is_staff = self.main_window.is_staff()
        self.client_lable.setVisible(is_staff)
        self.client_combo.setVisible(is_staff)
        if not is_staff:
            return
        try:
            users = get_all_users()
        except DatabaseError as e:
            show_error(self, str(e))
            return
        
        for user in users:
            self.client_combo.addItem(f"{get_full_name(user)} ({user['login']})", user["user_id"])
        own_index = self.client_combo.findData(self.main_window.current_user["user_id"])
        self.client_combo.setCurrentIndex(max(own_index, 0))
    
    def load_status(self):
        is_staff = self.main_window.is_staff()
        self.status_lable.setVisible(is_staff)
        self.status_combo.setVisible(is_staff)
        if not is_staff:
            return
        try:
            status = get_status()
        except DatabaseError as e:
            show_error(self, str(e))
            return
        
        self.status_combo.clear()
        for s in status:
            self.status_combo.addItem(s['name'], s['id'])
            
        default_index = self.status_combo.findText("Новый")
        if default_index != -1:
            self.status_combo.setCurrentIndex(default_index)

    
    def on_show(self):
        self.refresh_table()

    def refresh_table(self):
        rows = []
        total = Decimal(0)
        for item in self.main_window.cart_items:
            item_total = item['price'] * item['quantity']
            total += item_total
            rows.append(
                [
                    f"{item['product_name']} | {item['manufacturer']}",
                    item['variation_name'],
                    item['quantity'],
                    format_price(item['price']),
                    format_price(item_total),
                 
                 ]
            )
        fill_table(self.table, rows)
        self.total_lable.setText(f"Итого: {format_price(total)}")
        self.main_window.update_header()
    
    def get_selected_item(self):
        row = selected_row(self.table)
        if row < 0:
            show_warning(self, "Выберите позицию в таблице.")
            return None
        return self.main_window.cart_items[row]

    def change_quantity(self):
        item = self.get_selected_item()
        if item is None:
             return
        new_quantity, accepted = QInputDialog.getInt(
            self,
            "Изменение количества",
            f"Количество товара (от 1 до {item['stock_quantity']}):",
            item['quantity'],
            1,
            item['stock_quantity'],
        )
        if accepted:
            item['quantity'] = new_quantity
            self.refresh_table()

    def remove_product(self):
        item = self.get_selected_item()
        if item is None:
            return
        question = f"Удалить из заказа '{item['product_name']}', вариация {item['variation_name']}?"
        if show_confirm(self, question):
            self.main_window.cart_items.remove(item)
            self.refresh_table()

    def add_product(self):
        from app.catalog_page import CatalogPage

        self.main_window.open_page(CatalogPage(self.main_window))

    def cancel_order(self):
        if not self.main_window.cart_items:
            show_info(self, "Заказ пуст - отменять нечего")
            return
        if show_confirm(self, "Отказаться от оформления заказа? Все позиции будут удалены из корзины."):
            self.main_window.cart_items.clear()
            self.refresh_table()
            show_info(self, "Оформление заказа отменено")

    def confirm_order(self):
        if not self.main_window.cart_items:
            show_info(self, "В корзине нет товаров. Добавьте позиции из каталога.")
            return
        client_id = self.main_window.current_user['user_id']
        status_id = 1
        if self.main_window.is_staff():
            client_id = self.client_combo.currentData()
            status_id = self.status_combo.currentData()
        if not show_confirm(self, "Подтвердить и формить заказ?"):
            return
        try:
            order_id = create_order(client_id, self.main_window.cart_items, status_id)
        except DatabaseError as e:
            show_error(self, str(e))
            return
        self.main_window.cart_items.clear()
        show_info(self, f"Заказ №{order_id} успешно оформлен.")
        self.return_after_order()

    def return_after_order(self):
        from app.catalog_page import CatalogPage

        self.main_window.show_root_page(CatalogPage(self.main_window))

