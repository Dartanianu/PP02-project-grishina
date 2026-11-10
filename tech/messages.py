from PySide6.QtWidgets import QMessageBox

def show_error(parent, text):
    return QMessageBox.critical(parent, "Ошибка", text)

def show_warning(parent, text):
    return QMessageBox.warning(parent, "Предупреждение", text)

def show_info(parent, text):
    return QMessageBox.information(parent, "Информация", text)

def show_confirm(parent, text):
    answer = QMessageBox.question(
        parent,
        "Подтверждение действия",
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return answer == QMessageBox.StandardButton.Yes