
from PIL import Image, ImageTk
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

from frontend.histogram import HistogramViewer
from lut import LutViewer

class ImageApp:
    def __init__(self, root):
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
        tk.Button(button_frame, text="Wyświetl (800x600)", command=lambda: self.display_images(scale='fit')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Wyświetl (oryginalny)", command=lambda: self.display_images(scale='original')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Wyświetl (pełny ekran)", command=lambda: self.display_images(scale='fullscreen')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Pokaż LUT", command=self.show_lut).pack(side=tk.LEFT, padx=5)
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

    def display_images(self, scale='fit'):
        if not self.images:
            messagebox.showwarning("Brak obrazu", "Brak obrazów do wyświetlenia.")
            return

        for i, img in enumerate(self.images):
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if scale == 'fit':
                img_rgb = cv2.resize(img_rgb, (800, 600))
            elif scale == 'fullscreen':
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                img_rgb = cv2.resize(img_rgb, (screen_w, screen_h))
            elif scale == 'original':
                pass  # bez zmiany rozmiaru

            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)

            # NOWE OKNO DLA KAŻDEGO OBRAZU
            new_window = tk.Toplevel(self.root)
            new_window.title(f"Obraz {i+1}")

            if scale == 'fullscreen':
                new_window.attributes('-fullscreen', True)
                new_window.bind("<Escape>", lambda e: new_window.destroy())

            panel = tk.Label(new_window, image=img_tk)
            panel.image = img_tk  # przechowuj referencję!
            panel.pack()

            self.image_panels.append(panel)
    
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

    #     # frame.bind("<Button-1>", on_click)

    #     # label.bind("<Button-1>", on_click)
    #     # new_window.bind("<Button-1>", on_click)

    # def display_single_image(self, img, scale='fit', title=None):
    #     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #     if scale == 'fit':
    #         img_rgb = cv2.resize(img_rgb, (800, 600))
    #     elif scale == 'fullscreen':
    #         screen_w = self.root.winfo_screenwidth()
    #         screen_h = self.root.winfo_screenheight()
    #         img_rgb = cv2.resize(img_rgb, (screen_w, screen_h))
    #     elif scale == 'original':
    #         pass  # bez zmian

    #     img_pil = Image.fromarray(img_rgb)
    #     img_tk = ImageTk.PhotoImage(img_pil)

    #     new_window = tk.Toplevel(self.root)
    #     new_window.title(title or f"Obraz {len(self.images)}")

    #     if scale == 'fullscreen':
    #         new_window.attributes('-fullscreen', True)
    #         new_window.bind("<Escape>", lambda e: new_window.destroy())

    #     frame = tk.Frame(new_window)
    #     frame.pack()

    #     panel = tk.Button(frame, image=img_tk, borderwidth=0, highlightthickness=0, relief="flat")
    #     panel.image = img_tk
    #     panel.pack()

    #     self.image_panels.append(panel)
    #     self.tk_images.append(img_tk)  # zabezpieczenie przed GC

    #     def on_click():
    #         print("Klik działa!")
    #         self.set_current_image(img)
    #         new_window.title((title or "Obraz") + " [AKTYWNY]")

    #     panel.config(command=on_click)

    @staticmethod
    def create_lut_equalization(img_channel):
        # img_channel: 2D numpy array uint8 (0-255)
        hist = cv2.calcHist([img_channel], [0], None, [256], [0,256]).flatten()
        cdf = hist.cumsum()
        cdf_normalized = cdf / cdf[-1]  # normalizacja do [0,1]
        lut = np.round(cdf_normalized * 255).astype(np.uint8)
        return lut
    
    @staticmethod
    def apply_lut(img, luts):
        # img: numpy array (H,W) lub (H,W,3)
        # luts: list z 1 lub 3 tablic LUT po 256 elementów
        if len(img.shape) == 2:  # mono
            return cv2.LUT(img, luts[0])
        elif len(img.shape) == 3 and len(luts) == 3:
            channels = cv2.split(img)
            out_channels = [cv2.LUT(ch, lut) for ch, lut in zip(channels, luts)]
            return cv2.merge(out_channels)
        else:
            raise ValueError("Nieprawidłowy obraz lub LUT")
        
    # def show_lut(self):
    #     if self.current_image is None:
    #         messagebox.showwarning("Brak aktywnego obrazu", "Najpierw kliknij obraz.")
    #         return

    #     img = self.current_image
    #     if len(img.shape) == 2:
    #         luts = [self.create_lut_equalization(img)]
    #     else:
    #         channels = cv2.split(img)
    #         luts = [self.create_lut_equalization(ch) for ch in channels]

    #     LutViewer(self.root, luts)

    def show_lut(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Najpierw kliknij obraz.")
            return

        img = self.current_image
        if len(img.shape) == 2:
            luts = [self.create_lut_equalization(img)]
        else:
            channels = cv2.split(img)
            luts = [self.create_lut_equalization(ch) for ch in channels]

        LutViewer(self.root, luts)

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
        if len(img.shape) == 2:
            # Obraz monochromatyczny
            # hist = cv2.calcHist([img], [0], None, [256], [0,256])
            # return [hist.flatten()]
            hist = np.zeros(256, dtype=int)
            for pixel in img.flat:
                hist[pixel] += 1
            return [hist]
        elif len(img.shape) == 3 and img.shape[2] == 3:
            # Obraz kolorowy (BGR)
            # chans = cv2.split(img)
            # hists = []
            # for ch in chans:
                
            #     hist = cv2.calcHist([ch], [0], None, [256], [0,256])
            #     hists.append(hist.flatten())
            # return hists
            hists = [np.zeros(256, dtype=int) for _ in range(3)]
            for row in img:
                for pixel in row:
                    b, g, r = pixel
                    hists[0][b] += 1
                    hists[1][g] += 1
                    hists[2][r] += 1
            return hists
        else:
            raise ValueError("Nieobsługiwany format obrazu")

    def show_histogram(self):
        if self.current_image is None:
            messagebox.showwarning("Brak aktywnego obrazu", "Kliknij obraz aby go aktywować.")
            return

        histograms = self.calculate_histograms(self.current_image)
        HistogramViewer(self.root, histograms)




if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    app = ImageApp(root)
    root.mainloop()


# current_image decorator
# ustaw na domyslne pasek