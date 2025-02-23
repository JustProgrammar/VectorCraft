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

def generate_svg_path(points):
    """Generate SVG path command from control points."""
    if len(points) < 2:
        return ""
    
    path = f"M {points[0][0]:.1f},{points[0][1]:.1f} "
    
    for i in range(1, len(points)-2, 3):
        path += (f"C {points[i][0]:.1f},{points[i][1]:.1f} "
                f"{points[i+1][0]:.1f},{points[i+1][1]:.1f} "
                f"{points[i+2][0]:.1f},{points[i+2][1]:.1f} ")
    
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
