"""
Lab 4 - Zadanie 1: Analiza składowych wektora cech obiektu binarnego
Implementacja: momenty, pole, obwód, współczynniki kształtu
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple


class FeatureAnalysis:
    """Klasa do analizy cech obiektów binarnych"""
    
    @staticmethod
    def compute_moments(binary_image: np.ndarray) -> Dict[str, Dict[str, float]]:
        """
        Oblicza momenty obrazu binarnego.
        
        Args:
            binary_image: Obraz binarny (0/255 lub 0/1)
            
        Returns:
            Słownik z momentami: raw (m), centralne (mu), znormalizowane (nu)
        """
        # Upewnij się że obraz jest binarny
        if binary_image.max() == 1:
            binary_image = binary_image * 255
        
        # Oblicz momenty używając OpenCV
        moments = cv2.moments(binary_image)
        
        return {
            'raw': {
                'm00': moments['m00'],
                'm10': moments['m10'],
                'm01': moments['m01'],
                'm20': moments['m20'],
                'm11': moments['m11'],
                'm02': moments['m02'],
                'm30': moments['m30'],
                'm21': moments['m21'],
                'm12': moments['m12'],
                'm03': moments['m03']
            },
            'central': {
                'mu20': moments['mu20'],
                'mu11': moments['mu11'],
                'mu02': moments['mu02'],
                'mu30': moments['mu30'],
                'mu21': moments['mu21'],
                'mu12': moments['mu12'],
                'mu03': moments['mu03']
            },
            'normalized': {
                'nu20': moments['nu20'],
                'nu11': moments['nu11'],
                'nu02': moments['nu02'],
                'nu30': moments['nu30'],
                'nu21': moments['nu21'],
                'nu12': moments['nu12'],
                'nu03': moments['nu03']
            }
        }
    
    @staticmethod
    def compute_area_perimeter(binary_image: np.ndarray) -> Tuple[float, float]:
        """
        Oblicza pole powierzchni i obwód obiektu.
        
        Args:
            binary_image: Obraz binarny
            
        Returns:
            Tuple (area, perimeter)
        """
        # Upewnij się że obraz jest binarny
        if binary_image.max() == 1:
            binary_image = binary_image * 255
        
        # Znajdź kontury
        contours, _ = cv2.findContours(binary_image.astype(np.uint8), 
                                       cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_NONE)
        
        if len(contours) == 0:
            return 0.0, 0.0
        
        # Dla największego konturu (głównego obiektu)
        largest_contour = max(contours, key=cv2.contourArea)
        
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, closed=True)
        
        return area, perimeter
    
    @staticmethod
    def compute_shape_coefficients(binary_image: np.ndarray) -> Dict[str, float]:
        """
        Oblicza współczynniki kształtu dla obiektu binarnego.
        
        Args:
            binary_image: Obraz binarny
            
        Returns:
            Słownik ze współczynnikami: aspectRatio, extent, solidity, equivalentDiameter
        """
        # Upewnij się że obraz jest binarny
        if binary_image.max() == 1:
            binary_image = binary_image * 255
        
        # Znajdź kontury
        contours, _ = cv2.findContours(binary_image.astype(np.uint8), 
                                       cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return {
                'aspectRatio': 0.0,
                'extent': 0.0,
                'solidity': 0.0,
                'equivalentDiameter': 0.0
            }
        
        # Największy kontur
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        
        # 1. Aspect Ratio - stosunek szerokości do wysokości
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h if h != 0 else 0.0
        
        # 2. Extent - stosunek pola obiektu do pola prostokąta otaczającego
        rect_area = w * h
        extent = float(area) / rect_area if rect_area != 0 else 0.0
        
        # 3. Solidity - stosunek pola obiektu do pola jego wypukłej otoczki
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area != 0 else 0.0
        
        # 4. Equivalent Diameter - średnica koła o tym samym polu
        equivalent_diameter = np.sqrt(4 * area / np.pi) if area > 0 else 0.0
        
        return {
            'aspectRatio': aspect_ratio,
            'extent': extent,
            'solidity': solidity,
            'equivalentDiameter': equivalent_diameter
        }
    
    @staticmethod
    def analyze_binary_object(binary_image: np.ndarray) -> Dict:
        """
        Kompletna analiza obiektu binarnego.
        Zwraca wszystkie wymagane cechy.
        
        Args:
            binary_image: Obraz binarny
            
        Returns:
            Słownik ze wszystkimi cechami
        """
        moments = FeatureAnalysis.compute_moments(binary_image)
        area, perimeter = FeatureAnalysis.compute_area_perimeter(binary_image)
        shape_coeffs = FeatureAnalysis.compute_shape_coefficients(binary_image)
        
        # Środek masy (centroid) z momentów
        m00 = moments['raw']['m00']
        cx = moments['raw']['m10'] / m00 if m00 != 0 else 0
        cy = moments['raw']['m01'] / m00 if m00 != 0 else 0
        
        return {
            'moments': moments,
            'area': area,
            'perimeter': perimeter,
            'centroid': {'x': cx, 'y': cy},
            'shape_coefficients': shape_coeffs
        }
    
    @staticmethod
    def save_features_to_file(features: Dict, filename: str = "features.txt"):
        """
        Zapisuje cechy do pliku tekstowego w formacie zgodnym z Excel.
        
        Args:
            features: Słownik z cechami z analyze_binary_object
            filename: Nazwa pliku wyjściowego
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Analiza cech obiektu binarnego - Lab 4 Zadanie 1\n")
            f.write("# Format: CSV (separator: tabulacja)\n\n")
            
            # Nagłówek dla Excel
            f.write("Cecha\tWartość\n")
            
            # Pole i obwód
            f.write(f"Pole powierzchni\t{features['area']:.4f}\n")
            f.write(f"Obwód\t{features['perimeter']:.4f}\n")
            
            # Centroid
            f.write(f"Centroid X\t{features['centroid']['x']:.4f}\n")
            f.write(f"Centroid Y\t{features['centroid']['y']:.4f}\n")
            
            # Współczynniki kształtu
            f.write(f"\nWspółczynniki kształtu:\n")
            f.write(f"Aspect Ratio\t{features['shape_coefficients']['aspectRatio']:.4f}\n")
            f.write(f"Extent\t{features['shape_coefficients']['extent']:.4f}\n")
            f.write(f"Solidity\t{features['shape_coefficients']['solidity']:.4f}\n")
            f.write(f"Equivalent Diameter\t{features['shape_coefficients']['equivalentDiameter']:.4f}\n")
            
            # Momenty surowe
            f.write(f"\nMomenty surowe (m):\n")
            for key, val in features['moments']['raw'].items():
                f.write(f"{key}\t{val:.4f}\n")
            
            # Momenty centralne
            f.write(f"\nMomenty centralne (mu):\n")
            for key, val in features['moments']['central'].items():
                f.write(f"{key}\t{val:.4f}\n")
            
            # Momenty znormalizowane
            f.write(f"\nMomenty znormalizowane (nu):\n")
            for key, val in features['moments']['normalized'].items():
                f.write(f"{key}\t{val:.4f}\n")
    
    @staticmethod
    def save_features_to_csv(features_list: List[Dict], filename: str = "features.csv"):
        """
        Zapisuje cechy wielu obiektów do pliku CSV.
        
        Args:
            features_list: Lista słowników z cechami
            filename: Nazwa pliku wyjściowego
        """
        if not features_list:
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Nagłówek CSV
            headers = [
                'Object_ID',
                'Area', 'Perimeter', 'Centroid_X', 'Centroid_Y',
                'AspectRatio', 'Extent', 'Solidity', 'EquivalentDiameter',
                'm00', 'm10', 'm01', 'm20', 'm11', 'm02', 'm30', 'm21', 'm12', 'm03',
                'mu20', 'mu11', 'mu02', 'mu30', 'mu21', 'mu12', 'mu03',
                'nu20', 'nu11', 'nu02', 'nu30', 'nu21', 'nu12', 'nu03'
            ]
            f.write('\t'.join(headers) + '\n')
            
            # Dane dla każdego obiektu
            for idx, feat in enumerate(features_list, 1):
                row = [
                    str(idx),
                    f"{feat['area']:.4f}",
                    f"{feat['perimeter']:.4f}",
                    f"{feat['centroid']['x']:.4f}",
                    f"{feat['centroid']['y']:.4f}",
                    f"{feat['shape_coefficients']['aspectRatio']:.4f}",
                    f"{feat['shape_coefficients']['extent']:.4f}",
                    f"{feat['shape_coefficients']['solidity']:.4f}",
                    f"{feat['shape_coefficients']['equivalentDiameter']:.4f}",
                ]
                
                # Dodaj momenty surowe
                for key in ['m00', 'm10', 'm01', 'm20', 'm11', 'm02', 'm30', 'm21', 'm12', 'm03']:
                    row.append(f"{feat['moments']['raw'][key]:.4f}")
                
                # Dodaj momenty centralne
                for key in ['mu20', 'mu11', 'mu02', 'mu30', 'mu21', 'mu12', 'mu03']:
                    row.append(f"{feat['moments']['central'][key]:.4f}")
                
                # Dodaj momenty znormalizowane
                for key in ['nu20', 'nu11', 'nu02', 'nu30', 'nu21', 'nu12', 'nu03']:
                    row.append(f"{feat['moments']['normalized'][key]:.4f}")
                
                f.write('\t'.join(row) + '\n')