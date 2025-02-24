import math
import numpy as np
import re

def calculate_bezier_point(t, p0, p1, p2, p3):
    """Calculate point on cubic bezier curve at parameter t."""
    return (
        (1-t)**3 * p0 +
        3*(1-t)**2 * t * p1 +
        3*(1-t) * t**2 * p2 +
        t**3 * p3
    )

def generate_svg_path(points, canvas_height=600):
    """Generate SVG path command from control points."""
    if len(points) < 2:
        return ""

    # Transform function to flip y coordinates
    def transform_point(point):
        return (point[0], canvas_height - point[1])

    # Transform the first point
    first_point = transform_point(points[0])
    path = f"M {first_point[0]:.1f},{first_point[1]:.1f} "

    for i in range(1, len(points)-2, 3):
        # Transform control points and end point
        c1 = transform_point(points[i])
        c2 = transform_point(points[i+1])
        end = transform_point(points[i+2])

        path += (f"C {c1[0]:.1f},{c1[1]:.1f} "
                f"{c2[0]:.1f},{c2[1]:.1f} "
                f"{end[0]:.1f},{end[1]:.1f} ")

    return path

def distance(p1, p2):
    """Calculate distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def normalize_vector(vector):
    """Normalize a vector to unit length."""
    length = np.linalg.norm(vector)
    if length == 0:
        return vector
    return vector / length

class PathParser:
    """Parse glyph path commands and convert them to PathPoints."""

    def __init__(self):
        self.current_pos = np.array([0.0, 0.0])
        self.start_pos = None
        self.last_control = None

    def parse_number_sequence(self, params):
        """Parse a sequence of numbers from a string."""
        numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', params)
        return [float(n) for n in numbers]

    def parse_path(self, path_data):
        """Parse path data string and return list of points."""
        commands = re.findall(r'([A-Za-z])([^A-Za-z]*)', path_data)
        points = []
        current_point = None

        for cmd, params in commands:
            numbers = self.parse_number_sequence(params)

            if cmd == 'M':  # Move to
                self.current_pos = np.array([numbers[0], numbers[1]])
                self.start_pos = self.current_pos.copy()
                points.append((self.current_pos.copy(), None, None))

            elif cmd == 'm':  # Relative move to
                self.current_pos += np.array([numbers[0], numbers[1]])
                self.start_pos = self.current_pos.copy()
                points.append((self.current_pos.copy(), None, None))

            elif cmd in ('L', 'l'):  # Line to
                end_pos = (np.array([numbers[0], numbers[1]]) 
                          if cmd == 'L' else self.current_pos + np.array([numbers[0], numbers[1]]))
                handle_out = self.current_pos + (end_pos - self.current_pos) / 3
                handle_in = end_pos - (end_pos - self.current_pos) / 3
                points.append((end_pos, handle_in, handle_out))
                self.current_pos = end_pos

            elif cmd in ('C', 'c'):  # Cubic bezier
                for i in range(0, len(numbers), 6):
                    if cmd == 'c':
                        c1 = self.current_pos + np.array([numbers[i], numbers[i+1]])
                        c2 = self.current_pos + np.array([numbers[i+2], numbers[i+3]])
                        end = self.current_pos + np.array([numbers[i+4], numbers[i+5]])
                    else:
                        c1 = np.array([numbers[i], numbers[i+1]])
                        c2 = np.array([numbers[i+2], numbers[i+3]])
                        end = np.array([numbers[i+4], numbers[i+5]])

                    points.append((end, c2, c1))
                    self.current_pos = end
                    self.last_control = c2

            elif cmd in ('Z', 'z'):  # Close path
                if self.start_pos is not None:
                    handle_out = self.current_pos + (self.start_pos - self.current_pos) / 3
                    handle_in = self.start_pos - (self.start_pos - self.current_pos) / 3
                    points.append((self.start_pos, handle_in, handle_out))
                    self.current_pos = self.start_pos

        return points