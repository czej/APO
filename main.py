
import cv2
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

from frontend.histogram import HistogramViewer
from backend.AppManager import AppManager

class ImageApp:
    def __init__(self, root):
        self.app_manager = AppManager()

        self.root = root
        self.root.title("Przeglądarka Obrazów (OpenCV + Tkinter)")
        self.images = []
        self.image_panels = []
        self.current_image = None

        self.tk_images = []
        self.init_ui()

    def init_ui(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, pady=10)

        tk.Button(button_frame, text="Wczytaj obraz", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Zapisz obraz", command=self.save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Duplikuj obraz", command=self.duplicate_image).pack(side=tk.LEFT, padx=5)
        # TODO: show dialog if current_image is None
        tk.Button(button_frame, text="Wyświetl (800x600)", command=lambda: self.display_single_image(self.current_image, scale='fit')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Wyświetl (oryginalny)", command=lambda: self.display_single_image(self.current_image, scale='original')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Wyświetl (pełny ekran)", command=lambda: self.display_single_image(self.current_image, scale='fullscreen')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Pokaż histogram", command=self.show_histogram).pack(side=tk.LEFT, padx=5)

        # Obszar na obrazy
        # self.image_frame = tk.Frame(self.root)
        # self.image_frame.pack(fill=tk.BOTH, expand=True)

        # Nowy rząd przycisków dla operacji punktowych
        operations_frame = tk.Frame(self.root)
        operations_frame.pack(side=tk.TOP, pady=5)
        
        tk.Button(operations_frame, text="Negacja", command=self.apply_negate).pack(side=tk.LEFT, padx=5)
        tk.Button(operations_frame, text="Posteryzacja", command=self.apply_posterize).pack(side=tk.LEFT, padx=5)
        tk.Button(operations_frame, text="Progowanie binarne", command=self.apply_threshold_binary).pack(side=tk.LEFT, padx=5)
        tk.Button(operations_frame, text="Progowanie z poziomami", command=self.apply_threshold_with_levels).pack(side=tk.LEFT, padx=5)

        tk.Button(operations_frame, text="Rozciąganie histogramu", command=self.apply_stretch_histogram).pack(side=tk.LEFT, padx=5)
        tk.Button(operations_frame, text="Equalizacja histogramu", command=self.apply_equalize_histogram).pack(side=tk.LEFT, padx=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Obrazy", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")])
        if not file_path:
            return

        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        # Remove alpha channel if exists
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # ? TODO: to samo dla == 2
        # elif len(img.shape) == 3 and img.shape[2] == 2:
        #     img = cv2.cvtColor(img, cv2.COLOR_GRAY)

        # Convert to grayscale (this 2nd is needed only)
        # if len(img.shape) == 3 and img.shape[2] == 4:
        #     # RGBA -> Grayscale
        #     img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        # elif len(img.shape) == 3 and img.shape[2] == 3:
        #     # RGB -> Grayscale (jeśli wszystkie kanały równe)
        #     if np.all(img[:,:,0] == img[:,:,1]) and np.all(img[:,:,1] == img[:,:,2]):
        #         img = img[:,:,0]




        print(f"Shape: {img.shape}")
        print(f"Dtype: {img.dtype}")
        if img is None:
            messagebox.showerror("Błąd", "Nie udało się wczytać obrazu.")
            return

        self.images.append(img)
        self.display_single_image(img)

    def save_image(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij najpierw w okno obrazu, który chcesz zapisać.")
            return

        file_path = filedialog.asksaveasfilename(filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"),
                                                            ("BMP", "*.bmp"), ("TIFF", "*.tif")])
        if file_path:
            cv2.imwrite(file_path, self.current_image)
            messagebox.showinfo("Sukces", f"Zapisano obraz: {file_path}")

    def duplicate_image(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij najpierw w okno obrazu, który chcesz zduplikować.")
            return

        dup = self.current_image.copy()
        self.images.append(dup)
        self.display_single_image(dup, scale='fit', title="Duplikat")

    
    def display_single_image(self, img, scale='fit', title=None):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if scale == 'fit':
            img_rgb = cv2.resize(img_rgb, (800, 600))
        elif scale == 'fullscreen':
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            img_rgb = cv2.resize(img_rgb, (screen_w, screen_h))
        elif scale == 'original':
            pass  # bez zmian

        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)

        new_window = tk.Toplevel(self.root)
        new_window.title(title or f"Obraz {len(self.images)}")

        if scale == 'fullscreen':
            new_window.attributes('-fullscreen', True)
            new_window.bind("<Escape>", lambda e: new_window.destroy())

        frame = tk.Frame(new_window)
        frame.pack()

        panel = tk.Label(frame, image=img_tk)
        panel.image = img_tk
        panel.pack()
        panel.focus_set()

        self.image_panels.append(panel)

        def on_focus(event):
            if event.widget == new_window:
                print("hello")
                self._set_current_image(img)
                # new_window.title((title or "Obraz") + " [AKTYWNY]")

        new_window.bind("<FocusIn>", on_focus)


    def show_histogram(self):
        if self.current_image is None:
            # TODO: standardize this msg in decorator, Kliknij lub wczytaj
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return

        histograms = AppManager.calculate_histograms(self.current_image)
        HistogramViewer(self.root, histograms)

    def apply_negate(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return
        
        if len(self.current_image.shape) != 2:
            messagebox.showerror("Błąd", "Operacja dostępna tylko dla obrazów w odcieniach szarości")
            return
        
        result = self.app_manager.apply_negate(self.current_image)
        self.images.append(result)
        self.display_single_image(result, title="Negacja")

    def apply_posterize(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return
        
        if len(self.current_image.shape) != 2:
            messagebox.showerror("Błąd", "Operacja dostępna tylko dla obrazów w odcieniach szarości")
            return
        
        # Dialog do wprowadzenia liczby poziomów
        dialog = tk.Toplevel(self.root)
        dialog.title("Posteryzacja")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="Podaj liczbę poziomów szarości (2-256):").pack(pady=10)
        
        levels_var = tk.IntVar(value=8)
        spinbox = tk.Spinbox(dialog, from_=2, to=256, textvariable=levels_var, width=10)
        spinbox.pack(pady=5)
        
        def apply():
            try:
                levels = levels_var.get()
                result = self.app_manager.apply_posterize(self.current_image, levels)
                self.images.append(result)
                self.display_single_image(result, title=f"Posteryzacja ({levels} poziomów)")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Błąd", str(e))
        
        tk.Button(dialog, text="Zastosuj", command=apply).pack(pady=10)
        tk.Button(dialog, text="Anuluj", command=dialog.destroy).pack(pady=5)

    def apply_threshold_binary(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return
        
        if len(self.current_image.shape) != 2:
            messagebox.showerror("Błąd", "Operacja dostępna tylko dla obrazów w odcieniach szarości")
            return
        
        self._threshold_dialog("binarne")

    def apply_threshold_with_levels(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return
        
        if len(self.current_image.shape) != 2:
            messagebox.showerror("Błąd", "Operacja dostępna tylko dla obrazów w odcieniach szarości")
            return
        
        self._threshold_dialog("z poziomami")

    def _threshold_dialog(self, mode):
        # Dialog z histogramem i sliderem do wyboru progu
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Progowanie {mode}")
        dialog.geometry("600x500")
        
        # Histogram
        histogram_stats = self.app_manager.calculate_histograms(self.current_image)
        hist_data = histogram_stats[0].histogram  # Pobierz czysty histogram z namedtuple
        
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        fig = Figure(figsize=(6, 3))
        ax = fig.add_subplot(111)
        x = np.arange(256)
        ax.bar(x, hist_data, color='gray', width=1.0, alpha=0.7)
        ax.set_title("Histogram")
        ax.set_xlabel("Wartość piksela")
        ax.set_ylabel("Liczba wystąpień")
        ax.set_xlim(0, 255)
        
        # Linia progu
        threshold_line = ax.axvline(x=128, color='r', linestyle='--', linewidth=2, label='Próg')
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=dialog)
        canvas.get_tk_widget().pack(pady=10)
        
        # Slider
        threshold_var = tk.IntVar(value=128)
        
        def update_threshold(val):
            threshold = int(float(val))
            threshold_line.set_xdata([threshold, threshold])
            canvas.draw()
        
        tk.Label(dialog, text="Wybierz próg (0-255):").pack(pady=5)
        slider = tk.Scale(dialog, from_=0, to=255, orient=tk.HORIZONTAL, 
                        variable=threshold_var, command=update_threshold, length=400)
        slider.pack(pady=5)
        
        def apply():
            threshold = threshold_var.get()
            if mode == "binarne":
                result = self.app_manager.apply_threshold_binary(self.current_image, threshold)
                title = f"Progowanie binarne (próg={threshold})"
            else:
                result = self.app_manager.apply_threshold_with_levels(self.current_image, threshold)
                title = f"Progowanie z poziomami (próg={threshold})"
            
            self.images.append(result)
            self.display_single_image(result, title=title)
            dialog.destroy()
        
        tk.Button(dialog, text="Zastosuj", command=apply).pack(pady=10)
        tk.Button(dialog, text="Anuluj", command=dialog.destroy).pack(pady=5)

    def _set_current_image(self, img):
        self.current_image = img

    def apply_stretch_histogram(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return
        
        if len(self.current_image.shape) != 2:
            messagebox.showerror("Błąd", "Operacja dostępna tylko dla obrazów w odcieniach szarości")
            return
        
        # Dialog do wyboru przesycenia
        dialog = tk.Toplevel(self.root)
        dialog.title("Rozciąganie histogramu")
        dialog.geometry("400x200")
        
        tk.Label(dialog, text="Wybierz procent przesycenia (0-5%):").pack(pady=10)
        tk.Label(dialog, text="0% = bez przesycenia, 5% = maksymalne przesycenie").pack(pady=5)
        
        saturation_var = tk.DoubleVar(value=0)
        
        frame = tk.Frame(dialog)
        frame.pack(pady=10)
        
        tk.Radiobutton(frame, text="Bez przesycenia (0%)", variable=saturation_var, value=0).pack(anchor=tk.W)
        tk.Radiobutton(frame, text="1% przesycenia", variable=saturation_var, value=1).pack(anchor=tk.W)
        tk.Radiobutton(frame, text="2% przesycenia", variable=saturation_var, value=2).pack(anchor=tk.W)
        tk.Radiobutton(frame, text="5% przesycenia (max)", variable=saturation_var, value=5).pack(anchor=tk.W)
        
        def apply():
            try:
                saturation = saturation_var.get()
                result = self.app_manager.apply_stretch_histogram(self.current_image, saturation)
                self.images.append(result)
                title = f"Rozciąganie histogramu ({saturation}% przesycenia)"
                self.display_single_image(result, title=title)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Błąd", str(e))
        
        tk.Button(dialog, text="Zastosuj", command=apply).pack(pady=10)
        tk.Button(dialog, text="Anuluj", command=dialog.destroy).pack(pady=5)

    def apply_equalize_histogram(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return
        
        if len(self.current_image.shape) != 2:
            messagebox.showerror("Błąd", "Operacja dostępna tylko dla obrazów w odcieniach szarości")
            return
        
        result = self.app_manager.apply_equalize_histogram(self.current_image)
        self.images.append(result)
        self.display_single_image(result, title="Equalizacja histogramu")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    app = ImageApp(root)
    root.mainloop()


# tytuł nowych okienek
# current_image decorator == current_image is not None
# ustaw na domyslne pasek
# TODO: draggable + unififed pane lub grupowanie i wyciąganie całej grupy
# or minimize / bring back all the windows at once button
# or macbook style stickybar
# TODO: what if current image was closed
# TODO: nie nadpisuj current_image przy load image