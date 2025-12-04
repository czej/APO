
from PIL import Image, ImageTk
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

from frontend.histogram import HistogramViewer
from backend import AppManager

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
        # tk.Button(button_frame, text="Wyświetl (800x600)", command=lambda: self.display_images(scale='fit')).pack(side=tk.LEFT, padx=5)
        # tk.Button(button_frame, text="Wyświetl (oryginalny)", command=lambda: self.display_images(scale='original')).pack(side=tk.LEFT, padx=5)
        # tk.Button(button_frame, text="Wyświetl (pełny ekran)", command=lambda: self.display_images(scale='fullscreen')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Pokaż histogram", command=self.show_histogram).pack(side=tk.LEFT, padx=5)

        # Obszar na obrazy
        # self.image_frame = tk.Frame(self.root)
        # self.image_frame.pack(fill=tk.BOTH, expand=True)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Obrazy", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")])
        if not file_path:
            return

        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("Błąd", "Nie udało się wczytać obrazu.")
            return

        self.images.append(img)
        self.display_single_image(img)

        if self.current_image is None:
            # self.set_current_image(img)
            self.current_image = img

    def save_image(self):
        if not self.images:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"),
                                                            ("BMP", "*.bmp"), ("TIFF", "*.tif")])
        if file_path:
            cv2.imwrite(file_path, self.images[-1])
            messagebox.showinfo("Sukces", f"Zapisano obraz: {file_path}")

    def duplicate_image(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij najpierw w okno obrazu, który chcesz zduplikować.")
            return

        dup = self.current_image.copy()
        self.images.append(dup)
        self.display_single_image(dup, scale='fit', title="Duplikat")

    # def display_images(self, scale='fit'):
    #     if not self.images:
    #         messagebox.showwarning("Brak obrazu", "Brak obrazów do wyświetlenia.")
    #         return

    #     for i, img in enumerate(self.images):
    #         img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #         if scale == 'fit':
    #             img_rgb = cv2.resize(img_rgb, (800, 600))
    #         elif scale == 'fullscreen':
    #             screen_w = self.root.winfo_screenwidth()
    #             screen_h = self.root.winfo_screenheight()
    #             img_rgb = cv2.resize(img_rgb, (screen_w, screen_h))
    #         elif scale == 'original':
    #             pass  # bez zmiany rozmiaru

    #         img_pil = Image.fromarray(img_rgb)
    #         img_tk = ImageTk.PhotoImage(img_pil)

    #         # NOWE OKNO DLA KAŻDEGO OBRAZU
    #         new_window = tk.Toplevel(self.root)
    #         new_window.title(f"Obraz {i+1}")

    #         if scale == 'fullscreen':
    #             new_window.attributes('-fullscreen', True)
    #             new_window.bind("<Escape>", lambda e: new_window.destroy())

    #         panel = tk.Label(new_window, image=img_tk)
    #         panel.image = img_tk  # przechowuj referencję!
    #         panel.pack()

    #         self.image_panels.append(panel)
    
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

        def on_click(event):
            print("hello")
            # self.set_current_image(img)
            self.current_image = img
            new_window.title((title or "Obraz") + " [AKTYWNY]")

        panel.bind("<Button-1>", on_click)
        new_window.bind("<Button-1>", on_click)


    def show_histogram(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return

        histograms = AppManager.calculate_histograms(self.current_image)
        HistogramViewer(self.root, histograms)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    app = ImageApp(root)
    root.mainloop()


# current_image decorator
# ustaw na domyslne pasek
# TODO: draggable + unififed pane lub grupowanie i wyciąganie całej grupy