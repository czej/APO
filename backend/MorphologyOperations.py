import cv2
import numpy as np


class MorphologyOperations:
    """
    Klasa realizująca operacje morfologii matematycznej na obrazach binarnych
    """
    
    # Elementy strukturalne 3x3
    STRUCTURING_ELEMENTS = {
        'cross': cv2.MORPH_CROSS,
        'rect': cv2.MORPH_RECT,
        'ellipse': cv2.MORPH_ELLIPSE
    }
    
    @staticmethod
    def validate_binary_image(image):
        """
        Sprawdza czy obraz jest binarny
        """
        if image is None:
            raise ValueError("Obraz nie może być None")
        
        if len(image.shape) != 2:
            raise ValueError("Obraz musi być w skali szarości (2D)")
        
        unique_values = np.unique(image)
        if not (len(unique_values) <= 2 and all(v in [0, 1, 255] for v in unique_values)):
            raise ValueError("Obraz musi być binarny (wartości 0 i 1 lub 0 i 255)")
    
    @staticmethod
    def get_structuring_element(shape='rect', size=3):
        """
        Tworzy element strukturalny
        
        Args:
            shape: Kształt elementu ('rect', 'cross', 'ellipse')
            size: Rozmiar elementu (domyślnie 3x3)
            
        Returns:
            Element strukturalny
        """
        if shape not in MorphologyOperations.STRUCTURING_ELEMENTS:
            shape = 'rect'
        
        morph_shape = MorphologyOperations.STRUCTURING_ELEMENTS[shape]
        return cv2.getStructuringElement(morph_shape, (size, size))
    
    @staticmethod
    def erosion(image, element_shape='rect', element_size=3, iterations=1):
        """
        Erozja - operacja morfologiczna zmniejszająca obiekty
        
        Args:
            image: Obraz binarny
            element_shape: Kształt elementu strukturalnego ('rect', 'cross', 'ellipse')
            element_size: Rozmiar elementu strukturalnego
            iterations: Liczba iteracji
            
        Returns:
            Obraz po erozji
        """
        MorphologyOperations.validate_binary_image(image)
        
        # Normalizacja do 0/255
        img_normalized = image.copy()
        if img_normalized.max() == 1:
            img_normalized = img_normalized * 255
        
        kernel = MorphologyOperations.get_structuring_element(element_shape, element_size)
        result = cv2.erode(img_normalized, kernel, iterations=iterations)
        
        # Zwróć w tym samym formacie co wejście
        if image.max() == 1:
            result = (result / 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def dilation(image, element_shape='rect', element_size=3, iterations=1):
        """
        Dylacja - operacja morfologiczna powiększająca obiekty
        
        Args:
            image: Obraz binarny
            element_shape: Kształt elementu strukturalnego ('rect', 'cross', 'ellipse')
            element_size: Rozmiar elementu strukturalnego
            iterations: Liczba iteracji
            
        Returns:
            Obraz po dylacji
        """
        MorphologyOperations.validate_binary_image(image)
        
        # Normalizacja do 0/255
        img_normalized = image.copy()
        if img_normalized.max() == 1:
            img_normalized = img_normalized * 255
        
        kernel = MorphologyOperations.get_structuring_element(element_shape, element_size)
        result = cv2.dilate(img_normalized, kernel, iterations=iterations)
        
        # Zwróć w tym samym formacie co wejście
        if image.max() == 1:
            result = (result / 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def opening(image, element_shape='rect', element_size=3, iterations=1):
        """
        Otwarcie - erozja następnie dylacja
        Usuwa małe obiekty i wygładza kontury
        
        Args:
            image: Obraz binarny
            element_shape: Kształt elementu strukturalnego ('rect', 'cross', 'ellipse')
            element_size: Rozmiar elementu strukturalnego
            iterations: Liczba iteracji
            
        Returns:
            Obraz po otwarciu
        """
        MorphologyOperations.validate_binary_image(image)
        
        # Normalizacja do 0/255
        img_normalized = image.copy()
        if img_normalized.max() == 1:
            img_normalized = img_normalized * 255
        
        kernel = MorphologyOperations.get_structuring_element(element_shape, element_size)
        result = cv2.morphologyEx(img_normalized, cv2.MORPH_OPEN, kernel, iterations=iterations)
        
        # Zwróć w tym samym formacie co wejście
        if image.max() == 1:
            result = (result / 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def closing(image, element_shape='rect', element_size=3, iterations=1):
        """
        Zamknięcie - dylacja następnie erozja
        Wypełnia małe dziury i łączy blisko położone obiekty
        
        Args:
            image: Obraz binarny
            element_shape: Kształt elementu strukturalnego ('rect', 'cross', 'ellipse')
            element_size: Rozmiar elementu strukturalnego
            iterations: Liczba iteracji
            
        Returns:
            Obraz po zamknięciu
        """
        MorphologyOperations.validate_binary_image(image)
        
        # Normalizacja do 0/255
        img_normalized = image.copy()
        if img_normalized.max() == 1:
            img_normalized = img_normalized * 255
        
        kernel = MorphologyOperations.get_structuring_element(element_shape, element_size)
        result = cv2.morphologyEx(img_normalized, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        
        # Zwróć w tym samym formacie co wejście
        if image.max() == 1:
            result = (result / 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def skeletonization(image):
        """
        Szkieletyzacja - redukcja obiektu binarnego do linii środkowej (szkieletu)
        Implementacja zgodna z algorytmem z wykładu (Algorytm 1)
        
        Algorytm iteracyjnie stosuje operacje ścieniania (thinning) używając
        zestawów elementów strukturalnych w 8 kierunkach (0°, 90°, 180°, 270°
        oraz przekątne).
        
        Args:
            image: Obraz binarny (białe obiekty na czarnym tle)
            
        Returns:
            Szkielet obiektu
        """
        MorphologyOperations.validate_binary_image(image)
        
        # Normalizacja do 0/255
        img_normalized = image.copy()
        if img_normalized.max() == 1:
            img_normalized = img_normalized * 255
        
        # Konwersja do formatu binarnego (0 i 1) dla wygody obliczeń
        _, binary = cv2.threshold(img_normalized, 127, 1, cv2.THRESH_BINARY)
        
        # Definicja elementów strukturalnych dla 8 kierunków
        # zgodnie z algorytmem z wykładu (0°, 90°, 180°, 270° i przekątne)
        
        # Element bazowy [z 0 0; 1 1 0; z 1 z] dla różnych rotacji
        # z = "don't care" (może być 0 lub 1)
        
        # Kierunek 0° (North)
        se_0 = np.array([[0, 0, 0],
                         [0, 1, 0],
                         [1, 1, 1]], dtype=np.uint8)
        
        # Kierunek 90° (East)  
        se_90 = np.array([[0, 0, 1],
                          [0, 1, 1],
                          [0, 0, 1]], dtype=np.uint8)
        
        # Kierunek 180° (South)
        se_180 = np.array([[1, 1, 1],
                           [0, 1, 0],
                           [0, 0, 0]], dtype=np.uint8)
        
        # Kierunek 270° (West)
        se_270 = np.array([[1, 0, 0],
                           [1, 1, 0],
                           [1, 0, 0]], dtype=np.uint8)
        
        # Kierunki przekątne
        se_45 = np.array([[0, 0, 0],
                          [1, 1, 0],
                          [1, 1, 0]], dtype=np.uint8)
        
        se_135 = np.array([[0, 1, 1],
                           [0, 1, 1],
                           [0, 0, 0]], dtype=np.uint8)
        
        se_225 = np.array([[0, 1, 1],
                           [0, 1, 0],
                           [0, 0, 0]], dtype=np.uint8)
        
        se_315 = np.array([[1, 1, 0],
                           [1, 1, 0],
                           [0, 0, 0]], dtype=np.uint8)
        
        # Lista wszystkich elementów strukturalnych
        structuring_elements = [se_0, se_45, se_90, se_135, 
                                se_180, se_225, se_270, se_315]
        
        # Algorytm szkieletyzacji (zgodnie z wykładem)
        remain = binary.copy().astype(np.float32)
        skel = np.zeros_like(remain)
        
        # Iteruj dopóki obraz się zmienia
        while True:
            # false = pozostała część obrazu (przed operacjami)
            false = remain.copy()
            
            # Dla każdego elementu strukturalnego w kolejności 0-7
            for i, se in enumerate(structuring_elements):
                # Hit-or-miss transform
                # Erozja obrazu przez element strukturalny
                eroded = cv2.erode(remain, se, iterations=1)
                
                # Sprawdź czy coś zostało usunięte
                # if sąsiedztwo p odpowiada wzorcowi P then
                # podstaw true jako wartość znacznika skel
                temp = remain - eroded
                skel = np.maximum(skel, temp)
                
                # Usuń dopasowane piksele z remain
                remain = eroded.copy()
            
            # Sprawdź czy obraz się zmienił
            # Jeśli remain = false (nic się nie zmieniło), zakończ
            if np.array_equal(remain, false):
                break
            
            # Dodatkowe kryterium zakończenia - jeśli zostało bardzo mało pikseli
            if np.sum(remain) < 1:
                break
        
        # Finalna szkieletyzacja - dodaj to co zostało w remain do szkieletu
        skel = np.maximum(skel, remain)
        
        # Konwersja z powrotem do 0/255
        skel = (skel * 255).astype(np.uint8)
        
        # Zwróć w tym samym formacie co wejście
        if image.max() == 1:
            skel = (skel / 255).astype(np.uint8)
        
        return skel
    
    @staticmethod
    def get_element_shape_name(shape_key):
        """
        Zwraca czytelną nazwę elementu strukturalnego
        """
        names = {
            'rect': 'Prostokąt',
            'cross': 'Krzyż',
            'ellipse': 'Elipsa'
        }
        return names.get(shape_key, 'Prostokąt')
    
    # @staticmethod
    # def skeletonization(image):
    #     """Szkieletyzacja - algorytm z wykładu"""
    #     MorphologyOperations.validate_binary_image(image)
        
    #     img_normalized = image.copy()
    #     if img_normalized.max() == 1:
    #         img_normalized = img_normalized * 255
        
    #     _, binary = cv2.threshold(img_normalized, 127, 1, cv2.THRESH_BINARY)
        
    #     # 8 elementów strukturalnych (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°)
    #     se_0 = np.array([[0, 0, 0], [0, 1, 0], [1, 1, 1]], dtype=np.uint8)
    #     se_90 = np.array([[0, 0, 1], [0, 1, 1], [0, 0, 1]], dtype=np.uint8)
    #     se_180 = np.array([[1, 1, 1], [0, 1, 0], [0, 0, 0]], dtype=np.uint8)
    #     se_270 = np.array([[1, 0, 0], [1, 1, 0], [1, 0, 0]], dtype=np.uint8)
    #     se_45 = np.array([[0, 0, 0], [1, 1, 0], [1, 1, 0]], dtype=np.uint8)
    #     se_135 = np.array([[0, 1, 1], [0, 1, 1], [0, 0, 0]], dtype=np.uint8)
    #     se_225 = np.array([[0, 1, 1], [0, 1, 0], [0, 0, 0]], dtype=np.uint8)
    #     se_315 = np.array([[1, 1, 0], [1, 1, 0], [0, 0, 0]], dtype=np.uint8)
        
    #     structuring_elements = [se_0, se_45, se_90, se_135, se_180, se_225, se_270, se_315]
        
    #     remain = binary.copy().astype(np.float32)
    #     skel = np.zeros_like(remain)
        
    #     while True:
    #         false = remain.copy()
            
    #         for se in structuring_elements:
    #             eroded = cv2.erode(remain, se, iterations=1)
    #             temp = remain - eroded
    #             skel = np.maximum(skel, temp)
    #             remain = eroded.copy()
            
    #         if np.array_equal(remain, false) or np.sum(remain) < 1:
    #             break
        
    #     skel = np.maximum(skel, remain)
    #     skel = (skel * 255).astype(np.uint8)
        
    #     if image.max() == 1:
    #         skel = (skel / 255).astype(np.uint8)
        
    #     return skel

    @staticmethod
    def skeletonization(image):
        """Szkieletyzacja - redukcja obiektu binarnego do szkieletu"""
        MorphologyOperations.validate_binary_image(image)
        
        img_normalized = image.copy()
        if img_normalized.max() == 1:
            img_normalized = img_normalized * 255
        
        _, binary = cv2.threshold(img_normalized, 127, 1, cv2.THRESH_BINARY)
        
        img = binary.astype(np.uint8)
        skel = np.zeros_like(img)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        
        while True:
            eroded = cv2.erode(img, kernel)
            temp = cv2.dilate(eroded, kernel)
            temp = cv2.subtract(img, temp)
            skel = cv2.bitwise_or(skel, temp)
            img = eroded.copy()
            
            if cv2.countNonZero(img) == 0:
                break
        
        skel = (skel * 255).astype(np.uint8)
        
        if image.max() == 1:
            skel = (skel / 255).astype(np.uint8)
        
        return skel