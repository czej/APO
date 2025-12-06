from backend.PointOperations import PointOperations
from backend.Histogram import HistogramManager
from backend.LogicalOperations import LogicalOperations 
from backend.MaskOperations import MaskOperations
from backend.ArithmeticOperations import ArithmeticOperations
from backend.ConvolutionOperations import ConvolutionOperations

class AppManager:
    @staticmethod
    def calculate_histograms(img):
        """
        Oblicza histogramy pikseli obrazu.

        Parametr:
            img: obraz w formacie numpy.ndarray (mono lub BGR)

        Zwraca:
            lista histogramów (każdy to numpy.ndarray 256-elementowy)
            - 1 element w liście dla obrazu mono
            - 3 elementy dla obrazu kolorowego (B, G, R)
        """        
        return HistogramManager.calculate_histograms(img)
    
    @staticmethod
    def apply_negate(img):
        return PointOperations.negate(img)
    
    @staticmethod
    def apply_posterize(img, levels):
        return PointOperations.posterize(img, levels)
    
    @staticmethod
    def apply_threshold_binary(img, threshold):
        return PointOperations.threshold_binary(img, threshold)
    
    @staticmethod
    def apply_threshold_with_levels(img, threshold):
        return PointOperations.threshold_with_levels(img, threshold)
    
    @staticmethod
    def apply_stretch_histogram(img, saturation_percent=0):
        return HistogramManager.stretch_histogram(img, saturation_percent)

    @staticmethod
    def apply_equalize_histogram(img):
        return HistogramManager.equalize_histogram(img)
    
    # === LOGICAL OPERATIONS (LAB 2) ===  

    @staticmethod
    def apply_logical_not(img):
        """Operacja logiczna NOT"""
        return LogicalOperations.logical_not(img)
    
    @staticmethod
    def apply_logical_and(img1, img2):
        """Operacja logiczna AND"""
        return LogicalOperations.logical_and(img1, img2)
    
    @staticmethod
    def apply_logical_or(img1, img2):
        """Operacja logiczna OR"""
        return LogicalOperations.logical_or(img1, img2)
    
    @staticmethod
    def apply_logical_xor(img1, img2):
        """Operacja logiczna XOR"""
        return LogicalOperations.logical_xor(img1, img2)
    
    # === MASK CONVERSIONS (LAB 2) ===
    
    @staticmethod
    def convert_to_8bit_mask(img):
        """Konwertuje maskę binarną (0/1) na maskę 8-bitową (0/255)"""
        return MaskOperations.to_8bit_mask(img)
    
    @staticmethod
    def convert_to_binary_mask(img):
        """Konwertuje maskę 8-bitową (0/255) na maskę binarną (0/1)"""
        return MaskOperations.to_binary_mask(img)
    
    # === ARITHMETIC OPERATIONS (LAB 2) ===

    @staticmethod
    def apply_add_images(images, saturation=True):
        """Dodawanie obrazów (2-5)"""
        return ArithmeticOperations.add_images(images, saturation)
    
    @staticmethod
    def apply_absolute_difference(img1, img2):
        """Różnica bezwzględna obrazów"""
        return ArithmeticOperations.absolute_difference(img1, img2)
    
    @staticmethod
    def apply_add_scalar(img, scalar, saturation=True):
        """Dodawanie liczby do obrazu"""
        return ArithmeticOperations.add_scalar(img, scalar, saturation)
    
    @staticmethod
    def apply_multiply_scalar(img, scalar, saturation=True):
        """Mnożenie obrazu przez liczbę"""
        return ArithmeticOperations.multiply_scalar(img, scalar, saturation)
    
    @staticmethod
    def apply_divide_scalar(img, scalar):
        """Dzielenie obrazu przez liczbę"""
        return ArithmeticOperations.divide_scalar(img, scalar)

    # === CONVOLUTION OPERATIONS (LAB 2 - ZADANIE 3) ===
    
    @staticmethod
    def apply_smoothing(img, mask_name, border_type="BORDER_REFLECT", border_value=0):
        """Wygładzanie liniowe"""
        conv_ops = ConvolutionOperations()
        return conv_ops.apply_smoothing(img, mask_name, border_type, border_value)
    
    @staticmethod
    def apply_sharpening(img, mask_name, border_type="BORDER_REFLECT", border_value=0):
        """Wyostrzanie (Laplacjan)"""
        conv_ops = ConvolutionOperations()
        return conv_ops.apply_sharpening(img, mask_name, border_type, border_value)
    
    @staticmethod
    def apply_prewitt(img, direction, border_type="BORDER_REFLECT", border_value=0):
        """Detekcja krawędzi Prewitt"""
        conv_ops = ConvolutionOperations()
        return conv_ops.apply_prewitt(img, direction, border_type, border_value)
    
    @staticmethod
    def apply_sobel(img, border_type="BORDER_REFLECT", border_value=0):
        """Detekcja krawędzi Sobel"""
        conv_ops = ConvolutionOperations()
        return conv_ops.apply_sobel(img, border_type, border_value)
    
    @staticmethod
    def get_smoothing_masks():
        """Lista masek wygładzających"""
        conv_ops = ConvolutionOperations()
        return conv_ops.get_smoothing_mask_names()
    
    @staticmethod
    def apply_custom_mask(img, mask, border_type="BORDER_REFLECT", border_value=0):
        """Własna maska użytkownika"""
        conv_ops = ConvolutionOperations()
        return conv_ops.apply_custom_mask(img, mask, border_type, border_value)
    
    @staticmethod
    def get_laplacian_masks():
        """Lista masek Laplacjana"""
        conv_ops = ConvolutionOperations()
        return conv_ops.get_laplacian_mask_names()
    
    @staticmethod
    def get_prewitt_directions():
        """Lista kierunków Prewitta"""
        conv_ops = ConvolutionOperations()
        return conv_ops.get_prewitt_directions()
    
    @staticmethod
    def get_border_types():
        """Lista typów brzegów"""
        conv_ops = ConvolutionOperations()
        return conv_ops.get_border_types()
    
