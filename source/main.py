import sys
import numpy as np
import re
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PySide2.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def safe_eval(expr, x_val):
    safe_dict = {
        "x": x_val,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "sqrt": np.sqrt,
        "log10": np.log10,
        "abs": np.abs,
        "pi": np.pi,
        "e": np.e
    }
    expr = expr.replace('^', '**')
    if re.search(r'[^0-9x+\-*/() .sincostaexpsqrtlog10pieabs]', expr):
        raise ValueError("Invalid character in expression")
    try:
        return eval(expr, {"__builtins__": None}, safe_dict)
    except Exception as e:
        raise ValueError(f"Invalid expression: {'Type In a Correct Function'}")

def parse_and_evaluate(func_str, x_min, x_max):
    x = np.linspace(x_min, x_max, 1000)
    y = np.vectorize(lambda x_val: safe_eval(func_str, x_val))(x)
    return x, y

class FunctionPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Function Plotter")
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        input_layout = QHBoxLayout()
        self.function_input = QLineEdit()
        self.x_min_input = QLineEdit()
        self.x_max_input = QLineEdit()
        input_layout.addWidget(QLabel("Function f(x):"))
        input_layout.addWidget(self.function_input)
        input_layout.addWidget(QLabel("x min:"))
        input_layout.addWidget(self.x_min_input)
        input_layout.addWidget(QLabel("x max:"))
        input_layout.addWidget(self.x_max_input)
        main_layout.addLayout(input_layout)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_function)
        main_layout.addWidget(self.plot_button)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

    def validate_input(self):
        func_str = self.function_input.text().strip()
        x_min_str = self.x_min_input.text().strip()
        x_max_str = self.x_max_input.text().strip()

        if not func_str:
            raise ValueError("Please enter a function.")

        if not x_min_str or not x_max_str:
            raise ValueError("Please enter both x_min and x_max values.")

        try:
            x_min = safe_eval(x_min_str, 0)
            x_max = safe_eval(x_max_str, 0)
        except ValueError:
            raise ValueError("Invalid x_min or x_max value. Please enter valid numbers.")

        if x_min >= x_max:
            raise ValueError("x_min must be less than x_max.")

        return func_str, x_min, x_max

    def plot_function(self):
        try:
            func_str, x_min, x_max = self.validate_input()
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
            return

        try:
            x, y = parse_and_evaluate(func_str, x_min, x_max)
        except ValueError as e:
            QMessageBox.warning(self, "Function Error", str(e))
            return

        if np.any(np.isnan(y)) or np.any(np.isinf(y)):
            QMessageBox.warning(self, "Plot Error", "The function produces invalid values (NaN or Infinity) in the given range.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(x, y)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title(f'Plot of f(x) = {func_str}')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    plotter = FunctionPlotter()
    plotter.show()
    sys.exit(app.exec_())