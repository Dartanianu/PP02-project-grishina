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
from database.get_orders import get_orders, delete_order
from tech.messages import show_confirm, show_info, show_error, show_warning
from tech.table_helper import create_table, fill_table, selected_row


class OrderPage(QWidget):
    page_title = "Список заказы"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.orders = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)

        self.table = create_table(["ФИО клиента", "Дата заказа", "Номер заказа", "Сумма"])
        self.table.doubleClicked.connect(self.open_details)
        layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()

        add_button = QPushButton("Добавить заказ")
        add_button.setObjectName("accentButton")
        add_button.clicked.connect(self.add_order)
        buttons_layout.addWidget(add_button)

        details_button = QPushButton("Состав заказа")
        details_button.clicked.connect(self.open_details)
        buttons_layout.addWidget(details_button)

        self.edit_button = QPushButton("Редактировать заказ")
        self.edit_button.clicked.connect(self.edit_order)
        self.edit_button.setVisible(self.main_window.is_admin())
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addStretch()

        delete_button = QPushButton("Удалить заказ")
        delete_button.clicked.connect(self.delete_order_selected)
        buttons_layout.addWidget(delete_button)

        layout.addLayout(buttons_layout)

    def on_show(self):
        self.load_orders()

    def load_orders(self):
        try:
            self.orders = get_orders()
        except DatabaseError as e:
            show_error(self, str(e))
            return
        
        rows = []
        for order in self.orders:
            rows.append(
                [
                    order["client_name"],
                    order["order_date"].strftime("%d.%m.%Y"),
                    order["order_id"],
                    order["total_sum"],
                ]
            )
        fill_table(self.table, rows)

    def get_selected_order(self):
        row = selected_row(self.table)
        if row < 0:
            show_warning(self, "Сначала выберите заказ из таблицы.")
            return None
        return self.orders[row]
    
    def add_order(self):
        from app.catalog_page import CatalogPage

        self.main_window.open_page(CatalogPage(self.main_window))

    def open_details(self):
        from app.order_details_page import OrderDetailsPage

        order = self.get_selected_order()
        if order is not None:
            self.main_window.open_page(OrderDetailsPage(self.main_window, order["order_id"], edit_mode=False))

    def edit_order(self):
        from app.order_details_page import OrderDetailsPage

        if not self.main_window.is_admin():
            show_error(self, "Редактировать заказы может только администратор.")
            return
        order = self.get_selected_order()
        if order is not None:
            self.main_window.open_page(OrderDetailsPage(self.main_window, order["order_id"], edit_mode=True))
    
    def delete_order_selected(self):
        order = self.get_selected_order()
        if order is None:
            return
        question = (
            f"Удалить заказ №{order['order_id']} от {order['order_date']:%d.%m.%Y} "
            f"({order['client_name']})?"
        )
        if not show_confirm(self, question):
            return
        try:
            delete_order(order["order_id"])
        except DatabaseError as e:
            show_error(self, f"Заказ не удален. {e}")
        show_info(self, f"Заказа №{order['order_id']} удален.")
        self.load_orders()