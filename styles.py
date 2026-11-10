MAIN_BACKGROUND = "#FFFFFF"
SECONDARY_BACKGROUND = "#D2F6E7"
ACCENT_COLOR = "#70B2AF"
LOW_STOCK_COLOR = "#FF8080"
FONT_FAMILY = "Calibri"

STYLESHEET = f"""
QWidget {{
    font-family: "{FONT_FAMILY}";
    font-size: 14px;
    color: #000000;
}}
QMainWindow, QStackedWidget, QScrollArea {{
    background-color: {MAIN_BACKGROUND};
}}
#header {{
    background-color: {SECONDARY_BACKGROUND};
}}
QPushButton {{
    background-color: {ACCENT_COLOR};
    color: #FFFFFF;
    border: 1px solid {ACCENT_COLOR};
    border-radius: 5px;
    padding: 4px 14px;
}}
QTableWidget {{
    background-color: {MAIN_BACKGROUND};
    selection-background-color: {ACCENT_COLOR};
    selection-color: #FFFFFF;
}}
QLineEdit, QCombox, QDateEdit {{
    background-color: {MAIN_BACKGROUND};
    border: 1px solid {ACCENT_COLOR};
    border-radius: 4px;
    padding: 4px 6px;
    min-height: 22px;
}}
#productCard {{
    background-color: {MAIN_BACKGROUND};
    border: 1px solid #808080;
}}
#productCardLow {{
    background-color: {LOW_STOCK_COLOR};
    border: 1px solid #808080;
}}
"""