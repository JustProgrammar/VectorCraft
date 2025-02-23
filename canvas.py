from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath
import numpy as np
from styles import Colors
from tools import ToolMode

class DirectSelectTool:
    SELECTION_THRESHOLD = 10

    @staticmethod
    def find_closest_point(pos, path, threshold):
        closest_point = None
        min_distance = float('inf')
        is_handle = False
        is_in_handle = False

        for point in path.points:
            dist = distance(pos, point.position)
            if dist < min_distance:
                min_distance = dist
                closest_point = point
                is_handle = False
                is_in_handle = False

            if point.handle_in is not None:
                dist = distance(pos, point.handle_in)
                if dist < min_distance:
                    min_distance = dist
                    closest_point = point
                    is_handle = True
                    is_in_handle = True

            if point.handle_out is not None:
                dist = distance(pos, point.handle_out)
                if dist < min_distance:
                    min_distance = dist
                    closest_point = point
                    is_handle = True
                    is_in_handle = False

        return closest_point, is_handle, is_in_handle

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

class Canvas(QWidget):
    def __init__(self, path_manager, tool_state):
        super().__init__()
        self.path_manager = path_manager
        self.tool_state = tool_state
        self.zoom = 1.0
        self.offset = QPointF(0, 0)
        self.grid_size = 20
        self.last_freeform_pos = None
        self.freeform_distance_threshold = 10
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply zoom and pan
        painter.translate(self.offset)
        painter.scale(self.zoom, self.zoom)

        # Draw grid
        self.draw_grid(painter)

        # Draw snap points and their radii
        if self.tool_state.show_snap_radius:
            self.draw_snap_points(painter)

        # Draw paths
        for path in self.path_manager.paths:
            self.draw_path(painter, path)

        # Draw control points and handles
        if self.path_manager.current_path:
            self.draw_control_points(painter)

        painter.end()

    def draw_snap_points(self, painter):
        for snap_point in self.tool_state.snap_points:
            # Draw snap point
            painter.setPen(QPen(QColor(Colors.ACCENT), 2))
            painter.drawEllipse(QPointF(*snap_point.position), 4, 4)

            # Draw snap radius
            if self.tool_state.show_snap_radius:
                painter.setPen(QPen(QColor(Colors.SECONDARY), 1, Qt.PenStyle.DashLine))
                painter.drawEllipse(
                    QPointF(*snap_point.position),
                    snap_point.radius,
                    snap_point.radius
                )

    def draw_grid(self, painter):
        painter.setPen(QPen(QColor(Colors.GRID), 1))

        # Calculate visible area
        visible_rect = self.rect()
        start_x = int(visible_rect.left() / self.grid_size) * self.grid_size
        end_x = int(visible_rect.right() / self.grid_size + 1) * self.grid_size
        start_y = int(visible_rect.top() / self.grid_size) * self.grid_size
        end_y = int(visible_rect.bottom() / self.grid_size + 1) * self.grid_size

        # Draw vertical lines
        for x in range(start_x, end_x, self.grid_size):
            painter.drawLine(x, start_y, x, end_y)

        # Draw horizontal lines
        for y in range(start_y, end_y, self.grid_size):
            painter.drawLine(start_x, y, end_x, y)

    def draw_path(self, painter, path):
        if not path.points:
            return

        painter_path = QPainterPath()
        bezier_points = path.get_bezier_points()

        if len(bezier_points) < 4:
            return

        painter_path.moveTo(bezier_points[0][0], bezier_points[0][1])

        for i in range(1, len(bezier_points)-2, 3):
            painter_path.cubicTo(
                bezier_points[i][0], bezier_points[i][1],
                bezier_points[i+1][0], bezier_points[i+1][1],
                bezier_points[i+2][0], bezier_points[i+2][1]
            )

        if path.is_closed:
            painter_path.closeSubpath()

        painter.setPen(QPen(QColor(path.stroke_color), path.stroke_width))
        painter.drawPath(painter_path)

    def draw_control_points(self, painter):
        for point in self.path_manager.current_path.points:
            # Draw anchor point
            painter.setPen(QPen(QColor(Colors.ACCENT), 2))
            painter.drawEllipse(QPointF(*point.position), 4, 4)

            # Draw handles
            if point.handle_in is not None:
                painter.setPen(QPen(QColor(Colors.SECONDARY), 1))
                painter.drawLine(
                    QPointF(*point.position),
                    QPointF(*point.handle_in)
                )
                painter.drawEllipse(QPointF(*point.handle_in), 3, 3)

            if point.handle_out is not None:
                painter.setPen(QPen(QColor(Colors.SECONDARY), 1))
                painter.drawLine(
                    QPointF(*point.position),
                    QPointF(*point.handle_out)
                )
                painter.drawEllipse(QPointF(*point.handle_out), 3, 3)

    def mousePressEvent(self, event):
        pos = self.transform_pos(event.position())
        current_pos = np.array([pos.x(), pos.y()])

        if self.tool_state.current_mode == ToolMode.ADD_SNAP_POINT:
            self.tool_state.add_snap_point(current_pos)
        elif self.tool_state.current_mode == ToolMode.PEN:
            if not self.path_manager.current_path:
                self.path_manager.start_new_path()
            self.tool_state.is_drawing = True
            snapped_pos = self.tool_state.get_snap_position(current_pos)
            self.path_manager.current_path.add_point(snapped_pos)
        elif self.tool_state.current_mode == ToolMode.DIRECT_SELECT:
            if self.path_manager.current_path:
                point, is_handle, is_in_handle = DirectSelectTool.find_closest_point(
                    current_pos,
                    self.path_manager.current_path,
                    DirectSelectTool.SELECTION_THRESHOLD / self.zoom
                )
                self.tool_state.selected_point = point
                self.tool_state.selected_handle = is_handle
                self.tool_state.is_handle_in = is_in_handle
                self.tool_state.last_pos = current_pos
        elif self.tool_state.current_mode == ToolMode.FREEFORM:
            if not self.path_manager.current_path:
                self.path_manager.start_new_path()
            self.tool_state.is_drawing = True
            self.last_freeform_pos = current_pos
            snapped_pos = self.tool_state.get_snap_position(current_pos)
            self.path_manager.current_path.add_point(snapped_pos)

        self.update()

    def mouseMoveEvent(self, event):
        pos = self.transform_pos(event.position())
        current_pos = np.array([pos.x(), pos.y()])

        if self.tool_state.current_mode == ToolMode.PEN and self.tool_state.is_drawing:
            current_path = self.path_manager.current_path
            if current_path and current_path.points:
                last_point = current_path.points[-1]
                last_point.handle_out = current_pos

        elif self.tool_state.current_mode == ToolMode.DIRECT_SELECT:
            if self.tool_state.selected_point:
                if self.tool_state.selected_handle:
                    # Moving a handle
                    if self.tool_state.is_handle_in:
                        self.tool_state.selected_point.handle_in = current_pos
                        if self.tool_state.selected_point.is_smooth:
                            diff = self.tool_state.selected_point.position - current_pos
                            self.tool_state.selected_point.handle_out = (
                                self.tool_state.selected_point.position + diff
                            )
                    else:
                        self.tool_state.selected_point.handle_out = current_pos
                        if self.tool_state.selected_point.is_smooth:
                            diff = self.tool_state.selected_point.position - current_pos
                            self.tool_state.selected_point.handle_in = (
                                self.tool_state.selected_point.position + diff
                            )
                else:
                    # Moving the anchor point
                    snapped_pos = self.tool_state.get_snap_position(current_pos)
                    delta = snapped_pos - self.tool_state.last_pos
                    self.tool_state.selected_point.position += delta
                    if self.tool_state.selected_point.handle_in is not None:
                        self.tool_state.selected_point.handle_in += delta
                    if self.tool_state.selected_point.handle_out is not None:
                        self.tool_state.selected_point.handle_out += delta
                    self.tool_state.last_pos = snapped_pos

        elif self.tool_state.current_mode == ToolMode.FREEFORM and self.tool_state.is_drawing:
            if self.last_freeform_pos is not None:
                dist = distance(current_pos, self.last_freeform_pos)
                if dist >= self.freeform_distance_threshold:
                    snapped_pos = self.tool_state.get_snap_position(current_pos)
                    self.path_manager.current_path.add_point(snapped_pos)
                    self.last_freeform_pos = current_pos

        self.update()

    def mouseReleaseEvent(self, event):
        if self.tool_state.current_mode == ToolMode.FREEFORM:
            self.last_freeform_pos = None
        self.tool_state.is_drawing = False
        self.tool_state.selected_point = None
        self.tool_state.selected_handle = None
        self.update()

    def wheelEvent(self, event):
        zoom_factor = 1.1
        if event.angleDelta().y() < 0:
            self.zoom /= zoom_factor
        else:
            self.zoom *= zoom_factor
        self.update()

    def transform_pos(self, pos):
        return (pos - self.offset) / self.zoom