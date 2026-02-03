import cv2
import numpy as np


class CustomMorphologyOperations:
    """
    Erozja i dylacja z dowolnym elementem strukturyzującym podanym przez
    użytkownika oraz z możliwością określenia punktu zaczepienia (anchor).
    Zamiast cv2.erode / cv2.dilate używamy cv2.morphologyEx,
    który przyjmuje dowolną macierz uint8 jako kernel oraz anchor.
    """

    # ─── walidacja ────────────────────────────────────────────────────────

    @staticmethod
    def _validate_binary(image: np.ndarray) -> None:
        """
        Sprawdza, czy obraz jest binarny (wartości 0/255 lub 0/1).
        Rzuca ValueError z czytelną wiadomością jeśli nie jest.
        """
        if image.ndim != 2:
            raise ValueError(
                "Obraz nie jest jednokanalowy.\n"
                "Wymagany obraz w skali szarości (2D)."
            )

        unique = set(np.unique(image).tolist())
        # dopuszczamy {0}, {1}, {255}, {0, 1}, {0, 255}
        if not (unique.issubset({0, 255}) or unique.issubset({0, 1})):
            raise ValueError(
                "Obraz nie jest binarny.\n\n"
                "Dozwolone wartości pikselów: 0/255 lub 0/1.\n"
                f"Znalezione wartości: {sorted(unique)}\n\n"
                "Wskazówka: przekonwertuj obraz na binarny np.\n"
                "Przetwarzanie → Binaryzacja → Progowanie Otsu"
            )

    @staticmethod
    def _validate_kernel(kernel: np.ndarray) -> None:
        """
        Sprawdza poprawność kernela:
        - musi być macierzą 2D numpy uint8
        - musi zawierać przynajmniej jeden piksel != 0
        """
        if kernel.ndim != 2:
            raise ValueError("Kernel musi być macierzą 2D.")
        if kernel.size == 0:
            raise ValueError("Kernel nie może być pusty.")
        if not np.any(kernel):
            raise ValueError(
                "Element strukturyzujący jest pusty (same zeros).\n"
                "Zaznacz przynajmniej jedną komórę."
            )

    @staticmethod
    def _validate_anchor(anchor: tuple[int, int], kernel_shape: tuple[int, int]) -> None:
        """
        Sprawdza poprawność punktu zaczepienia.
        """
        if not isinstance(anchor, tuple) or len(anchor) != 2:
            raise ValueError("Anchor musi być krotką (row, col).")
        r, c = anchor
        h, w = kernel_shape
        if not (0 <= r < h and 0 <= c < w):
            raise ValueError(
                f"Anchor ({r}, {c}) jest poza zakresem kernela ({h}x{w})."
            )

    # ─── helper ───────────────────────────────────────────────────────────

    @staticmethod
    def _is_01_mask(image: np.ndarray) -> bool:
        """True jeśli obraz jest maską 0/1 (max wartość <= 1)."""
        return image.max() <= 1

    @staticmethod
    def _convert_anchor_to_cv2(anchor: tuple[int, int]) -> tuple[int, int]:
        """
        Konwertuje anchor z formatu (row, col) na format OpenCV (x, y).
        OpenCV używa (col, row) jako (x, y).
        """
        row, col = anchor
        return (col, row)  # (x, y) dla OpenCV

    # ─── operacje ─────────────────────────────────────────────────────────

    @staticmethod
    def erode(image: np.ndarray, kernel: np.ndarray, anchor: tuple[int, int],
              border_type: str = "BORDER_REFLECT", border_value: int = 0) -> np.ndarray:
        """
        Erozja obrazu binarnego z podanym elementem strukturyzującym i punktem zaczepienia.
        Działa dla maski 0/255 i 0/1 — wynik ma ten sam zakres co wejście.
        
        Parameters
        ----------
        image        : obraz binarny (0/255 lub 0/1)
        kernel       : element strukturyzujący (0/1)
        anchor       : punkt zaczepienia (row, col) - współrzędne w kernelu
        border_type  : "BORDER_CONSTANT" | "BORDER_REFLECT" | "Wypełnienie wyniku stałą"
        border_value : wartość dla BORDER_CONSTANT / wypełnienia (0-255)
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)
        CustomMorphologyOperations._validate_anchor(anchor, kernel.shape)

        kernel = kernel.astype(np.uint8)
        is_01 = CustomMorphologyOperations._is_01_mask(image)
        
        # Konwertuj anchor na format OpenCV (x, y)
        cv_anchor = CustomMorphologyOperations._convert_anchor_to_cv2(anchor)

        # Normalize to 0/255 for morphologyEx
        work = image * 255 if is_01 else image
        
        # Handle border types
        if border_type == "Wypełnienie wyniku stałą":
            # Fill result with constant, compute only interior
            result = np.full_like(work, border_value, dtype=np.uint8)
            anchor_r, anchor_c = anchor
            h, w = work.shape
            kh, kw = kernel.shape
            
            # Iterate over output pixels
            for i in range(h):
                for j in range(w):
                    # Define ROI boundaries based on anchor
                    r_start = i - anchor_r
                    r_end = r_start + kh
                    c_start = j - anchor_c
                    c_end = c_start + kw
                    
                    # Check if entire kernel fits within image
                    if r_start >= 0 and r_end <= h and c_start >= 0 and c_end <= w:
                        roi = work[r_start:r_end, c_start:c_end]
                        # Erosion: min of roi where kernel == 1
                        masked_vals = roi[kernel == 1]
                        if len(masked_vals) > 0:
                            result[i, j] = np.min(masked_vals)
        
        elif border_type == "BORDER_CONSTANT":
            # Add border before morphologyEx
            anchor_r, anchor_c = anchor
            pad_top = anchor_r
            pad_bottom = kernel.shape[0] - anchor_r - 1
            pad_left = anchor_c
            pad_right = kernel.shape[1] - anchor_c - 1
            
            padded = cv2.copyMakeBorder(
                work, pad_top, pad_bottom, pad_left, pad_right,
                cv2.BORDER_CONSTANT, value=float(border_value)
            )
            temp = cv2.morphologyEx(padded, cv2.MORPH_ERODE, kernel, anchor=cv_anchor)
            result = temp[pad_top:pad_top+work.shape[0], pad_left:pad_left+work.shape[1]]
        
        else:  # BORDER_REFLECT
            cv_border = cv2.BORDER_REFLECT
            result = cv2.morphologyEx(work, cv2.MORPH_ERODE, kernel, 
                                     anchor=cv_anchor, borderType=cv_border)

        return (result // 255).astype(np.uint8) if is_01 else result

    @staticmethod
    def dilate(image: np.ndarray, kernel: np.ndarray, anchor: tuple[int, int],
               border_type: str = "BORDER_REFLECT", border_value: int = 0) -> np.ndarray:
        """
        Dylacja obrazu binarnego z podanym elementem strukturyzującym i punktem zaczepienia.
        Działa dla maski 0/255 i 0/1 — wynik ma ten sam zakres co wejście.
        
        Parameters
        ----------
        image        : obraz binarny (0/255 lub 0/1)
        kernel       : element strukturyzujący (0/1)
        anchor       : punkt zaczepienia (row, col) - współrzędne w kernelu
        border_type  : "BORDER_CONSTANT" | "BORDER_REFLECT" | "Wypełnienie wyniku stałą"
        border_value : wartość dla BORDER_CONSTANT / wypełnienia (0-255)
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)
        CustomMorphologyOperations._validate_anchor(anchor, kernel.shape)

        kernel = kernel.astype(np.uint8)
        is_01 = CustomMorphologyOperations._is_01_mask(image)
        
        # Konwertuj anchor na format OpenCV (x, y)
        cv_anchor = CustomMorphologyOperations._convert_anchor_to_cv2(anchor)

        # Normalize to 0/255 for morphologyEx
        work = image * 255 if is_01 else image
        
        # Handle border types
        if border_type == "Wypełnienie wyniku stałą":
            # Fill result with constant, compute only interior
            result = np.full_like(work, border_value, dtype=np.uint8)
            anchor_r, anchor_c = anchor
            h, w = work.shape
            kh, kw = kernel.shape
            
            # Iterate over output pixels
            for i in range(h):
                for j in range(w):
                    # Define ROI boundaries based on anchor
                    r_start = i - anchor_r
                    r_end = r_start + kh
                    c_start = j - anchor_c
                    c_end = c_start + kw
                    
                    # Check if entire kernel fits within image
                    if r_start >= 0 and r_end <= h and c_start >= 0 and c_end <= w:
                        roi = work[r_start:r_end, c_start:c_end]
                        # Dilation: max of roi where kernel == 1
                        masked_vals = roi[kernel == 1]
                        if len(masked_vals) > 0:
                            result[i, j] = np.max(masked_vals)
        
        elif border_type == "BORDER_CONSTANT":
            # Add border before morphologyEx
            anchor_r, anchor_c = anchor
            pad_top = anchor_r
            pad_bottom = kernel.shape[0] - anchor_r - 1
            pad_left = anchor_c
            pad_right = kernel.shape[1] - anchor_c - 1
            
            padded = cv2.copyMakeBorder(
                work, pad_top, pad_bottom, pad_left, pad_right,
                cv2.BORDER_CONSTANT, value=float(border_value)
            )
            temp = cv2.morphologyEx(padded, cv2.MORPH_DILATE, kernel, anchor=cv_anchor)
            result = temp[pad_top:pad_top+work.shape[0], pad_left:pad_left+work.shape[1]]
        
        else:  # BORDER_REFLECT
            cv_border = cv2.BORDER_REFLECT
            result = cv2.morphologyEx(work, cv2.MORPH_DILATE, kernel,
                                     anchor=cv_anchor, borderType=cv_border)

        return (result // 255).astype(np.uint8) if is_01 else result