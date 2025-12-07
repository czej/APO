import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np


class ConvolutionDialog:
    """
    Bazowy dialog dla operacji konwolucji
    Umożliwia wybór typu brzegu i wartości stałej
    """
    
    def __init__(self, parent, title, image, app_manager):
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        # Okno dialogowe
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x350")
        self.window.resizable(False, False)
        
        # Centrowanie okna
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Tworzy podstawowe widgety (do nadpisania)"""
        pass
    
    def _create_border_controls(self, parent_frame, start_row=0):
        """
        Tworzy kontrolki wyboru typu brzegu
        Zwraca numer następnego wolnego wiersza
        """
        # Separator
        ttk.Separator(parent_frame, orient='horizontal').grid(
            row=start_row, column=0, columnspan=2, sticky='ew', pady=10
        )
        
        # Wybór typu brzegu
        ttk.Label(parent_frame, text="Typ brzegu:").grid(
            row=start_row+1, column=0, sticky='w', padx=10, pady=5
        )
        
        self.border_type_var = tk.StringVar(value="BORDER_REFLECT")
        border_combo = ttk.Combobox(
            parent_frame,
            textvariable=self.border_type_var,
            values=self.app_manager.get_border_types(),
            state='readonly',
            width=25
        )
        border_combo.grid(row=start_row+1, column=1, sticky='w', padx=10, pady=5)
        border_combo.bind('<<ComboboxSelected>>', self._on_border_type_changed)
        
        # Wartość stała dla BORDER_CONSTANT
        ttk.Label(parent_frame, text="Wartość stała (0-255):").grid(
            row=start_row+2, column=0, sticky='w', padx=10, pady=5
        )
        
        self.border_value_var = tk.IntVar(value=0)
        self.border_value_spinbox = ttk.Spinbox(
            parent_frame,
            from_=0,
            to=255,
            textvariable=self.border_value_var,
            width=23,
            state='disabled'
        )
        self.border_value_spinbox.grid(row=start_row+2, column=1, sticky='w', padx=10, pady=5)
        
        return start_row + 3
    
    def _on_border_type_changed(self, event=None):
        """Włącza/wyłącza spinbox wartości w zależności od typu brzegu"""
        border_type = self.border_type_var.get()
        if border_type in ["BORDER_CONSTANT", "Wypełnienie wyniku stałą"]:
            self.border_value_spinbox.config(state='normal')
        else:
            self.border_value_spinbox.config(state='disabled')
    
    def _apply_and_show(self):
        """Zastosuj operację i pokaż wynik (do nadpisania)"""
        pass
    
    def _create_buttons(self, parent_frame, row):
        """Tworzy przyciski OK i Anuluj"""
        button_frame = ttk.Frame(parent_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply_and_show,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)


class SmoothingDialog(ConvolutionDialog):
    """Dialog dla wygładzania liniowego"""
    
    def __init__(self, parent, image, app_manager):
        # Nadpisujemy __init__ żeby mieć większe okno
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Wygładzanie liniowe")
        self.window.geometry("450x550")
        self.window.resizable(False, False)
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Wybór maski
        ttk.Label(main_frame, text="Wybierz maskę wygładzania:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 10)
        )
        
        self.mask_var = tk.StringVar(value=self.app_manager.get_smoothing_masks()[0])
        mask_combo = ttk.Combobox(
            main_frame,
            textvariable=self.mask_var,
            values=self.app_manager.get_smoothing_masks(),
            state='readonly',
            width=30
        )
        mask_combo.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        mask_combo.bind('<<ComboboxSelected>>', self._update_mask_display)
        
        # Ramka na wyświetlenie maski
        mask_display_frame = ttk.LabelFrame(main_frame, text="Podgląd maski 3x3:", padding="10")
        mask_display_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        
        # Grid do wyświetlenia maski
        self.mask_labels = []
        for i in range(3):
            row_labels = []
            for j in range(3):
                label = ttk.Label(
                    mask_display_frame,
                    text="0",
                    font=('Courier', 11, 'bold'),
                    width=6,
                    anchor='center',
                    relief='solid',
                    borderwidth=1
                )
                label.grid(row=i, column=j, padx=2, pady=2)
                row_labels.append(label)
            self.mask_labels.append(row_labels)
        
        # Współczynnik
        self.divisor_label = ttk.Label(
            mask_display_frame,
            text="/ 1",
            font=('Arial', 11, 'bold'),
            foreground='#0066cc'
        )
        self.divisor_label.grid(row=1, column=3, padx=10)
        
        # Wyświetl początkową maskę
        self._update_mask_display()
        
        # Kontrolki brzegu
        next_row = self._create_border_controls(main_frame, start_row=3)
        
        # Przyciski
        self._create_buttons(main_frame, next_row)
    
    def _update_mask_display(self, event=None):
        """Aktualizuje wyświetlanie wartości maski"""
        from backend.ConvolutionOperations import ConvolutionOperations
        conv_ops = ConvolutionOperations()
        
        mask_name = self.mask_var.get()
        mask = conv_ops.SMOOTHING_MASKS.get(mask_name)
        
        if mask is not None:
            # Odtwórz oryginalne wartości całkowite
            # Suma znormalizowanej maski powinna być bliska 1.0
            sum_normalized = np.sum(mask)
            
            if abs(sum_normalized - 1.0) < 0.01:  # Maska jest znormalizowana
                # Znajdź współczynnik - sprawdź możliwe wartości
                # Dla "Uśrednienie": suma oryginalna = 5
                # Dla "Filtr Gaussa": suma oryginalna = 17
                
                # Przemnóż przez różne współczynniki i sprawdź który daje całkowite
                for divisor in [5, 17, 9, 16, 25]:  # Typowe współczynniki
                    int_mask = mask * divisor
                    # Sprawdź czy wszystkie wartości są bliskie całkowitym
                    if np.allclose(int_mask, np.round(int_mask), atol=0.01):
                        # Znaleziono właściwy współczynnik
                        for i in range(3):
                            for j in range(3):
                                value = int(round(int_mask[i, j]))
                                self.mask_labels[i][j].config(text=f"{value}")
                        
                        self.divisor_label.config(text=f"/ {divisor}")
                        return
            
            # Fallback - pokaż wartości rzeczywiste
            for i in range(3):
                for j in range(3):
                    value = mask[i, j]
                    self.mask_labels[i][j].config(text=f"{value:.3f}")
            
            self.divisor_label.config(text="")
    
    def _apply_and_show(self):
        try:
            result = self.app_manager.apply_smoothing(
                self.image,
                self.mask_var.get(),
                self.border_type_var.get(),
                self.border_value_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")


class SharpeningDialog(ConvolutionDialog):
    """Dialog dla wyostrzania (Laplacjan)"""
    
    def __init__(self, parent, image, app_manager):
        # Nadpisujemy __init__ żeby mieć większe okno
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Wyostrzanie (Laplacjan)")
        self.window.geometry("450x550")
        self.window.resizable(False, False)
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Wybór maski
        ttk.Label(main_frame, text="Wybierz maskę Laplacjana:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 10)
        )
        
        self.mask_var = tk.StringVar(value=self.app_manager.get_laplacian_masks()[0])
        mask_combo = ttk.Combobox(
            main_frame,
            textvariable=self.mask_var,
            values=self.app_manager.get_laplacian_masks(),
            state='readonly',
            width=30
        )
        mask_combo.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        mask_combo.bind('<<ComboboxSelected>>', self._update_mask_display)
        
        # Ramka na wyświetlenie maski
        mask_display_frame = ttk.LabelFrame(main_frame, text="Podgląd maski 3x3:", padding="10")
        mask_display_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        
        # Grid do wyświetlenia maski
        self.mask_labels = []
        for i in range(3):
            row_labels = []
            for j in range(3):
                label = ttk.Label(
                    mask_display_frame,
                    text="0",
                    font=('Courier', 11, 'bold'),
                    width=6,
                    anchor='center',
                    relief='solid',
                    borderwidth=1
                )
                label.grid(row=i, column=j, padx=2, pady=2)
                row_labels.append(label)
            self.mask_labels.append(row_labels)
        
        # Wyświetl początkową maskę
        self._update_mask_display()
        
        # Kontrolki brzegu
        next_row = self._create_border_controls(main_frame, start_row=3)
        
        # Przyciski
        self._create_buttons(main_frame, next_row)
    
    def _update_mask_display(self, event=None):
        """Aktualizuje wyświetlanie wartości maski"""
        from backend.ConvolutionOperations import ConvolutionOperations
        conv_ops = ConvolutionOperations()
        
        mask_name = self.mask_var.get()
        mask = conv_ops.LAPLACIAN_MASKS.get(mask_name)
        
        if mask is not None:
            for i in range(3):
                for j in range(3):
                    value = int(mask[i, j])
                    self.mask_labels[i][j].config(text=f"{value}")
    
    def _apply_and_show(self):
        try:
            result = self.app_manager.apply_sharpening(
                self.image,
                self.mask_var.get(),
                self.border_type_var.get(),
                self.border_value_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")


class PrewittDialog(ConvolutionDialog):
    """Dialog dla kierunkowej detekcji krawędzi Prewitta"""
    
    def __init__(self, parent, image, app_manager):
        super().__init__(parent, "Detekcja krawędzi - Prewitt", image, app_manager)
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Wybór kierunku
        ttk.Label(main_frame, text="Wybierz kierunek detekcji:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 10)
        )
        
        self.direction_var = tk.StringVar(value=self.app_manager.get_prewitt_directions()[0])
        direction_combo = ttk.Combobox(
            main_frame,
            textvariable=self.direction_var,
            values=self.app_manager.get_prewitt_directions(),
            state='readonly',
            width=30
        )
        direction_combo.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        # Kontrolki brzegu
        next_row = self._create_border_controls(main_frame, start_row=2)
        
        # Przyciski
        self._create_buttons(main_frame, next_row)
    
    def _apply_and_show(self):
        try:
            result = self.app_manager.apply_prewitt(
                self.image,
                self.direction_var.get(),
                self.border_type_var.get(),
                self.border_value_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")


class SobelDialog(ConvolutionDialog):
    """Dialog dla detekcji krawędzi Sobela"""
    
    def __init__(self, parent, image, app_manager):
        super().__init__(parent, "Detekcja krawędzi - Sobel", image, app_manager)
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info
        ttk.Label(
            main_frame, 
            text="Operator Sobela używa dwóch prostopadłych masek\ndo obliczenia magnitūdy gradientu.",
            font=('Arial', 9),
            foreground='#666'
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Kontrolki brzegu
        next_row = self._create_border_controls(main_frame, start_row=1)
        
        # Przyciski
        self._create_buttons(main_frame, next_row)
    
    def _apply_and_show(self):
        try:
            result = self.app_manager.apply_sobel(
                self.image,
                self.border_type_var.get(),
                self.border_value_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")


class CustomMaskDialog(ConvolutionDialog):
    """Dialog dla własnej maski 3x3 zdefiniowanej przez użytkownika"""
    
    def __init__(self, parent, image, app_manager):
        # Nie wywołujemy super().__init__ bo chcemy niestandardowy rozmiar
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        # Okno dialogowe - większe niż standardowe
        self.window = tk.Toplevel(parent)
        self.window.title("Własna maska 3x3")
        self.window.geometry("480x500")
        self.window.resizable(False, False)
        
        # Centrowanie okna
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nagłówek
        header = ttk.Label(
            main_frame, 
            text="Zdefiniuj własną maskę 3x3:",
            font=('Arial', 10, 'bold')
        )
        header.pack(pady=(0, 10))
        
        # Rama dla grida 3x3
        grid_frame = ttk.Frame(main_frame)
        grid_frame.pack(pady=10)
        
        # Grid 3x3 dla wartości
        self.mask_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = ttk.Entry(grid_frame, width=8, justify='center')
                entry.grid(row=i, column=j, padx=5, pady=5)
                entry.insert(0, "0")
                entry.bind('<KeyRelease>', self._update_divisor)
                row_entries.append(entry)
            self.mask_entries.append(row_entries)
        
        # Rama dla dzielnika
        divisor_frame = ttk.Frame(main_frame)
        divisor_frame.pack(pady=10)
        
        ttk.Label(divisor_frame, text="Dzielnik (suma wag):").pack(side=tk.LEFT, padx=5)
        
        self.divisor_var = tk.StringVar(value="0")
        divisor_label = ttk.Label(
            divisor_frame,
            textvariable=self.divisor_var,
            font=('Arial', 10, 'bold'),
            foreground='#0066cc'
        )
        divisor_label.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Rama dla kontrolek brzegu
        border_frame = ttk.Frame(main_frame)
        border_frame.pack(fill='x', pady=5)
        
        ttk.Label(border_frame, text="Typ brzegu:").pack(side=tk.LEFT, padx=5)
        
        self.border_type_var = tk.StringVar(value="BORDER_REFLECT")
        border_combo = ttk.Combobox(
            border_frame,
            textvariable=self.border_type_var,
            values=self.app_manager.get_border_types(),
            state='readonly',
            width=25
        )
        border_combo.pack(side=tk.LEFT, padx=5)
        border_combo.bind('<<ComboboxSelected>>', self._on_border_type_changed)
        
        # Wartość stała
        value_frame = ttk.Frame(main_frame)
        value_frame.pack(fill='x', pady=5)
        
        ttk.Label(value_frame, text="Wartość stała (0-255):").pack(side=tk.LEFT, padx=5)
        
        self.border_value_var = tk.IntVar(value=0)
        self.border_value_spinbox = ttk.Spinbox(
            value_frame,
            from_=0,
            to=255,
            textvariable=self.border_value_var,
            width=23,
            state='disabled'
        )
        self.border_value_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply_and_show,
            width=20
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy,
            width=20
        ).pack(side=tk.LEFT, padx=10)
    
    def _apply_and_show(self):
        try:
            # Pobierz wartości z grida
            mask = np.zeros((3, 3), dtype=np.float32)
            for i in range(3):
                for j in range(3):
                    try:
                        value = float(self.mask_entries[i][j].get())
                        mask[i, j] = value
                    except ValueError:
                        messagebox.showerror("Błąd", f"Nieprawidłowa wartość w pozycji [{i},{j}]")
                        return
            
            # Pobierz dzielnik
            try:
                divisor = float(self.divisor_var.get())
            except ValueError:
                divisor = 1.0
            
            if divisor == 0:
                divisor = 1.0
            
            # Zastosuj dzielnik
            mask = mask / divisor
            
            # Wywołaj operację
            result = self.app_manager.apply_custom_mask(
                self.image,
                mask,
                self.border_type_var.get(),
                self.border_value_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")
    
    def _update_divisor(self, event=None):
        """Automatycznie wylicza sumę wartości w gridzie"""
        total = 0
        for i in range(3):
            for j in range(3):
                try:
                    value = float(self.mask_entries[i][j].get())
                    total += value
                except ValueError:
                    pass
        
        # Jeśli suma <= 0, użyj 1
        if total <= 0:
            total = 1.0
        
        self.divisor_var.set(f"{total:.2f}")


class CannyDialog:
    """Dialog dla detekcji krawędzi Canny"""
    
    def __init__(self, parent, image, app_manager):
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Detekcja krawędzi - Canny")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame, 
            text="Operator Canny'ego - detekcja krawędzi z histerezą",
            font=('Arial', 10, 'bold')
        ).pack(pady=(0, 15))
        
        # Threshold 1
        threshold1_frame = ttk.Frame(main_frame)
        threshold1_frame.pack(fill='x', pady=5)
        
        ttk.Label(threshold1_frame, text="Dolny próg:").pack(side=tk.LEFT, padx=5)
        
        self.threshold1_var = tk.IntVar(value=100)
        ttk.Spinbox(
            threshold1_frame,
            from_=0,
            to=255,
            textvariable=self.threshold1_var,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Threshold 2
        threshold2_frame = ttk.Frame(main_frame)
        threshold2_frame.pack(fill='x', pady=5)
        
        ttk.Label(threshold2_frame, text="Górny próg:").pack(side=tk.LEFT, padx=5)
        
        self.threshold2_var = tk.IntVar(value=200)
        ttk.Spinbox(
            threshold2_frame,
            from_=0,
            to=255,
            textvariable=self.threshold2_var,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            main_frame,
            text="Zalecane: górny próg = 2-3 × dolny próg",
            font=('Arial', 8),
            foreground='#666'
        ).pack(pady=10)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply_and_show,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _apply_and_show(self):
        try:
            result = self.app_manager.apply_canny(
                self.image,
                self.threshold1_var.get(),
                self.threshold2_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")


class MedianDialog:
    """Dialog dla filtru medianowego"""
    
    def __init__(self, parent, image, app_manager):
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Filtr medianowy")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame, 
            text="Filtr medianowy - redukcja szumu",
            font=('Arial', 10, 'bold')
        ).pack(pady=(0, 15))
        
        # Rozmiar kernela
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill='x', pady=5)
        
        ttk.Label(size_frame, text="Rozmiar otoczenia:").pack(side=tk.LEFT, padx=5)
        
        self.size_var = tk.IntVar(value=3)
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=[3, 5, 7, 9],
            state='readonly',
            width=15
        )
        size_combo.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Typ brzegu
        border_frame = ttk.Frame(main_frame)
        border_frame.pack(fill='x', pady=5)
        
        ttk.Label(border_frame, text="Typ brzegu:").pack(side=tk.LEFT, padx=5)
        
        self.border_type_var = tk.StringVar(value="BORDER_REFLECT")
        border_combo = ttk.Combobox(
            border_frame,
            textvariable=self.border_type_var,
            values=self.app_manager.get_border_types(),
            state='readonly',
            width=25
        )
        border_combo.pack(side=tk.LEFT, padx=5)
        border_combo.bind('<<ComboboxSelected>>', self._on_border_type_changed)
        
        # Wartość stała
        value_frame = ttk.Frame(main_frame)
        value_frame.pack(fill='x', pady=5)
        
        ttk.Label(value_frame, text="Wartość stała (0-255):").pack(side=tk.LEFT, padx=5)
        
        self.border_value_var = tk.IntVar(value=0)
        self.border_value_spinbox = ttk.Spinbox(
            value_frame,
            from_=0,
            to=255,
            textvariable=self.border_value_var,
            width=23,
            state='disabled'
        )
        self.border_value_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply_and_show,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_border_type_changed(self, event=None):
        border_type = self.border_type_var.get()
        if border_type in ["BORDER_CONSTANT", "Wypełnienie wyniku stałą"]:
            self.border_value_spinbox.config(state='normal')
        else:
            self.border_value_spinbox.config(state='disabled')
    
    def _apply_and_show(self):
        try:
            result = self.app_manager.apply_median(
                self.image,
                self.size_var.get(),
                self.border_type_var.get(),
                self.border_value_var.get()
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykonać operacji:\n{str(e)}")