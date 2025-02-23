from enum import Enum
import numpy as np
from utils import distance, normalize_vector

class ToolMode(Enum):
    PEN = "pen"
    DIRECT_SELECT = "direct_select"
    FREEFORM = "freeform"

class DirectSelectTool:
    SELECTION_THRESHOLD = 8

    @staticmethod
    def find_closest_point(pos, path, threshold):
        """Find the closest point or handle within threshold distance."""
        min_dist = float('inf')
        closest = None
        is_handle = False
        is_in_handle = False

        for point in path.points:
            # Check anchor point
            dist = distance(np.array(pos), point.position)
            if dist < min_dist and dist < threshold:
                min_dist = dist
                closest = point
                is_handle = False

            # Check handles
            if point.handle_in is not None:
                dist = distance(np.array(pos), point.handle_in)
                if dist < min_dist and dist < threshold:
                    min_dist = dist
                    closest = point
                    is_handle = True
                    is_in_handle = True

            if point.handle_out is not None:
                dist = distance(np.array(pos), point.handle_out)
                if dist < min_dist and dist < threshold:
                    min_dist = dist
                    closest = point
                    is_handle = True
                    is_in_handle = False

        return closest, is_handle, is_in_handle

class ToolState:
    def __init__(self):
        self.current_mode = ToolMode.PEN
        self.is_drawing = False
        self.selected_point = None
        self.selected_handle = None
        self.hover_point = None
        self.hover_handle = None
        self.is_handle_in = False
        self.last_pos = None

    def set_mode(self, mode):
        self.current_mode = mode
        self.reset_state()

    def reset_state(self):
        self.is_drawing = False
        self.selected_point = None
        self.selected_handle = None
        self.hover_point = None
        self.hover_handle = None
        self.is_handle_in = False
        self.last_pos = None

class PenTool:
    HANDLE_LENGTH = 50
    
    @staticmethod
    def create_point(pos, path):
        if not path.points:
            path.add_point(pos)
            return
            
        last_point = path.points[-1]
        handle_out = last_point.position + normalize_vector(
            np.array(pos) - last_point.position
        ) * PenTool.HANDLE_LENGTH
        
        last_point.handle_out = handle_out
        handle_in = np.array(pos) - normalize_vector(
            np.array(pos) - last_point.position
        ) * PenTool.HANDLE_LENGTH
        
        path.add_point(pos, handle_in=handle_in)
    
    @staticmethod
    def adjust_handle(point, handle_pos, is_in_handle):
        if is_in_handle:
            point.handle_in = np.array(handle_pos)
            if point.is_smooth and point.handle_out is not None:
                diff = point.position - point.handle_in
                point.handle_out = point.position + diff
        else:
            point.handle_out = np.array(handle_pos)
            if point.is_smooth and point.handle_in is not None:
                diff = point.position - point.handle_out
                point.handle_in = point.position + diff