"""
Lab 4 - Analiza obiektów binarnych
Wykorzystanie gotowych funkcji OpenCV
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple


class ObjectAnalysis:
    """Analiza obiektów binarnych używając OpenCV"""
    
    @staticmethod
    def analyze_objects(binary_image: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Analizuje wszystkie obiekty na obrazie binarnym.
        
        Args:
            binary_image: Obraz binarny (0/255)
            
        Returns:
            Tuple (objects_data, preview_colored):
            - objects_data: Lista słowników z danymi dla każdego obiektu
            - preview_colored: Kolorowy obraz z konturami
        """
        # Normalizuj do 0/255
        if binary_image.max() == 1:
            binary_image = binary_image * 255
        binary_image = binary_image.astype(np.uint8)
        
        # Znajdź kontury
        contours, hierarchy = cv2.findContours(
            binary_image, 
            cv2.RETR_LIST,  # wszystkie kontury bez hierarchii
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Przygotuj kolorowy obraz do rysowania
        preview = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        
        objects_data = []
        
        for idx, cnt in enumerate(contours):
            # Pomiń bardzo małe obiekty (szum)
            area = cv2.contourArea(cnt)
            if area < 10:
                continue
            
            # 1. Momenty (M1, M2, M3)
            M = cv2.moments(cnt)
            
            # 2. Pole i obwód
            perimeter = cv2.arcLength(cnt, closed=True)
            
            # 3. Solidity
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # 4. Equivalent Diameter
            equivalent_diameter = np.sqrt(4 * area / np.pi) if area > 0 else 0
            
            # Centroid
            cx = int(M['m10'] / M['m00']) if M['m00'] != 0 else 0
            cy = int(M['m01'] / M['m00']) if M['m00'] != 0 else 0
            
            # Zapisz dane
            obj_data = {
                'id': idx + 1,
                'area': area,
                'perimeter': perimeter,
                'centroid': (cx, cy),
                'solidity': solidity,
                'equivalent_diameter': equivalent_diameter,
                # Momenty - tylko M1, M2, M3
                'm00': M['m00'],  # M0
                'm10': M['m10'],  # M1
                'm01': M['m01'],  # M1
                'm20': M['m20'],  # M2
                'm11': M['m11'],  # M2
                'm02': M['m02'],  # M2
                'm30': M['m30'],  # M3
                'm21': M['m21'],  # M3
                'm12': M['m12'],  # M3
                'm03': M['m03'],  # M3
            }
            
            objects_data.append(obj_data)
            
            # Rysuj kontur (każdy innym kolorem)
            color = ObjectAnalysis._get_color(idx)
            cv2.drawContours(preview, [cnt], 0, color, 2)
            
            # Rysuj centroid
            cv2.circle(preview, (cx, cy), 3, (0, 0, 255), -1)
            
            # Podpisz numer
            cv2.putText(preview, str(idx + 1), (cx + 5, cy - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return objects_data, preview
    
    @staticmethod
    def _get_color(idx: int) -> Tuple[int, int, int]:
        """Generuje kolor dla indeksu obiektu"""
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 0), (0, 128, 0), (0, 0, 128),
            (128, 128, 0), (128, 0, 128), (0, 128, 128),
        ]
        return colors[idx % len(colors)]
    
    @staticmethod
    def save_to_csv(objects_data: List[Dict], filename: str):
        """
        Zapisuje dane do pliku CSV.
        
        Args:
            objects_data: Lista słowników z danymi
            filename: Nazwa pliku wyjściowego
        """
        if not objects_data:
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Nagłówek
            headers = [
                'ID', 'Pole', 'Obwód', 'Centroid_X', 'Centroid_Y',
                'Solidity', 'EquivalentDiameter',
                'm00', 'm10', 'm01',  # M0, M1
                'm20', 'm11', 'm02',  # M2
                'm30', 'm21', 'm12', 'm03'  # M3
            ]
            f.write('\t'.join(headers) + '\n')
            
            # Dane
            for obj in objects_data:
                row = [
                    str(obj['id']),
                    f"{obj['area']:.2f}",
                    f"{obj['perimeter']:.2f}",
                    str(obj['centroid'][0]),
                    str(obj['centroid'][1]),
                    f"{obj['solidity']:.4f}",
                    f"{obj['equivalent_diameter']:.2f}",
                    f"{obj['m00']:.2f}",
                    f"{obj['m10']:.2f}",
                    f"{obj['m01']:.2f}",
                    f"{obj['m20']:.2f}",
                    f"{obj['m11']:.2f}",
                    f"{obj['m02']:.2f}",
                    f"{obj['m30']:.2f}",
                    f"{obj['m21']:.2f}",
                    f"{obj['m12']:.2f}",
                    f"{obj['m03']:.2f}",
                ]
                f.write('\t'.join(row) + '\n')