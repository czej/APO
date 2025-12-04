from backend.PointOperations import PointOperations
from backend.Histogram import HistogramManager

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
