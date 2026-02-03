import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
from PIL import Image, ImageTk


class StructuringElementEditor(tk.Frame):
    """
    Interaktywny edytor elementu strukturyzującego.

    - Siatka NxN przycisków-toggleów
    - Zmiana rozmiaru siatki
    - Presety: pełny, krzyż, X, ramka.
    - Wybór punktu zaczepienia (anchor point) - podświetlony na czerwono
    - Odczyt bieżącego kernela i punktu zaczepienia
    """

    # kolory komórki
    _COLOR_ON  = "#4CAF50"   # zielone — piksel aktywny
    _COLOR_OFF = "#2d2d2d"   # ciemne  — piksel nieaktywny
    _COLOR_HOVER_ON  = "#66BB6A"
    _COLOR_HOVER_OFF = "#3e3e3e"
    _COLOR_ANCHOR = "#ff3333"  # czerwone — anchor na nieaktywnym
    _COLOR_ANCHOR_HOVER = "#ff5555"
    _COLOR_ANCHOR_ACTIVE = "#ff8800"  # pomarańczowy — anchor na aktywnym (zielone+czerwone)
    _COLOR_ANCHOR_ACTIVE_HOVER = "#ffaa33"

    def __init__(self, master, initial_size: int = 3):
        super().__init__(master, bg="#1e1e1e", padx=6, pady=6)

        self._size = initial_size
        # macierz wartości 0/1
        self._grid: list[list[int]] = []
        # lista widżetów Button
        self._buttons: list[list[tk.Button]] = []
        # punkt zaczepienia (domyślnie środek)
        self._anchor = (initial_size // 2, initial_size // 2)

        self._build_controls()
        self._build_grid_frame()
        self._init_grid(self._size)
        self._apply_preset_cross()   # domyślny preset — krzyż

    # ─── kontrolki nad siatką ─────────────────────────────────────────────

    def _build_controls(self):
        ctrl = tk.Frame(self, bg="#1e1e1e")
        ctrl.pack(fill=tk.X, pady=(0, 4))

        # --- rozmiar ---
        size_frame = tk.Frame(ctrl, bg="#1e1e1e")
        size_frame.pack(side=tk.LEFT)

        tk.Label(size_frame, text="Rozmiar:", bg="#1e1e1e",
                 fg="#ccc", font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 4))

        self._size_var = tk.IntVar(value=self._size)
        sizes = [3, 5, 7, 9, 11, 13]
        self._size_combo = ttk.Combobox(
            size_frame, values=sizes, textvariable=self._size_var,
            width=4, state="readonly"
        )
        self._size_combo.pack(side=tk.LEFT)
        self._size_combo.bind("<<ComboboxSelected>>", self._on_size_change)

        # --- presets ---
        preset_frame = tk.Frame(ctrl, bg="#1e1e1e")
        preset_frame.pack(side=tk.RIGHT)

        tk.Label(preset_frame, text="Preset:", bg="#1e1e1e",
                 fg="#ccc", font=("Consolas", 9)).pack(side=tk.LEFT, padx=(8, 4))

        for label, method in [("Pełny", self._apply_preset_full),
                              ("Krzyż", self._apply_preset_cross),
                              ("X",     self._apply_preset_x),
                              ("Ramka", self._apply_preset_frame)]:
            tk.Button(
                preset_frame, text=label, command=method,
                bg="#3a3a3a", fg="#eee", relief=tk.FLAT,
                activebackground="#555", activeforeground="#fff",
                font=("Consolas", 8), padx=6, pady=2, bd=0
            ).pack(side=tk.LEFT, padx=2)

    # ─── siatka toggleów ──────────────────────────────────────────────────

    def _build_grid_frame(self):
        # Fixed-size frame, grid scales to fit
        self._grid_frame = tk.Frame(self, bg="#1e1e1e")
        self._grid_frame.pack(pady=4)

    def _init_grid(self, n: int):
        """Czyści i buduje siatką NxN."""
        # usuwanie starych widżetów
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._grid = []
        self._buttons = []
        self._size = n
        # ustaw anchor na środek przy zmianie rozmiaru
        self._anchor = (n // 2, n // 2)

        # Skalowanie kwadratow        
        if n <= 5:
            pad = 12
        elif n <= 9:
            pad = 6
        else:
            pad = 0

        for r in range(n):
            row_vals = []
            row_btns = []
            for c in range(n):
                val = 0
                row_vals.append(val)
                btn = tk.Button(
                    self._grid_frame,
                    width=1, height=1,
                    bg=self._COLOR_OFF,
                    activebackground=self._COLOR_HOVER_OFF,
                    relief=tk.FLAT, bd=1, highlightthickness=1,
                    highlightbackground="#444"
                )
                btn.grid(row=r, column=c, padx=1, pady=1, ipady=pad, ipadx=pad)
                # zamknięcie nad r, c w lambda
                btn.config(command=lambda row=r, col=c: self._toggle(row, col))
                btn.bind("<Enter>", lambda e, row=r, col=c: self._on_hover(row, col, True))
                btn.bind("<Leave>", lambda e, row=r, col=c: self._on_hover(row, col, False))
                # prawy przycisk myszy - ustaw anchor
                btn.bind("<Button-3>", lambda e, row=r, col=c: self._set_anchor(row, col))
                row_btns.append(btn)
            self._grid.append(row_vals)
            self._buttons.append(row_btns)

    def _toggle(self, r: int, c: int):
        self._grid[r][c] = 1 - self._grid[r][c]
        self._refresh_button(r, c)
        # trigger callback if set
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    def _set_anchor(self, r: int, c: int):
        """Ustawia punkt zaczepienia na (r, c)."""
        old_anchor = self._anchor
        self._anchor = (r, c)
        # odśwież stary i nowy anchor
        self._refresh_button(old_anchor[0], old_anchor[1])
        self._refresh_button(r, c)
        # trigger callback
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    def _on_hover(self, r: int, c: int, entering: bool):
        btn = self._buttons[r][c]
        if entering:
            if (r, c) == self._anchor:
                # anchor - hover version zależna od stanu
                if self._grid[r][c]:
                    btn.config(bg=self._COLOR_ANCHOR_ACTIVE_HOVER)
                else:
                    btn.config(bg=self._COLOR_ANCHOR_HOVER)
            else:
                btn.config(bg=self._COLOR_HOVER_ON if self._grid[r][c] else self._COLOR_HOVER_OFF)
        else:
            self._refresh_button(r, c)

    def _refresh_button(self, r: int, c: int):
        """Odświeża kolor przycisku na podstawie stanu i czy jest anchor."""
        if (r, c) == self._anchor:
            # punkt zaczepienia - pomarańczowy (aktywny) lub czerwony (nieaktywny)
            if self._grid[r][c]:
                self._buttons[r][c].config(
                    bg=self._COLOR_ANCHOR_ACTIVE,
                    activebackground=self._COLOR_ANCHOR_ACTIVE_HOVER
                )
            else:
                self._buttons[r][c].config(
                    bg=self._COLOR_ANCHOR,
                    activebackground=self._COLOR_ANCHOR_HOVER
                )
        else:
            # normalny piksel - zielony lub szary
            self._buttons[r][c].config(
                bg=self._COLOR_ON if self._grid[r][c] else self._COLOR_OFF,
                activebackground=self._COLOR_HOVER_ON if self._grid[r][c] else self._COLOR_HOVER_OFF
            )

    def _refresh_all(self):
        for r in range(self._size):
            for c in range(self._size):
                self._refresh_button(r, c)

    # ─── zmiana rozmiary ──────────────────────────────────────────────────

    def _on_size_change(self, event=None):
        new_size = self._size_var.get()
        if new_size == self._size:
            return
        # zapamiętaj stary kernel, potem wycentruj w nowym
        old = self.get_kernel()
        self._init_grid(new_size)
        self._embed_old_kernel(old)
        self._refresh_all()
        # trigger callback
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    def _embed_old_kernel(self, old: np.ndarray):
        """Wkłada stary kernel (mniejszy lub większy) w środek nowej siatki."""
        n = self._size
        oh, ow = old.shape
        # oblicz offset żeby umieścić w środku
        or_ = (n - oh) // 2
        oc  = (n - ow) // 2
        for r in range(oh):
            for c in range(ow):
                nr, nc = r + or_, c + oc
                if 0 <= nr < n and 0 <= nc < n:
                    self._grid[nr][nc] = int(old[r, c])

    # ─── presets ──────────────────────────────────────────────────────────

    def _set_all(self, value: int):
        for r in range(self._size):
            for c in range(self._size):
                self._grid[r][c] = value
        self._refresh_all()
        # Don't trigger callback here - will be called by preset methods

    def _apply_preset_full(self):
        self._set_all(1)
        # trigger callback
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    def _apply_preset_cross(self):
        self._set_all(0)
        mid = self._size // 2
        for i in range(self._size):
            self._grid[mid][i] = 1
            self._grid[i][mid] = 1
        self._refresh_all()
        # trigger callback
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    def _apply_preset_x(self):
        self._set_all(0)
        n = self._size
        for i in range(n):
            self._grid[i][i] = 1
            self._grid[i][n - 1 - i] = 1
        self._refresh_all()
        # trigger callback
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    def _apply_preset_frame(self):
        self._set_all(0)
        n = self._size
        for i in range(n):
            self._grid[0][i]     = 1
            self._grid[n-1][i]   = 1
            self._grid[i][0]     = 1
            self._grid[i][n-1]   = 1
        self._refresh_all()
        # trigger callback
        if hasattr(self, '_on_change_callback') and self._on_change_callback:
            self._on_change_callback()

    # ─── output ───────────────────────────────────────────────────────────

    def set_on_change_callback(self, callback):
        """Ustawia callback wywoływany przy każdej zmianie kernela."""
        self._on_change_callback = callback

    def get_kernel(self) -> np.ndarray:
        """Zwraca bieżący element strukturyzujący jako np.ndarray uint8 (0/1)."""
        return np.array(self._grid, dtype=np.uint8)

    def get_anchor(self) -> tuple[int, int]:
        """Zwraca punkt zaczepienia (row, col)."""
        return self._anchor


# ─── główny dialog ────────────────────────────────────────────────────────────

class CustomMorphologyDialog:
    """
    Dialog: wybór operacji (erozja / dylacja) + edytor elementu strukturyzującego
    + live preview wyniku.

    Jeśli obraz nie jest binarny — wyskakuje messagebox z błędem i dialog
    się zamyka bez otwarcia okna.
    """

    def __init__(self, master, image: np.ndarray, app_manager, operation: str):
        """
        Parameters
        ----------
        master    : tk widget — okno rodzice
        image     : np.ndarray — aktywny obraz
        operation : "erode" | "dilate"
        """
        self.master = master
        self.image  = image
        self.operation = operation
        self.app_manager = app_manager
        self.on_result_callback = None   # lambda img: ...


        # ─── budowa okna ──────────────────────────────────────────────
        op_label = "Erozja" if operation == "erode" else "Dylacja"

        self.window = tk.Toplevel(master)
        self.window.title(f"{op_label} — Element strukturyzujący")
        self.window.geometry("540x1050")
        self.window.configure(bg="#2b2b2b")
        self.window.grab_set()
        self.window.focus_set()

        self._build_ui(op_label)

        # wstępny preview
        self._update_preview()

    # ─── UI ───────────────────────────────────────────────────────────────

    def _build_ui(self, op_label: str):
        # --- tytuł ---
        tk.Label(
            self.window, text=op_label,
            font=("Consolas", 14, "bold"), bg="#2b2b2b", fg="#fff"
        ).pack(pady=(12, 2))

        tk.Label(
            self.window,
            text="Zaprojektuj element strukturyzujący\n(lewy przycisk myszy: włącz/wyłącz • prawy przycisk: ustaw punkt zaczepienia)",
            font=("Consolas", 8), bg="#2b2b2b", fg="#888"
        ).pack(pady=(0, 6))

        # --- edytor ---
        self.editor = StructuringElementEditor(self.window)
        self.editor.pack(pady=(4, 6))
        # live preview przy każdej zmianie
        self.editor.set_on_change_callback(self._update_preview)

        # --- kontrolki brzegów ---
        border_frame = tk.LabelFrame(
            self.window, text=" Obsługa brzegów ",
            font=("Consolas", 9), bg="#2b2b2b", fg="#aaa",
            bd=1, relief=tk.GROOVE
        )
        border_frame.pack(fill=tk.X, padx=16, pady=(4, 4))

        # Typ brzegu
        border_row1 = tk.Frame(border_frame, bg="#2b2b2b")
        border_row1.pack(fill=tk.X, padx=8, pady=(6, 2))
        
        tk.Label(border_row1, text="Typ brzegu:", bg="#2b2b2b",
                 fg="#ccc", font=("Consolas", 9)).pack(side=tk.LEFT)
        
        self.border_type_var = tk.StringVar(value="BORDER_REFLECT")
        border_combo = ttk.Combobox(
            border_row1,
            textvariable=self.border_type_var,
            values=["BORDER_CONSTANT", "BORDER_REFLECT", "Wypełnienie wyniku stałą"],
            state='readonly',
            width=25
        )
        border_combo.pack(side=tk.LEFT, padx=8)
        border_combo.bind('<<ComboboxSelected>>', self._on_border_type_changed)

        # Wartość stała
        border_row2 = tk.Frame(border_frame, bg="#2b2b2b")
        border_row2.pack(fill=tk.X, padx=8, pady=(2, 6))
        
        tk.Label(border_row2, text="Wartość stała:", bg="#2b2b2b",
                 fg="#ccc", font=("Consolas", 9)).pack(side=tk.LEFT)
        
        self.border_value_var = tk.IntVar(value=0)
        self.border_value_combo = ttk.Combobox(
            border_row2,
            textvariable=self.border_value_var,
            values=[0, 255],
            state='disabled',
            width=10
        )
        self.border_value_combo.pack(side=tk.LEFT, padx=8)
        self.border_value_combo.bind('<<ComboboxSelected>>', lambda e: self._update_preview())

        # --- preview pane ---
        preview_frame = tk.LabelFrame(
            self.window, text=" Preview wyniku ",
            font=("Consolas", 9), bg="#2b2b2b", fg="#aaa",
            bd=1, relief=tk.GROOVE
        )
        preview_frame.pack(fill=tk.X, padx=16, pady=(4, 4))

        # Container for side-by-side layout
        preview_container = tk.Frame(preview_frame, bg="#2b2b2b")
        preview_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Left side: kernel preview
        kernel_frame = tk.Frame(preview_container, bg="#2b2b2b")
        kernel_frame.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(kernel_frame, text="Kernel:", bg="#2b2b2b",
                 fg="#aaa", font=("Consolas", 8)).pack(anchor=tk.W)
        self._kernel_label = tk.Label(kernel_frame, bg="#2b2b2b")
        self._kernel_label.pack()

        # Right side: image preview
        image_frame = tk.Frame(preview_container, bg="#2b2b2b")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(image_frame, text="Wynik:", bg="#2b2b2b",
                 fg="#aaa", font=("Consolas", 8)).pack(anchor=tk.W)
        self._preview_label = tk.Label(image_frame, bg="#2b2b2b")
        self._preview_label.pack()

        # info o błędzie (below both)
        self._error_label = tk.Label(
            preview_frame, text="", bg="#2b2b2b", fg="#f55",
            font=("Consolas", 8), wraplength=440, justify=tk.LEFT
        )
        self._error_label.pack(pady=(4, 4), padx=8)

        # --- przyciągi OK / Anuluj ---
        bottom = tk.Frame(self.window, bg="#2b2b2b")
        bottom.pack(fill=tk.X, pady=(8, 12), padx=16)

        tk.Button(
            bottom, text="✓  Zastosuj",
            command=self._apply,
            bg="#4CAF50", fg="#fff", relief=tk.FLAT,
            activebackground="#66BB6A", font=("Consolas", 10, "bold"),
            padx=18, pady=5, bd=0, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            bottom, text="✕  Anuluj",
            command=self.window.destroy,
            bg="#555", fg="#ddd", relief=tk.FLAT,
            activebackground="#666", font=("Consolas", 10),
            padx=14, pady=5, bd=0, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=4)

    # ─── preview ──────────────────────────────────────────────────────────

    def _on_border_type_changed(self, event=None):
        """Włącza/wyłącza combobox wartości w zależności od typu brzegu"""
        border_type = self.border_type_var.get()
        if border_type in ["BORDER_CONSTANT", "Wypełnienie wyniku stałą"]:
            self.border_value_combo.config(state='readonly')
        else:
            self.border_value_combo.config(state='disabled')
        # Update preview when border type changes
        self._update_preview()

    def _update_preview(self):
        self._error_label.config(text="")
        kernel = self.editor.get_kernel()
        anchor = self.editor.get_anchor()
        border_type = self.border_type_var.get()
        border_value = self.border_value_var.get()

        # --- malutki podgląd kernela ---
        self._show_kernel_preview(kernel, anchor)

        # --- próba obliczenia wyniku ---
        try:
            if self.operation == "erode":
                result = self.app_manager.custom_erode(
                    self.image, kernel, anchor, border_type, border_value
                )
            else:
                result = self.app_manager.custom_dilate(
                    self.image, kernel, anchor, border_type, border_value
                )
            self._last_result = result
            self._show_image_preview(result)
        except ValueError as e:
            self._error_label.config(text=str(e))
            self._last_result = None

    def _show_kernel_preview(self, kernel: np.ndarray, anchor: tuple[int, int]):
        """Rysuje malutki obraz kernela (białe = 1, czarne = 0, kolorowy = anchor)."""
        cell = 12
        h, w = kernel.shape
        vis = np.zeros((h * cell, w * cell, 3), dtype=np.uint8)
        
        for r in range(h):
            for c in range(w):
                if (r, c) == anchor:
                    # punkt zaczepienia - pomarańczowy (aktywny) lub czerwony (nieaktywny)
                    if kernel[r, c]:
                        vis[r*cell:(r+1)*cell, c*cell:(c+1)*cell] = [255, 136, 0]  # pomarańczowy
                    else:
                        vis[r*cell:(r+1)*cell, c*cell:(c+1)*cell] = [255, 50, 50]  # czerwony
                elif kernel[r, c]:
                    # aktywny piksel - biały
                    vis[r*cell:(r+1)*cell, c*cell:(c+1)*cell] = 255
                # nieaktywny pozostaje czarny
        
        # dodaj szare ramki między komórkami
        for i in range(h + 1):
            if i * cell < vis.shape[0]:
                vis[i*cell, :] = [128, 128, 128]
        for j in range(w + 1):
            if j * cell < vis.shape[1]:
                vis[:, j*cell] = [128, 128, 128]

        pil_img = Image.fromarray(vis, mode="RGB").resize(
            (w * cell, h * cell), Image.NEAREST
        )
        self._kernel_tk = ImageTk.PhotoImage(pil_img)
        self._kernel_label.config(image=self._kernel_tk)

    def _show_image_preview(self, result: np.ndarray):
        """
        Wyświetla obraz wynikowy, przeskalowany do ~200px (stały rozmiar).
        Zachowuje aspect ratio — zawsze wypełnia obszar preview.
        """
        target_size = 200  # stały rozmiar podglądu
        h, w = result.shape[:2]
        
        # Konwertuj 0/1 na 0/255 dla poprawnego wyświetlenia
        if result.max() <= 1:
            result = result * 255
        
        # oblicz skalę żeby dłuższa krawędź miała target_size
        scale = target_size / max(h, w)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        
        # upscale używa NEAREST dla obrazów binarnych (ostre krawędzie)
        # downscale też NEAREST żeby zachować ostre piksele
        pil_img = Image.fromarray(result, mode="L").resize((new_w, new_h), Image.NEAREST)
        self._preview_tk = ImageTk.PhotoImage(pil_img)
        self._preview_label.config(image=self._preview_tk)

    # ─── zastosowanie ─────────────────────────────────────────────────────

    def _apply(self):
        """Oblicza wynik i przekazuje do callback, potem zamyka okno."""
        kernel = self.editor.get_kernel()
        anchor = self.editor.get_anchor()
        border_type = self.border_type_var.get()
        border_value = self.border_value_var.get()
        
        try:
            if self.operation == "erode":
                result = self.app_manager.custom_erode(
                    self.image, kernel, anchor, border_type, border_value
                )
            else:
                result = self.app_manager.custom_dilate(
                    self.image, kernel, anchor, border_type, border_value
                )
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))
            return

        if self.on_result_callback:
            self.on_result_callback(result)

        self.window.destroy()