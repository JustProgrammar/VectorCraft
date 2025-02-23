from dataclasses import dataclass
import numpy as np
from utils import calculate_bezier_point, generate_svg_path

@dataclass
class PathPoint:
    position: np.ndarray
    handle_in: np.ndarray = None
    handle_out: np.ndarray = None
    is_smooth: bool = True

class Path:
    def __init__(self):
        self.points = []
        self.is_closed = False
        self.stroke_width = 2
        self.stroke_color = "#000000"
        self.fill = "none"

    def add_point(self, position, handle_in=None, handle_out=None):
        point = PathPoint(
            np.array(position),
            np.array(handle_in) if handle_in is not None else None,
            np.array(handle_out) if handle_out is not None else None
        )
        self.points.append(point)

    def close_path(self):
        if len(self.points) >= 3:
            self.is_closed = True

    def get_bezier_points(self):
        bezier_points = []
        for i in range(len(self.points)):
            current = self.points[i]
            bezier_points.append(current.position)

            if current.handle_out is not None:
                bezier_points.append(current.handle_out)

            next_point = self.points[(i + 1) % len(self.points)]
            if next_point.handle_in is not None:
                bezier_points.append(next_point.handle_in)

            if i == len(self.points) - 1 and not self.is_closed:
                break

        return bezier_points

    def to_svg(self):
        path_data = generate_svg_path(self.get_bezier_points())
        return f'<path d="{path_data}" stroke="{self.stroke_color}" stroke-width="{self.stroke_width}" fill="{self.fill}"/>'

class PathManager:
    def __init__(self):
        self.paths = []
        self.current_path = None

    def start_new_path(self):
        self.current_path = Path()
        self.paths.append(self.current_path)

    def get_current_path(self):
        return self.current_path

    def export_svg(self):
        svg_paths = []
        for path in self.paths:
            svg_paths.append(path.to_svg())

        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">\n'
            f'  {"".join(svg_paths)}\n'
            '</svg>'
        )
        return svg_content