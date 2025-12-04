import numpy as np
from collections import namedtuple

Histogram = namedtuple('Histogram', ['histogram', 'mean', 'median', 'std', 'pixels_num', 'min', 'max'])

class HistogramManager:
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
        if len(img.shape) == 2:  # monochromatic
            hists = HistogramManager._calculate_mono_histogram(img)
        elif len(img.shape) == 3 and img.shape[2] == 3:  # color RGB
            hists = HistogramManager._calculate_rgb_histograms(img)
        else:
            raise ValueError("Nieobsługiwany format obrazu")
        
        return HistogramManager._calculate_histogram_stats(hists)
    
    @staticmethod
    def _calculate_histogram_stats(hists):
        stats = []
        for hist in hists:
            values = np.arange(256)
            pixels_num = np.sum(hist)
            mean = np.sum(values * hist) / pixels_num
            median = np.searchsorted(np.cumsum(hist), pixels_num / 2) # np.interp(pixels_num / 2, np.cumsum(hist), values)  # TODO: test
            std = np.sqrt(np.sum(((values - mean) ** 2) * hist) / pixels_num)
            max_value = np.max(hist)
            min_value = np.min(hist)

            stats.append(Histogram(
                histogram=hist,
                mean=mean,
                median=median,
                std=std,
                pixels_num=pixels_num,
                max=max_value,
                min=min_value
            ))
        
        return stats
    
    @staticmethod
    def _calculate_rgb_histograms(img):
        hists = [np.zeros(256, dtype=int) for _ in range(3)]
        for row in img:
            for pixel in row:
                b, g, r = pixel
                hists[0][b] += 1
                hists[1][g] += 1
                hists[2][r] += 1
        return hists
    
    @staticmethod
    def _calculate_mono_histogram(img):
        hist = np.zeros(256, dtype=int)
        for pixel in img.flat:
            hist[pixel] += 1
        return [hist]
    
    # @staticmethod
    # def stretch_histogram(img, saturation_percent=0):
    #     """
    #     Liniowe rozciąganie histogramu.
        
    #     Parametry:
    #         img: obraz numpy.ndarray (grayscale)
    #         saturation_percent: procent pikseli do przesycenia (0-5)
        
    #     Zwraca:
    #         obraz z rozciągniętym histogramem
    #     """
    #     if len(img.shape) != 2:
    #         raise ValueError("Obraz musi być w odcieniach szarości")
        
    #     if saturation_percent < 0 or saturation_percent > 5:
    #         raise ValueError("Przesycenie musi być w zakresie 0-5%")
        
    #     # Bez przesycenia
    #     if saturation_percent == 0:
    #         min_val = np.min(img)
    #         max_val = np.max(img)
    #     else:
    #         # Z przesyceniem - oblicz percentyle
    #         lower_percentile = saturation_percent / 2
    #         upper_percentile = 100 - (saturation_percent / 2)
            
    #         min_val = np.percentile(img, lower_percentile)
    #         max_val = np.percentile(img, upper_percentile)
        
    #     # Unikaj dzielenia przez zero
    #     if max_val == min_val:
    #         return img.copy()
        
    #     # Rozciągnij histogram
    #     result = ((img - min_val) / (max_val - min_val) * 255)
    #     result = np.clip(result, 0, 255).astype(np.uint8)
        
    #     return result

    @staticmethod
    def stretch_histogram(img, saturation_percent=0):
        """
        Liniowe rozciąganie histogramu według algorytmu z wykładu.
        
        Parametry:
            img: obraz numpy.ndarray (grayscale)
            saturation_percent: procent pikseli do przesycenia (0-5)
        
        Zwraca:
            obraz z rozciągniętym histogramem
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        if saturation_percent < 0 or saturation_percent > 5:
            raise ValueError("Przesycenie musi być w zakresie 0-5%")
        
        # Oblicz histogram
        hist = np.zeros(256, dtype=int)
        for pixel in img.flat:
            hist[pixel] += 1
        
        # Znajdź Lmin i Lmax
        Lmin = 0
        Lmax = 255
        sem_min = False
        sem_max = False
        
        if saturation_percent > 0:
            # Z przesyceniem - szukaj Lmin
            total_pixels = img.shape[0] * img.shape[1]
            threshold_pixels = int((saturation_percent / 2 / 100) * total_pixels)
            
            accumulated = 0
            for z in range(256):
                if not sem_min:
                    if hist[z] != 0:
                        sem_min = True
                        Lmin = z
                accumulated += hist[z]
                if accumulated >= threshold_pixels and hist[z] != 0:
                    Lmin = z
                    break
            
            # Szukaj Lmax
            accumulated = 0
            for z in range(255, -1, -1):
                if not sem_max:
                    if hist[z] != 0:
                        sem_max = True
                        Lmax = z
                accumulated += hist[z]
                if accumulated >= threshold_pixels and hist[z] != 0:
                    Lmax = z
                    break
        else:
            # Bez przesycenia - znajdź pierwsze i ostatnie niezerowe
            for z in range(256):
                if hist[z] != 0:
                    Lmin = z
                    break
            
            for z in range(255, -1, -1):
                if hist[z] != 0:
                    Lmax = z
                    break
        
        print(f"Lmin: {Lmin}, Lmax: {Lmax}")
        
        # Unikaj dzielenia przez zero
        if Lmax == Lmin:
            return img.copy()
        
        # Tablica LUT dla transformacji
        lut = np.zeros(256, dtype=np.uint8)
        for z in range(256):
            if z < Lmin:
                lut[z] = 0
            elif z > Lmax:
                lut[z] = 255
            else:
                # Wzór: ((p(i,j) - Lmin) * Lmax_output) / (Lmax - Lmin)
                lut[z] = int(((z - Lmin) * 255) / (Lmax - Lmin))
        
        # Zastosuj transformację
        result = lut[img]
        
        return result

    @staticmethod
    def equalize_histogram(img):
        """
        Wyrównywanie histogramu (equalizacja).
        Implementacja algorytmu z wykładu.
        
        Parametr:
            img: obraz numpy.ndarray (grayscale)
        
        Zwraca:
            obraz z wyrównanym histogramem
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        # Oblicz histogram
        hist = np.zeros(256, dtype=int)
        for pixel in img.flat:
            hist[pixel] += 1
        
        # Oblicz histogram skumulowany (CDF - Cumulative Distribution Function)
        cdf = np.cumsum(hist)
        
        # Normalizuj CDF do zakresu 0-255
        # Pomijamy pierwszą niezerową wartość CDF dla lepszego kontrastu
        cdf_min = cdf[cdf > 0].min()
        total_pixels = img.shape[0] * img.shape[1]
        
        # Tablica LUT (Look-Up Table) dla transformacji
        lut = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            if cdf[i] > 0:
                lut[i] = np.round(((cdf[i] - cdf_min) / (total_pixels - cdf_min)) * 255)
            else:
                lut[i] = 0
        
        # Zastosuj transformację
        result = lut[img]
        
        return result