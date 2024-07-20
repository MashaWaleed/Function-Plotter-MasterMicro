import sys
import numpy as np
import re
import random
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QMessageBox, QFileDialog, QScrollArea,
    QSplitter, QStyleFactory
)
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -------------------- Utility Functions --------------------

def safe_eval(expr, x_val):
    """Safely evaluate a mathematical expression."""
    safe_dict = {
        "x": x_val,
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "exp": np.exp, "sqrt": np.sqrt, "log10": np.log10,
        "abs": np.abs, "pi": np.pi, "e": np.e
    }
    expr = expr.replace('^', '**')
    if re.search(r'[^0-9x+\-*/() .sincostaexpsqrtlog10pieabs]', expr):
        raise ValueError("Invalid character in expression")
    try:
        return eval(expr, {"__builtins__": None}, safe_dict)
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")

def parse_and_evaluate(func_str, x_min, x_max):
    """Parse and evaluate the function over the given range."""
    x = np.linspace(x_min, x_max, 1000)
    y = np.vectorize(lambda x_val: safe_eval(func_str, x_val))(x)
    return x, y

# -------------------- GUI Components --------------------

class FunctionInput(QWidget):
    """Widget for inputting function and range."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.function_input = QLineEdit()
        self.x_min_input = QLineEdit()
        self.x_max_input = QLineEdit()
        layout.addWidget(QLabel("f(x):"))
        layout.addWidget(self.function_input)
        layout.addWidget(QLabel("x min:"))
        layout.addWidget(self.x_min_input)
        layout.addWidget(QLabel("x max:"))
        layout.addWidget(self.x_max_input)

class FunctionPlotter(QMainWindow):
    """Main window for the function plotter application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Function Plotter")
        self.setGeometry(100, 100, 1000, 600)

        self.setup_ui()
        self.setup_dark_theme()

        self.functions = []
        self.press = None
        self.cur_xlim = self.cur_ylim = None
        self.x0 = self.y0 = self.x1 = self.y1 = self.xpress = self.ypress = None

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        # Create a splitter for easy resizing
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        self.setup_left_panel()
        self.setup_right_panel()

        # Set initial sizes for splitter
        self.splitter.setSizes([300, 700])

        # Add toggle button
        self.setup_toggle_button()

    def setup_left_panel(self):
        """Set up the left panel with input controls."""
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)

        self.add_function_button = QPushButton("Add Function")
        self.add_function_button.clicked.connect(self.add_function_input)
        left_layout.addWidget(self.add_function_button)

        self.function_inputs_widget = QWidget()
        self.function_inputs_layout = QVBoxLayout(self.function_inputs_widget)
        self.function_inputs_layout.setAlignment(Qt.AlignTop)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.function_inputs_widget)
        left_layout.addWidget(scroll_area)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_functions)
        left_layout.addWidget(self.plot_button)

        self.save_button = QPushButton("Save Plot")
        self.save_button.clicked.connect(self.save_plot)
        left_layout.addWidget(self.save_button)

        self.splitter.addWidget(self.left_panel)

    def setup_right_panel(self):
        """Set up the right panel with the plot."""
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('scroll_event', self.zoom)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.splitter.addWidget(self.canvas)

    def setup_toggle_button(self):
        """Set up the toggle button for hiding/showing the left panel."""
        self.toggle_button = QPushButton()
        self.toggle_button.setIcon(QIcon("list.png"))
        self.toggle_button.setIconSize(QSize(20, 20))
        self.toggle_button.setFixedSize(QSize(30, 60))
        self.toggle_button.clicked.connect(self.toggle_left_panel)
        self.toggle_button.setParent(self)
        self.toggle_button.raise_()
        self.position_toggle_button()

    def setup_dark_theme(self):
        """Set up the dark theme for the application."""
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        QApplication.instance().setPalette(dark_palette)
        QApplication.instance().setStyleSheet("""
            QToolTip { 
                color: #ffffff; 
                background-color: #2a82da; 
                border: 1px solid white; 
            }
            QWidget {
                background-color: #353535;
                color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #353535;
                width: 14px;
                margin: 15px 0 15px 0;
            }
            QScrollBar::handle:vertical {
                background: #5c5c5c;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    # -------------------- Event Handlers --------------------

    def position_toggle_button(self):
        """Position the toggle button based on the left panel visibility."""
        button_x = self.left_panel.width() if self.left_panel.isVisible() else 0
        button_y = 0
        self.toggle_button.move(button_x, button_y)

    def toggle_left_panel(self):
        """Toggle the visibility of the left panel."""
        self.left_panel.setVisible(not self.left_panel.isVisible())
        self.toggle_button.setIcon(QIcon("list.png"))
        self.position_toggle_button()

    def zoom(self, event):
        """Handle zoom events on the plot."""
        if event.inaxes:
            ax = event.inaxes
            scale_factor = 1.1 if event.button == 'up' else 1/1.1
            ax.set_xlim([ax.get_xlim()[0]*scale_factor, ax.get_xlim()[1]*scale_factor])
            ax.set_ylim([ax.get_ylim()[0]*scale_factor, ax.get_ylim()[1]*scale_factor])
            self.canvas.draw()

    def on_press(self, event):
        """Handle mouse press events on the plot."""
        if event.inaxes != self.figure.axes[0]:
            return
        self.cur_xlim = self.figure.axes[0].get_xlim()
        self.cur_ylim = self.figure.axes[0].get_ylim()
        self.press = self.x0, self.y0, event.xdata, event.ydata
        self.x0, self.y0, self.xpress, self.ypress = self.press

    def on_release(self, event):
        """Handle mouse release events on the plot."""
        self.press = None
        self.figure.axes[0].figure.canvas.draw()

    def on_motion(self, event):
        """Handle mouse motion events on the plot."""
        if self.press is None or event.inaxes != self.figure.axes[0]:
            return
        dx = event.xdata - self.xpress
        dy = event.ydata - self.ypress
        self.cur_xlim -= dx
        self.cur_ylim -= dy
        self.figure.axes[0].set_xlim(self.cur_xlim)
        self.figure.axes[0].set_ylim(self.cur_ylim)
        self.figure.axes[0].figure.canvas.draw()

    def resizeEvent(self, event):
        """Handle resize events for the main window."""
        super().resizeEvent(event)
        self.position_toggle_button()

    # -------------------- Functionality --------------------

    def add_function_input(self):
        """Add a new function input widget to the left panel."""
        function_input = FunctionInput()
        self.function_inputs_layout.insertWidget(0, function_input)

    def validate_input(self, function_input):
        """Validate the input from a function input widget."""
        func_str = function_input.function_input.text().strip()
        x_min_str = function_input.x_min_input.text().strip()
        x_max_str = function_input.x_max_input.text().strip()

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

    def plot_functions(self):
        """Plot the functions based on the input."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.set_facecolor('#353535')
        self.figure.patch.set_facecolor('#353535')
        
        # Add grid lines
        ax.grid(True, color='#555555', linestyle='--', linewidth=0.5)
        
        valid_plots = 0

        for i, function_input in enumerate(self.function_inputs_widget.findChildren(FunctionInput)):
            try:
                func_str, x_min, x_max = self.validate_input(function_input)
                x, y = parse_and_evaluate(func_str, x_min, x_max)
                if np.any(np.isnan(y)) or np.any(np.isinf(y)):
                    raise ValueError("Function produces invalid values")
                color = f"#{random.randint(0x808080, 0xFFFFFF):06x}"
                ax.plot(x, y, label=f"f{i+1}(x) = {func_str}", color=color)
                valid_plots += 1
            except ValueError as e:
                QMessageBox.warning(self, "Input Error", str(e))

        if valid_plots > 0:
            ax.set_xlabel('x', color='white')
            ax.set_ylabel('y', color='white')
            ax.set_title('Function Plotter', color='white')
            ax.legend(facecolor='#353535', edgecolor='#353535', labelcolor='white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
            
            # Ensure grid is on top of axis lines but below plots
            ax.set_axisbelow(True)
            
            self.canvas.draw()
        else:
            self.figure.clear()

    def save_plot(self):
        """Save the current plot as an image file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "", "PNG Files (*.png);;All Files (*)"
        )
        if file_path:
            self.figure.savefig(file_path)
            QMessageBox.information(self, "Save Successful", f"Plot saved to {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    plotter = FunctionPlotter()
    plotter.show()
    sys.exit(app.exec_())