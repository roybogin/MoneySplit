import sys
from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

ROOMMATES = ["Bogin", "Khashper", "Chuprov", "Ory", "Harel", "Eyal"]


class ProductLabel(QLabel):
    def __init__(self, text, id, clicked):
        super(ProductLabel, self).__init__(text)
        self.id = id
        self.clicked = clicked

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit(self.id)

class CreateReceipt(QWidget):
    clicked_signal = pyqtSignal(int)

    def __init__(self, done_signal):
        super().__init__()
        self.id = 0
        self.clicked_signal.connect(self.delete)
        self.groceries = []
        self.total = 0.0
        self.done_signal = done_signal
        self.total_label = QLabel('total: ' + str(self.total))
        self.total_label.setStyleSheet("font-weight: bold")

        self.layout = QVBoxLayout()

        insert_layout = QHBoxLayout()
        self.product = QLineEdit()
        insert_layout.addWidget(self.product)
        self.price = QLineEdit()
        insert_layout.addWidget(self.price)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_item)
        insert_layout.addWidget(add_button)

        self.bill_layout = QVBoxLayout()

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.finish_list)

        self.layout.addLayout(insert_layout)
        self.layout.addLayout(self.bill_layout)
        self.layout.addWidget(self.total_label)
        self.layout.addWidget(done_button)

        self.setLayout(self.layout)

    def delete(self, lbl_id):
        for idx, lbl in enumerate(self.groceries):
            if lbl[2].id == lbl_id:
                #self.bill_layout.removeWidget(lbl[2])
                self.groceries.remove(lbl)
                self.total -= lbl[1]
                self.total = round(self.total*100)/100
                lbl[2].deleteLater()
                self.total_label.setText(f'total: {self.total}')
    
    def add_item(self):
        if self.product.text() != "" and self.price.text() != "":
            try:
                price_float = float(self.price.text())
                label = ProductLabel(f'{self.product.text()}\t{price_float}', self.id, self.clicked_signal)
                self.id += 1
                self.bill_layout.addWidget(label)
                self.groceries.append((self.product.text(), price_float, label))
                self.total += price_float
                self.total = round(self.total*100)/100
                self.total_label.setText(f'total: {self.total}')
            except ValueError:
                print("not a price")

    def finish_list(self):
        self.done_signal.emit(self.groceries)


class ChooseGroceries(QWidget):
    def __init__(self, groceries, done_signal):
        super(ChooseGroceries, self).__init__()
        self.set_all = []
        self.check_list = []
        self.table = QTableWidget()
        self.groceries = groceries
        self.done_signal = done_signal
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.set_table()

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.finish_assign)

        self.layout.addWidget(done_button)
        self.setLayout(self.layout)

    def set_table(self):
        for i in range(len(ROOMMATES)):
            self.table.insertColumn(i)
        self.table.insertColumn(len(ROOMMATES))
        self.table.setHorizontalHeaderLabels(ROOMMATES + [""])
        for i in range(len(self.groceries)):
            self.table.insertRow(i)
        self.table.setVerticalHeaderLabels(map(lambda a: a[0], self.groceries))
        for i in range(len(self.groceries)):
            self.check_list.append([])
            item = QPushButton("Toggle All")
            item.clicked.connect(partial(self.toggle_all, i))
            self.table.setCellWidget(i, len(ROOMMATES), item)
            self.set_all.append(item)
            for j in range(len(ROOMMATES)):
                item = QTableWidgetItem()
                item.setCheckState(Qt.Unchecked)
                self.check_list[i].append(item)
                self.table.setItem(i, j, item)

    def finish_assign(self):
        self.done_signal.emit(self.check_list, self.groceries)

    def toggle_all(self, i):
        lst = self.check_list[i]
        if not all(map(lambda item: item.checkState() == Qt.Checked, lst)):
            for item in lst:
                item.setCheckState(Qt.Checked)
        else:
            for item in lst:
                item.setCheckState(Qt.Unchecked)

class MainClass(QWidget):
    finish_create_list = pyqtSignal(list)
    finish_split_money = pyqtSignal(list, list)

    def __init__(self):
        super(MainClass, self).__init__()
        self.groceries = None
        self.layout = QVBoxLayout()
        self.stack = QStackedWidget()
        r = CreateReceipt(self.finish_create_list)
        self.finish_create_list.connect(self.finished_list)
        self.finish_split_money.connect(self.finished_split)

        self.stack.addWidget(r)
        self.stack.setCurrentWidget(r)
        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

    def finished_list(self, lst):
        self.groceries = lst
        split_money = ChooseGroceries(self.groceries, self.finish_split_money)
        self.stack.addWidget(split_money)
        self.stack.setCurrentWidget(split_money)

    def finished_split(self, cost_lst, price_lst):
        costs = [0 for _ in ROOMMATES]
        for grocery in range(len(cost_lst)):
            pays = [False for _ in ROOMMATES]
            for roommate in range(len(ROOMMATES)):
                if cost_lst[grocery][roommate].checkState() == Qt.Checked:
                    pays[roommate] = True
            if not any(pays):
                continue
            pay_sum = sum(pays)
            for roommate in range(len(ROOMMATES)):
                if pays[roommate]:
                    costs[roommate] += price_lst[grocery][1] / pay_sum
                costs[roommate] = round(costs[roommate]*100)/100

        for idx, roommate in enumerate(ROOMMATES):
            print(f'{roommate}: {costs[idx]}')
        print(f'Total: {sum(costs)}')
        app.exit(0)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_class = MainClass()
    main_class.show()
    app.exec_()