import sys
from operator import add, sub, mul, truediv

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFontDatabase

from ui.design import Ui_MainWindow
import config

operations = {
    '+': add,
    '−': sub,
    '×': mul,
    '÷': truediv
}


class Calculator(QMainWindow):
    def __init__(self):
        super(Calculator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.LineEdit_entry = self.ui.LineEdit_entry
        self.tempLabel = self.ui.tempLabel
        self.entry_max_len = self.LineEdit_entry.maxLength()

        QFontDatabase.addApplicationFont("ui/fonts/Rubik-Regular.ttf")

        for btn in config.DIGIT_BUTTONS:
            getattr(self.ui, btn).clicked.connect(self.add_digit)

        self.ui.btn_calc.clicked.connect(self.calculate)
        for btn in config.MATH_OPERATIONS:
            getattr(self.ui, btn).clicked.connect(self.math_operation)

        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_ce.clicked.connect(self.clear_LineEdit)
        self.ui.btn_point.clicked.connect(self.add_point)
        self.ui.btn_neg.clicked.connect(self.negate)
        self.ui.btn_backspace.clicked.connect(self.backspace)

        self.new_action = False
        self.result = 0

    def add_digit(self) -> None:
        if self.new_action:
            self.clear_LineEdit()
            self.new_action = False

        self.remove_error()
        self.clear_tempLabel_if_equality()
        btn = self.sender()

        if btn.objectName() in config.DIGIT_BUTTONS:
            if self.LineEdit_entry.text() == '0':
                self.LineEdit_entry.setText(btn.text())
            else:
                self.LineEdit_entry.setText(self.LineEdit_entry.text() + btn.text())

        self.adjust_LineEdit_font_size()

    def add_point(self) -> None:
        self.clear_tempLabel_if_equality()
        if '.' not in self.LineEdit_entry.text():
            self.LineEdit_entry.setText(self.LineEdit_entry.text() + '.')
            self.adjust_LineEdit_font_size()

    def avoid_deleting_char_on_negation(self, entry: str) -> None:
        if len(entry) == self.entry_max_len + 1 and '-' in entry:
            self.LineEdit_entry.setMaxLength(self.entry_max_len + 1)
        else:
            self.LineEdit_entry.setMaxLength(self.entry_max_len)

    def negate(self) -> None:
        self.clear_tempLabel_if_equality()
        entry = self.LineEdit_entry.text()

        if '-' not in entry:
            if entry != '0':
                entry = '-' + entry
        else:
            entry = entry[1:]

        self.avoid_deleting_char_on_negation(entry)
        self.LineEdit_entry.setText(entry)
        self.adjust_LineEdit_font_size()

    def backspace(self) -> None:
        self.remove_error()
        self.clear_tempLabel_if_equality()
        entry = self.LineEdit_entry.text()

        if len(entry) != 1:
            if len(entry) == 2 and '-' in entry:
                self.LineEdit_entry.setText('0')
            else:
                self.LineEdit_entry.setText(entry[:-1])
        else:
            self.LineEdit_entry.setText('0')

        self.adjust_LineEdit_font_size()

    def clear_all(self) -> None:
        self.remove_error()
        self.LineEdit_entry.setText('0')
        self.adjust_LineEdit_font_size()
        self.tempLabel.clear()
        self.adjust_tempLabel_font_size()

    def clear_LineEdit(self) -> None:
        self.remove_error()
        self.clear_tempLabel_if_equality()
        self.LineEdit_entry.setText('0')
        self.adjust_LineEdit_font_size()

    def clear_tempLabel_if_equality(self) -> None:
        if self.get_sign() == '=':
            self.tempLabel.clear()
            self.adjust_tempLabel_font_size()

    @staticmethod
    def remove_zeros(number: float | int | str) -> str:
        num = str(float(number))
        return num.replace('.0', '') if num.endswith('.0') else num

    def add_tempLabel(self) -> None:
        btn = self.sender()
        entry = self.remove_zeros(self.LineEdit_entry.text())

        if not self.tempLabel.text() or self.get_sign() == '=':
            self.tempLabel.setText(entry + f' {btn.text()} ')
            self.adjust_tempLabel_font_size()
            self.LineEdit_entry.setText('0')
            self.adjust_LineEdit_font_size()

    def get_LineEdit_num(self) -> int | float:
        entry = self.LineEdit_entry.text().strip('.')
        return float(entry) if '.' in entry else int(entry)

    def get_tempLabel_num(self) -> int | float | None:
        if self.tempLabel.text():
            temp = self.tempLabel.text().strip('.').split()[0]
            return float(temp) if '.' in temp else int(temp)

    def get_sign(self) -> None | str:
        if self.tempLabel.text():
            return self.tempLabel.text().strip('.').split()[-1]

    def get_LineEdit_width(self) -> int:
        return self.LineEdit_entry.fontMetrics().boundingRect(self.LineEdit_entry.text()).width()

    def get_tempLabel_width(self) -> int:
        return self.tempLabel.fontMetrics().boundingRect(self.tempLabel.text()).width()

    def calculate(self) -> None | str:
        try:
            result = self.remove_zeros(
                (operations[self.get_sign()](self.get_tempLabel_num(), self.get_LineEdit_num()))
            )
            self.tempLabel.setText(
                self.tempLabel.text() + self.remove_zeros(self.LineEdit_entry.text()) + ' =')
            self.adjust_tempLabel_font_size()
            self.LineEdit_entry.setText(result)
            self.adjust_LineEdit_font_size()
            self.new_action = True
            self.result = result
            return result

        except KeyError:
            pass
        except ZeroDivisionError:
            self.show_zero_division_error()

    def show_zero_division_error(self) -> None:
        if self.get_tempLabel_num() == 0:
            self.show_error(config.ERROR_UNDEFINED)
        else:
            self.show_error(config.ERROR_ZERO_DIV)

    def math_operation(self) -> None:
        btn = self.sender()

        if not self.tempLabel.text():
            self.add_tempLabel()
        else:
            if self.get_sign() != btn.text():
                if self.get_sign() == '=':
                    self.add_tempLabel()
                else:
                    self.replace_tempLabel_sign()
            else:
                try:
                    self.tempLabel.setText(self.calculate() + f' {btn.text()} ')
                except TypeError:
                    pass

        self.adjust_tempLabel_font_size()

    def replace_tempLabel_sign(self) -> None:
        btn = self.sender()
        self.tempLabel.setText(self.tempLabel.text()[:-2] + f'{btn.text()} ')

    def show_error(self, text: str) -> None:
        self.LineEdit_entry.setMaxLength(len(text))
        self.LineEdit_entry.setText(text)
        self.adjust_LineEdit_font_size()
        self.disable_buttons(True)

    def remove_error(self) -> None:
        if self.LineEdit_entry.text() in (config.ERROR_UNDEFINED, config.ERROR_ZERO_DIV):
            self.LineEdit_entry.setMaxLength(self.entry_max_len)
            self.LineEdit_entry.setText('0')
            self.adjust_LineEdit_font_size()
            self.disable_buttons(False)

    def disable_buttons(self, disable: bool) -> None:
        for btn in config.BUTTONS_TO_DISABLE:
            getattr(self.ui, btn).setDisabled(disable)

        color = 'color: #888;' if disable else 'color: white;'
        self.change_buttons_color(color)

    def change_buttons_color(self, css_color: str) -> None:
        for btn in config.BUTTONS_TO_DISABLE:
            getattr(self.ui, btn).setStyleSheet(css_color)

    def adjust_LineEdit_font_size(self) -> None:
        font_size = config.DEFAULT_ENTRY_FONT_SIZE
        while self.get_LineEdit_width() > self.LineEdit_entry.width() - 15:
            font_size -= 1
            self.LineEdit_entry.setStyleSheet(f'font-size: {font_size}pt; border: none;')

        font_size = 1
        while self.get_LineEdit_width() < self.LineEdit_entry.width() - 60:
            font_size += 1

            if font_size > config.DEFAULT_ENTRY_FONT_SIZE:
                break

            self.LineEdit_entry.setStyleSheet(f'font-size: {font_size}pt; border: none;')

    def adjust_tempLabel_font_size(self) -> None:
        font_size = config.DEFAULT_FONT_SIZE
        while self.get_tempLabel_width() > self.tempLabel.width() - 10:
            font_size -= 1
            self.tempLabel.setStyleSheet(f'font-size: {font_size}pt; color: #888;')

        font_size = 1
        while self.get_tempLabel_width() < self.tempLabel.width() - 60:
            font_size += 1

            if font_size > config.DEFAULT_FONT_SIZE:
                break

            self.tempLabel.setStyleSheet(f'font-size: {font_size}pt; color: #888;')

    def resizeEvent(self, event) -> None:
        self.adjust_LineEdit_font_size()
        self.adjust_tempLabel_font_size()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec())
