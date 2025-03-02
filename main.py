import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar,
                          QToolButton, QVBoxLayout, QWidget, QDialog,
                          QTextEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from canvas import Canvas
from path_manager import PathManager
from tools import ToolState, ToolMode
from styles import StyleSheet

class SVGDialog(QDialog):
    def __init__(self, svg_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SVG Path Commands")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # Text area for SVG content
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(svg_content)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Drawing App")
        self.setStyleSheet(StyleSheet.MAIN_WINDOW)

        # Initialize managers and states
        self.path_manager = PathManager()
        self.tool_state = ToolState()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create toolbar
        self.create_toolbar()

        # Create canvas
        self.canvas = Canvas(self.path_manager, self.tool_state)
        layout.addWidget(self.canvas)

        # Set window properties
        self.setMinimumSize(800, 600)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setStyleSheet(StyleSheet.TOOLBAR)
        self.addToolBar(toolbar)

        # Pen tool button
        pen_button = QToolButton()
        pen_button.setText("Pen")
        pen_button.setCheckable(True)
        pen_button.setChecked(True)
        pen_button.clicked.connect(lambda: self.set_tool_mode(ToolMode.PEN))
        toolbar.addWidget(pen_button)

        # Direct select tool button
        direct_select_button = QToolButton()
        direct_select_button.setText("Direct")
        direct_select_button.setCheckable(True)
        direct_select_button.clicked.connect(
            lambda: self.set_tool_mode(ToolMode.DIRECT_SELECT)
        )
        toolbar.addWidget(direct_select_button)

        # Freeform tool button
        freeform_button = QToolButton()
        freeform_button.setText("Freeform")
        freeform_button.setCheckable(True)
        freeform_button.clicked.connect(
            lambda: self.set_tool_mode(ToolMode.FREEFORM)
        )
        toolbar.addWidget(freeform_button)

        # Add snap point tool button
        add_snap_button = QToolButton()
        add_snap_button.setText("Add Snap")
        add_snap_button.setCheckable(True)
        add_snap_button.clicked.connect(
            lambda: self.set_tool_mode(ToolMode.ADD_SNAP_POINT)
        )
        toolbar.addWidget(add_snap_button)

        # Toggle snap radius visibility button
        toggle_snap_radius_button = QToolButton()
        toggle_snap_radius_button.setText("Show Radius")
        toggle_snap_radius_button.setCheckable(True)
        toggle_snap_radius_button.setChecked(True)
        toggle_snap_radius_button.clicked.connect(self.toggle_snap_radius)
        toolbar.addWidget(toggle_snap_radius_button)

        # Close path button
        close_path_button = QToolButton()
        close_path_button.setText("Close")
        close_path_button.clicked.connect(self.close_current_path)
        toolbar.addWidget(close_path_button)

        # Export SVG button
        export_svg_button = QToolButton()
        export_svg_button.setText("Export SVG")
        export_svg_button.clicked.connect(self.show_svg_export)
        toolbar.addWidget(export_svg_button)

    def set_tool_mode(self, mode):
        self.tool_state.set_mode(mode)
        self.canvas.update()

    def close_current_path(self):
        if self.path_manager.current_path:
            self.path_manager.current_path.close_path()
            self.path_manager.current_path = None
            self.canvas.update()

    def show_svg_export(self):
        svg_content = self.path_manager.export_svg()
        dialog = SVGDialog(svg_content, self)
        dialog.exec()

    def toggle_snap_radius(self):
        self.tool_state.toggle_snap_radius_visibility()
        self.canvas.update()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()