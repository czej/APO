import tkinter as tk
from tkinter import messagebox


class BinaryOperationDialog(tk.Toplevel):
    """Dialog do wyboru obrazów dla operacji dwuargumentowych (logiczne, arytmetyczne)"""
    
    def __init__(self, parent, operation, operation_type, all_images, app_manager):
        """
        Parametry:
            parent: okno rodzica
            operation: "AND", "OR", "XOR", "Różnica bezwzględna", etc.
            operation_type: "logical" lub "arithmetic"
            all_images: lista wszystkich obrazów
            app_manager: instancja AppManager
        """
        super().__init__(parent)
        
        self.operation = operation
        self.operation_type = operation_type
        self.all_images = all_images
        self.app_manager = app_manager
        self.on_result_callback = None
        
        # Konfiguracja dla różnych typów operacji
        if operation_type == "logical":
            self.min_images = 2
            self.max_images = None
            self.exact_count = None
        elif operation_type == "arithmetic_multi":
            self.min_images = 2
            self.max_images = 5
            self.exact_count = None
        else:  # arithmetic (np. różnica bezwzględna)
            self.min_images = 2
            self.max_images = 2
            self.exact_count = 2
        
        self.title(f"Operacja: {operation}")
        self.geometry("550x500")
        
        self._create_ui()
    
    def _get_operation_info(self):
        """Zwraca opis operacji"""
        if self.operation_type == "logical":
            info_map = {
                "AND": "Wynik = 1 tylko gdy wszystkie piksele = 1\nDziała bit po bicie: obraz1 AND obraz2 AND...",
                "OR": "Wynik = 1 gdy co najmniej jeden piksel = 1\nDziała bit po bicie: obraz1 OR obraz2 OR...",
                "XOR": "Wynik = 1 gdy nieparzysta liczba pikseli = 1\nDziała bit po bicie: obraz1 XOR obraz2 XOR..."
            }
        else:  # arithmetic
            info_map = {
                "Różnica bezwzględna": "Oblicza różnicę bezwzględną: |obraz1 - obraz2|\nPokazuje różnice między obrazami",
                "Dodawanie": "Dodaje 2-5 obrazów.\nZ wysyceniem: obcięcie do 0-255\nBez wysycenia: automatyczne skalowanie"  # DODAJ
            }

        return info_map.get(self.operation, "")
    
    def _create_ui(self):
        """Tworzy interfejs dialogu"""
        # Nagłówek
        header_frame = tk.Frame(self, bg="#f0f0f0", height=100)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        operation_title = f"Operacja {'logiczna' if self.operation_type == 'logical' else 'arytmetyczna'}"
        
        tk.Label(
            header_frame,
            text=f"{operation_title}: {self.operation}",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).pack(pady=(15, 5))
        
        if self.exact_count:
            instruction = f"Wybierz dokładnie {self.exact_count} obrazy"
        elif self.max_images:
            instruction = f"Wybierz {self.min_images}-{self.max_images} obrazów"
        else:
            instruction = f"Wybierz co najmniej {self.min_images} obrazy"
        
        tk.Label(
            header_frame,
            text=instruction,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        ).pack(pady=(0, 3))
        
        tk.Label(
            header_frame,
            text="(Ctrl+klik = wielokrotny wybór | Shift+klik = zakres)",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#999"
        ).pack(pady=(0, 8))
        
        tk.Label(
            header_frame,
            text="⚠ Wszystkie wybrane obrazy muszą mieć identyczny rozmiar i typ",
            font=("Arial", 9, "bold"),
            bg="#f0f0f0",
            fg="#d9534f"
        ).pack()
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Info
        info_frame = tk.LabelFrame(content_frame, text="Informacje o operacji", font=("Arial", 9, "bold"))
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            info_frame,
            text=self._get_operation_info(),
            font=("Arial", 9),
            justify=tk.LEFT,
            fg="#444"
        ).pack(padx=10, pady=8, anchor="w")
        
        # Lista obrazów
        list_header = tk.Frame(content_frame)
        list_header.pack(fill=tk.X, pady=(5, 5))
        
        tk.Label(
            list_header,
            text=f"Dostępne obrazy (łącznie: {len(self.all_images)}):",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT)
        
        tk.Label(
            list_header,
            text=instruction,
            font=("Arial", 8),
            fg="#d9534f"
        ).pack(side=tk.RIGHT)
        
        listbox_frame = tk.Frame(content_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            selectmode=tk.EXTENDED,
            height=12
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Wypełnij listę
        for idx, img in enumerate(self.all_images):
            h, w = img.shape[:2]
            img_type = "Gray" if len(img.shape) == 2 else "Color"
            
            text = f"Obraz {idx + 1:2d} | {w:4d}x{h:4d} | {img_type:5s}"
            self.listbox.insert(tk.END, text)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply,
            width=12,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Anuluj",
            command=self.destroy,
            width=12
        ).pack(side=tk.LEFT, padx=5)
    
    def _apply(self):
        """Zastosuj operację"""
        selection = self.listbox.curselection()
        
        # Sprawdź liczbę wybranych obrazów
        if self.exact_count and len(selection) != self.exact_count:
            messagebox.showwarning(
                "Nieprawidłowa liczba obrazów",
                f"Wybrano: {len(selection)} obraz(ów)\n\n"
                f"{self.operation} wymaga dokładnie {self.exact_count} obrazów."
            )
            return
        elif not self.exact_count and len(selection) < self.min_images:
            messagebox.showwarning(
                "Za mało obrazów",
                f"Wybrano: {len(selection)} obraz(ów)\n\n"
                f"{self.operation} wymaga co najmniej {self.min_images} obrazów."
            )
            return
        elif self.max_images and len(selection) > self.max_images:
            messagebox.showwarning(
                "Za dużo obrazów",
                f"Wybrano: {len(selection)} obraz(ów)\n\n"
                f"{self.operation} obsługuje maksymalnie {self.max_images} obrazów."
            )
            return
        
        # Pobierz wybrane obrazy
        selected_images = [self.all_images[idx] for idx in selection]
        
        # Sprawdź czy wszystkie są grayscale
        non_grayscale = []
        for i, img in enumerate(selected_images):
            if len(img.shape) != 2:
                non_grayscale.append(selection[i] + 1)
        
        if non_grayscale:
            messagebox.showerror(
                "Błąd: Obrazy kolorowe",
                f"Operacje wymagają obrazów w skali szarości!\n\n"
                f"Obrazy kolorowe: {', '.join(map(str, non_grayscale))}\n\n"
                f"Konwertuj: Obraz → Typ → 8-bit Skala szarości"
            )
            return
        
        # Sprawdź rozmiary
        first_shape = selected_images[0].shape
        incompatible = []
        
        for i, img in enumerate(selected_images[1:], start=1):
            if img.shape != first_shape:
                incompatible.append((selection[i] + 1, img.shape))
        
        if incompatible:
            error_msg = f"Wszystkie obrazy muszą mieć identyczny rozmiar!\n\n"
            error_msg += f"Pierwszy obraz (nr {selection[0] + 1}): {first_shape[1]}x{first_shape[0]}\n\n"
            error_msg += "Niekompatybilne:\n"
            for img_num, shape in incompatible:
                error_msg += f"  • Obraz {img_num}: {shape[1]}x{shape[0]}\n"
            
            messagebox.showerror("Błąd: Niezgodne rozmiary", error_msg)
            return
        
        # Wykonaj operację
        try:
            if self.operation_type == "logical":
                result = selected_images[0]
                for img in selected_images[1:]:
                    if self.operation == "AND":
                        result = self.app_manager.apply_logical_and(result, img)
                    elif self.operation == "OR":
                        result = self.app_manager.apply_logical_or(result, img)
                    elif self.operation == "XOR":
                        result = self.app_manager.apply_logical_xor(result, img)
            elif self.operation_type == "arithmetic":
                if self.operation == "Różnica bezwzględna":
                    result = self.app_manager.apply_absolute_difference(
                        selected_images[0], 
                        selected_images[1]
                    )
            elif self.operation_type == "arithmetic_multi":
                if self.operation == "Dodawanie":
                    # Dialog wyboru wysycenia
                    saturation = self._ask_saturation()
                    if saturation is None:  # User anulował
                        return
                    result = self.app_manager.apply_add_images(selected_images, saturation)
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Błąd operacji", str(e))

    def _ask_saturation(self):
        """
        Pyta użytkownika o tryb wysycenia.
        
        Zwraca:
            True: z wysyceniem
            False: bez wysycenia
            None: anulowano
        """
        dialog = tk.Toplevel(self)
        dialog.title("Wybierz tryb")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        result = [None]  # Lista dla closure
        
        tk.Label(
            dialog,
            text="Wybierz tryb dodawania:",
            font=("Arial", 11, "bold")
        ).pack(pady=(20, 10))
        
        saturation_var = tk.BooleanVar(value=True)
        
        tk.Radiobutton(
            dialog,
            text="Z wysyceniem (obcięcie do 0-255)",
            variable=saturation_var,
            value=True,
            font=("Arial", 10)
        ).pack(anchor="w", padx=40, pady=5)
        
        tk.Radiobutton(
            dialog,
            text="Bez wysycenia (automatyczne skalowanie)",
            variable=saturation_var,
            value=False,
            font=("Arial", 10)
        ).pack(anchor="w", padx=40, pady=5)
        
        def on_ok():
            result[0] = saturation_var.get()
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            width=10,
            bg="#4CAF50",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Anuluj",
            command=on_cancel,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result[0]