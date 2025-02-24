import math
import numpy as np

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