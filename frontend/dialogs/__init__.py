"""
Dialogi dla operacji na obrazach
"""

from .threshold_dialog import ThresholdDialog
from .posterize_dialog import PosterizeDialog
from .stretch_dialog import StretchDialog
from .binary_operation_dialog import BinaryOperationDialog

__all__ = [
    'ThresholdDialog',
    'PosterizeDialog',
    'StretchDialog',
    'BinaryOperationDialog'
]