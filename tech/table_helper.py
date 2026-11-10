from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

def create_table(column_names):
    table = QTableWidget(0, len(column_names))
    table.setHorizontalHeaderLabels(column_names)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.SelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    return table

def fill_table(table, rows):
    table.setRowCount(0)
    for row_values in rows:
        row_index = table.rowCount()
        table.insertRow(row_index)
        for column_index, value in enumerate(row_values):
            table.setItem(row_index, column_index, QTableWidgetItem(str(value)))

def selected_row(table):
    rows = table.selectionModel().selectedRows()
    if not rows:
        return -1
    return rows[0].row()
