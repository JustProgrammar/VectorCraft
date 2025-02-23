from enum import Enum
import numpy as np
from utils import distance, normalize_vector

class ToolMode(Enum):
    PEN = "pen"
    DIRECT_SELECT = "direct_select"
    FREEFORM = "freeform"

class ToolState:
    def __init__(self):
        self.current_mode = ToolMode.PEN
        self.is_drawing = False
        self.selected_point = None
        self.selected_handle = None
        self.hover_point = None
        self.hover_handle = None
        
    def set_mode(self, mode):
        self.current_mode = mode
        self.reset_state()
        
    def reset_state(self):
        self.is_drawing = False
        self.selected_point = None
        self.selected_handle = None
        self.hover_point = None
        self.hover_handle = None

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
