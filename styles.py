# Color scheme and styles for the application
class Colors:
    PRIMARY = "#2D2D2D"
    SECONDARY = "#535353"
    ACCENT = "#4DACFF"
    BACKGROUND = "#F0F0F0"
    ACTIVE = "#FF6B6B"
    GRID = "#CCCCCC"

class StyleSheet:
    MAIN_WINDOW = """
        QMainWindow {
            background-color: """ + Colors.BACKGROUND + """;
        }
    """
    
    TOOLBAR = """
        QToolBar {
            background-color: """ + Colors.PRIMARY + """;
            border: none;
            spacing: 5px;
            padding: 5px;
        }
        QToolButton {
            background-color: """ + Colors.SECONDARY + """;
            border: none;
            border-radius: 4px;
            padding: 5px;
            color: white;
        }
        QToolButton:hover {
            background-color: """ + Colors.ACCENT + """;
        }
        QToolButton:checked {
            background-color: """ + Colors.ACTIVE + """;
        }
    """
