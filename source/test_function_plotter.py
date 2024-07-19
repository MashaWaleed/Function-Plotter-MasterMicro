import pytest
from PySide2.QtWidgets import QApplication
from PySide2.QtTest import QTest
from PySide2.QtCore import Qt
from main import FunctionPlotter, FunctionInput, safe_eval, parse_and_evaluate
import numpy as np

@pytest.fixture(scope="session")
def app(qapp):
    return qapp

@pytest.fixture
def window(app, qtbot):
    plotter = FunctionPlotter()
    qtbot.addWidget(plotter)
    return plotter

def test_window_title(window):
    assert window.windowTitle() == "Function Plotter"

def test_initial_state(window):
    assert len(window.function_inputs_widget.findChildren(FunctionInput)) == 0

def test_plot_button_exists(window):
    assert window.plot_button.text() == "Plot"

def test_safe_eval():
    assert safe_eval("x + 1", 2) == 3
    assert np.isclose(safe_eval("sin(x)", np.pi/2), 1)
    with pytest.raises(ValueError):
        safe_eval("1 + exec('print(1)')", 0)

def test_parse_and_evaluate():
    x, y = parse_and_evaluate("x^2", -1, 1)
    assert len(x) == 1000
    assert np.allclose(y, x**2)

def test_plot_valid_function(window, qtbot):
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    function_input = window.function_inputs_widget.findChild(FunctionInput)
    function_input.function_input.setText("x^2")
    function_input.x_min_input.setText("-1")
    function_input.x_max_input.setText("1")
    qtbot.mouseClick(window.plot_button, Qt.LeftButton)
    assert len(window.figure.axes) == 1

def test_plot_invalid_function(window, qtbot):
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    function_input = window.function_inputs_widget.findChild(FunctionInput)
    function_input.function_input.setText("x/")
    function_input.x_min_input.setText("-1")
    function_input.x_max_input.setText("1")
    with qtbot.waitSignal(window.plot_button.clicked, timeout=1000):
        qtbot.mouseClick(window.plot_button, Qt.LeftButton)
    assert len(window.figure.axes) == 0

def test_plot_invalid_range(window, qtbot):
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    function_input = window.function_inputs_widget.findChild(FunctionInput)
    function_input.function_input.setText("x^2")
    function_input.x_min_input.setText("1")
    function_input.x_max_input.setText("-1")
    with qtbot.waitSignal(window.plot_button.clicked, timeout=1000):
        qtbot.mouseClick(window.plot_button, Qt.LeftButton)
    assert len(window.figure.axes) == 0

def test_plot_empty_input(window, qtbot):
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    function_input = window.function_inputs_widget.findChild(FunctionInput)
    function_input.function_input.setText("")
    function_input.x_min_input.setText("")
    function_input.x_max_input.setText("")
    with qtbot.waitSignal(window.plot_button.clicked, timeout=1000):
        qtbot.mouseClick(window.plot_button, Qt.LeftButton)
    assert len(window.figure.axes) == 0

def test_add_function_button_exists(window):
    assert window.add_function_button.text() == "Add Function"

def test_add_function_input(window, qtbot):
    initial_count = len(window.function_inputs_widget.findChildren(FunctionInput))
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    new_count = len(window.function_inputs_widget.findChildren(FunctionInput))
    assert new_count == initial_count + 1

def test_plot_multiple_functions(window, qtbot):
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    qtbot.mouseClick(window.add_function_button, Qt.LeftButton)
    
    function_inputs = window.function_inputs_widget.findChildren(FunctionInput)
    
    function_inputs[0].function_input.setText("x^2")
    function_inputs[0].x_min_input.setText("-1")
    function_inputs[0].x_max_input.setText("1")
    
    function_inputs[1].function_input.setText("sin(x)")
    function_inputs[1].x_min_input.setText("0")
    function_inputs[1].x_max_input.setText("2*pi")
    
    qtbot.mouseClick(window.plot_button, Qt.LeftButton)
    
    assert len(window.figure.axes) == 1
    assert len(window.figure.axes[0].get_lines()) == 2

if __name__ == "__main__":
    pytest.main(["-v", __file__])