from PySide6.QtCore import Qt
from PySide6.QtWidgets import(
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from database.connection import DatabaseError
from database.get_users import find_user_by_login
from tech.messages import show_error, show_warning

class LoginPage(QWidget):
    page_title = "Вход в программу"

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        form = QWidget()
        form.setObjectName("toolbar")
        form.setFixedHeight(400)
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.addSpacing(10)

        form_layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setMaxLength(50)
        self.login_input.returnPressed.connect(self.try_login)
        form_layout.addWidget(self.login_input)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.try_login)
        form_layout.addWidget(login_button)
        
        guest_button = QPushButton("Войти как гость")
        guest_button.clicked.connect(self.main_window.login_as_guest)
        form_layout.addWidget(guest_button)

        layout = QVBoxLayout(self)
        layout.addWidget(form)

    def on_show(self):
        self.login_input.setFocus()

    def try_login(self):
        login = self.login_input.text().strip()
        if not login:
            show_warning(self, "Введите логин, чтобы войти.")
            return
        try:
            user = find_user_by_login(login)
        except DatabaseError as e:
            show_error(self, str(e))
            return
        if user is None:
            show_error(self, f"Пользователь с логином '{login}', не найден.")
            return
        self.main_window.login(user)