"""
Dialogi dla operacji na obrazach
"""

from .threshold_dialog import ThresholdDialog
from .posterize_dialog import PosterizeDialog
from .stretch_dialog import StretchDialog
from .binary_operation_dialog import BinaryOperationDialog
from .scalar_operation_dialog import ScalarOperationDialog
from .convolution_dialog import SmoothingDialog, SharpeningDialog, PrewittDialog, SobelDialog, CustomMaskDialog

__all__ = [
    'ThresholdDialog',
    'PosterizeDialog',
    'StretchDialog',
    'BinaryOperationDialog',
    'ScalarOperationDialog' 
    'SmoothingDialog',
    'SharpeningDialog',
    'PrewittDialog',
    'SobelDialog',
    'CustomMaskDialog'
]