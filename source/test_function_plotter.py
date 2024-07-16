import pytest
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt
from main import FunctionPlotter, safe_eval, parse_and_evaluate
import numpy as np

@pytest.fixture
def app(qtbot):
    test_app = FunctionPlotter()
    qtbot.addWidget(test_app)
    return test_app

def test_safe_eval():
    assert safe_eval("2*x + 1", 2) == 5
    assert safe_eval("sin(x)", np.pi/2) == 1
    assert safe_eval("log10(x)", 100) == 2
    
    with pytest.raises(ValueError):
        safe_eval("invalid_function(x)", 1)

def test_parse_and_evaluate():
    x, y = parse_and_evaluate("x^2", -1, 1)
    assert len(x) == 1000
    assert np.allclose(y, x**2)

def test_input_validation(app, qtbot):
    # Test empty inputs
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert "Please enter a function" in [b.text() for b in app.findChildren(QMessageBox)]

    # Test invalid x_min and x_max
    app.function_input.setText("x^2")
    app.x_min_input.setText("invalid")
    app.x_max_input.setText("10")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert "Invalid x_min or x_max value" in [b.text() for b in app.findChildren(QMessageBox)]

    # Test x_min >= x_max
    app.x_min_input.setText("10")
    app.x_max_input.setText("5")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert "x_min must be less than x_max" in [b.text() for b in app.findChildren(QMessageBox)]

def test_function_plotting(app, qtbot):
    app.function_input.setText("x^2")
    app.x_min_input.setText("-5")
    app.x_max_input.setText("5")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    
    assert app.figure.axes[0].get_title() == "Plot of f(x) = x^2"
    assert app.figure.axes[0].get_xlabel() == "x"
    assert app.figure.axes[0].get_ylabel() == "f(x)"

def test_error_handling(app, qtbot):
    app.function_input.setText("1/x")
    app.x_min_input.setText("-1")
    app.x_max_input.setText("1")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    
    assert "The function produces invalid values" in [b.text() for b in app.findChildren(QMessageBox)]

def test_end_to_end(app, qtbot):
    # Simulate user entering a function and range
    app.function_input.setText("sin(x)")
    app.x_min_input.setText("0")
    app.x_max_input.setText("2*pi")
    
    # Simulate clicking the plot button
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    
    # Check if the plot was created
    assert len(app.figure.axes) == 1
    assert app.figure.axes[0].get_title() == "Plot of f(x) = sin(x)"
    
    # Check the plotted data
    line = app.figure.axes[0].get_lines()[0]
    x_data, y_data = line.get_data()
    assert len(x_data) == 1000
    assert np.allclose(y_data, np.sin(x_data))