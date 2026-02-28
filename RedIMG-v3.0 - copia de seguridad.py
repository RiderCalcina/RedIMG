import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import threading
import queue
from PIL import Image
from io import BytesIO
import customtkinter as ctk

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Constante de Versión
VERSION = "3.1.0"

class CTKToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        # Obtener posición del widget
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
        y += self.widget.winfo_rooty() + self.widget.winfo_height() + 10 # 10px abajo

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{int(x)}+{int(y)}")
        self.tooltip_window.attributes("-topmost", True)
        
        label = tk.Label(
            self.tooltip_window, 
            text=self.text, 
            justify="left",
            background="#1c1c2b", 
            foreground="#FFFFFF",
            relief="solid", 
            borderwidth=1,
            font=("Arial", 9),
            padx=5,
            pady=2
        )
        label.pack()
        
        # Ajustar posición para centrar el tooltip respecto al widget
        self.tooltip_window.update_idletasks()
        tw = self.tooltip_window.winfo_width()
        tx = x - (tw // 2)
        self.tooltip_window.wm_geometry(f"+{int(tx)}+{int(y)}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class RedIMGApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"RedIMG v{VERSION}")
        self.root.geometry("300x170")
        self.root.resizable(False, False)
        
        # Paleta Midnight Navy
        self.BG_MAIN = "#14141e"
        self.ACCENT = "#F0971C"
        self.ACCENT_HOVER = "#ffa836"
        self.root.configure(fg_color=self.BG_MAIN)
        
        # Estado y Comunicación
        self.processing_queue = queue.Queue()
        self.is_processing = False
        self.webp_enabled = tk.BooleanVar(value=False)
        
        # Cargar Iconos e Imágenes
        self._load_resources()
        
        self.setup_ui()
        self.centrar_ventana(self.root)
        
        # Iniciar despachador de cola
        self.root.after(100, self.check_queue)
        
    def _load_resources(self):
        # Icono de ventana
        if os.path.exists("RedIMG.ico"):
            try:
                self.root.iconbitmap("RedIMG.ico")
            except Exception:
                pass
        
        # Imágenes para botones
        img_path = os.path.join(os.path.dirname(__file__), "img")
        try:
            path_galeria = os.path.join(img_path, "galeria.png")
            path_imagen = os.path.join(img_path, "imagen.png")
            
            if os.path.exists(path_galeria):
                pil_galeria = Image.open(path_galeria)
                self.icon_galeria = ctk.CTkImage(light_image=pil_galeria, dark_image=pil_galeria, size=(24, 24))
            else:
                self.icon_galeria = None
                
            if os.path.exists(path_imagen):
                pil_imagen = Image.open(path_imagen)
                self.icon_imagen = ctk.CTkImage(light_image=pil_imagen, dark_image=pil_imagen, size=(24, 24))
            else:
                self.icon_imagen = None
        except Exception as e:
            print(f"Error cargando imágenes: {e}")
            self.icon_galeria = None
            self.icon_imagen = None

    def setup_ui(self):
        # Barra de progreso
        self.progress = ctk.CTkProgressBar(
            self.root, 
            width=250, 
            progress_color=self.ACCENT, 
            fg_color="#0a0a0f",
            height=8
        )
        self.progress.set(0)
        self.progress.pack(pady=(15, 10))
        
        # Contenedor para botones side-by-side
        self.btns_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.btns_frame.pack(pady=(10, 5), fill="x", padx=40)

        # Botón Carpeta (Masa)
        self.btn_carpeta = ctk.CTkButton(
            self.btns_frame,
            text="",
            image=self.icon_galeria,
            command=self.on_select_folder,
            fg_color="transparent",
            hover_color="#8B0000",
            width=40,
            height=40,
            corner_radius=8
        )
        self.btn_carpeta.pack(side="left", expand=True, padx=10)
        CTKToolTip(self.btn_carpeta, "Redimensionar carpeta (Proceso en masa)")

        # Botón Archivo (Individual)
        self.btn_archivo = ctk.CTkButton(
            self.btns_frame,
            text="",
            image=self.icon_imagen,
            command=self.on_select_file,
            fg_color="transparent",
            hover_color="#8B0000",
            width=40,
            height=40,
            corner_radius=8
        )
        self.btn_archivo.pack(side="left", expand=True, padx=10)
        CTKToolTip(self.btn_archivo, "Redimensionar archivo (Individual)")

        # Checkbox WEBP (Minimalista)
        self.check_webp = ctk.CTkCheckBox(
            self.root,
            text="WEBP (Opt. Máx.)",
            variable=self.webp_enabled,
            font=("Arial", 11),
            checkbox_width=18,
            checkbox_height=18,
            border_width=2,
            fg_color=self.ACCENT,
            hover_color=self.ACCENT_HOVER,
            corner_radius=4
        )
        self.check_webp.pack(pady=(10, 15))

        # About Link
        self.lbl_about = ctk.CTkLabel(
            self.root,
            text="ABOUT",
            text_color="#15FF00",
            font=("Arial", 8, "bold"),
            cursor="hand2"
        )
        self.lbl_about.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)
        self.lbl_about.bind("<Button-1>", lambda e: self.mostrar_about())

    def centrar_ventana(self, ventana):
        ventana.update_idletasks()
        ancho = ventana.winfo_width()
        alto = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"+{x}+{y}")

    def check_queue(self):
        try:
            while True:
                msg = self.processing_queue.get_nowait()
                if msg[0] == "progress":
                    self.progress.set(msg[1])
                elif msg[0] == "done":
                    self.is_processing = False
                    messagebox.showinfo("Éxito", msg[1])
                    self.progress.set(0)
                elif msg[0] == "error":
                    messagebox.showerror("Error", msg[1])
                elif msg[0] == "warning":
                    messagebox.showwarning("Completado con avisos", msg[1])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def on_select_folder(self):
        if self.is_processing: return
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta con imágenes")
        if carpeta:
            self.is_processing = True
            threading.Thread(target=self.batch_process, args=(carpeta,), daemon=True).start()

    def on_select_file(self):
        if self.is_processing: return
        archivo = filedialog.askopenfilename(
            title="Seleccionar una imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("Todos", "*.*")]
        )
        if archivo:
            self.is_processing = True
            threading.Thread(target=self.single_process, args=(archivo,), daemon=True).start()

    # --- Lógica de procesamiento optimizada ---
    
    def corregir_orientacion(self, img):
        try:
            exif = img._getexif()
            if exif:
                orient = exif.get(274)
                if orient == 3: img = img.rotate(180, expand=True)
                elif orient == 6: img = img.rotate(270, expand=True)
                elif orient == 8: img = img.rotate(90, expand=True)
        except Exception: pass
        return img

    def preparar_imagen(self, img):
        img = self.corregir_orientacion(img)
        ancho, alto = img.size
        if max(ancho, alto) > 1500:
            escala = 1500 / max(ancho, alto)
            nuevo_tam = (int(ancho * escala), int(alto * escala))
            img = img.resize(nuevo_tam, Image.Resampling.LANCZOS)
        
        # Manejo de fondos para JPEG
        if not self.webp_enabled.get():
            if img.mode in ("RGBA", "P", "LA"):
                fondo = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P": img = img.convert("RGBA")
                elif img.mode == "LA": img = img.convert("RGBA")
                fondo.paste(img, mask=img.split()[-1])
                return fondo
            elif img.mode != "RGB":
                return img.convert("RGB")
        return img

    def optimizar_y_guardar(self, img, ruta_salida):
        is_webp = self.webp_enabled.get()
        ext = "WEBP" if is_webp else "JPEG"
        
        buffer = BytesIO()
        calidad = 95
        while calidad >= 10:
            buffer.seek(0)
            buffer.truncate()
            if ext == "JPEG":
                img.save(buffer, ext, quality=calidad, optimize=True, progressive=True, subsampling="4:2:0")
            else:
                img.save(buffer, ext, quality=calidad, method=6) # Method 6 es mejor compresión para WEBP
            
            if buffer.tell() <= 700 * 1024: break
            calidad -= 5
            
        with open(ruta_salida, "wb") as f:
            f.write(buffer.getvalue())

    def single_process(self, ruta):
        try:
            nombre = os.path.splitext(os.path.basename(ruta))[0]
            ext_final = ".webp" if self.webp_enabled.get() else ".jpg"
            salida = os.path.join(os.path.dirname(ruta), f"{nombre}_RedIMG{ext_final}")
            
            with Image.open(ruta) as img:
                img_proc = self.preparar_imagen(img)
                self.optimizar_y_guardar(img_proc, salida)
            
            self.processing_queue.put(("done", f"Imagen procesada como:\n{os.path.basename(salida)}"))
        except Exception as e:
            self.processing_queue.put(("error", str(e)))

    def batch_process(self, carpeta):
        try:
            formatos = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
            archivos = [f for f in os.listdir(carpeta) if os.path.splitext(f)[1].lower() in formatos]
            if not archivos:
                self.processing_queue.put(("done", "No hay imágenes compatibles."))
                return

            total = len(archivos)
            nombre_base = os.path.basename(carpeta) or "redimg"
            ext_final = ".webp" if self.webp_enabled.get() else ".jpg"
            errores = 0

            for i, archivo in enumerate(archivos, 1):
                ruta = os.path.join(carpeta, archivo)
                try:
                    with Image.open(ruta) as img:
                        img_proc = self.preparar_imagen(img)
                        salida = os.path.join(carpeta, f"{nombre_base}_{i:03d}{ext_final}")
                        self.optimizar_y_guardar(img_proc, salida)
                except Exception:
                    errores += 1
                self.processing_queue.put(("progress", i / total))

            if errores == 0:
                self.processing_queue.put(("done", f"¡Éxito! {total} imágenes redimensionadas."))
            else:
                self.processing_queue.put(("warning", f"Proceso terminado con {errores} errores de {total} archivos."))
        except Exception as e:
            self.processing_queue.put(("error", str(e)))

    def mostrar_about(self):
        about = ctk.CTkToplevel(self.root)
        about.title("About")
        about.geometry("300x155")
        about.resizable(False, False)
        about.configure(fg_color="#1c1c2b")
        about.overrideredirect(True)
        
        # Posicionar relativo a la ventana principal
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y()
        about.geometry(f"+{x}+{y}")
        
        btn_close = ctk.CTkButton(
            about, text="x", width=15, height=15, fg_color="#8B0000", hover_color="#FF0000",
            command=about.destroy, font=("Arial", 9, "bold")
        )
        btn_close.place(relx=0, rely=1, anchor="sw", x=5, y=-5)
        
        txt = (f"RedIMG Modern v{VERSION}\n\n"
               "Optimizador de imágenes de alto rendimiento.\n\n"
               "• Multithreading (UI Fluida)\n"
               "• Soporte WEBP & JPEG\n"
               "• Estética Midnight Navy")
        
        ctk.CTkLabel(about, text=txt, font=("Arial", 11), justify="left").pack(pady=15, padx=15, anchor="w")
        
        link = ctk.CTkLabel(about, text="www.qwertyaserty.com", text_color="#00BFFF", cursor="hand2", font=("Arial", 9, "underline"))
        link.place(relx=1, rely=1, anchor="se", x=-10, y=-5)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://qwertyaserty.com/"))

if __name__ == "__main__":
    app = RedIMGApp()
    app.root.mainloop()
