"""
RedIMG - Modern Image Optimizer
Optimización y redimensionamiento masivo de imágenes con procesamiento paralelo.
"""

import os
import sys
import math
import random
import logging
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List
import webbrowser
import threading
import queue
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import ctypes

try:
    import windnd
except ImportError:
    windnd = None


VERSION = "3.5.3"

MAX_SIZE = 1600
MAX_WEIGHT_KB = 780


def setup_logging() -> logging.Logger:
    """Configura el sistema de logging para la aplicación."""
    logger = logging.getLogger("RedIMG")
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        file_handler = logging.FileHandler("redimg.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_max_threads() -> int:
    """Retorna el número máximo de hilos disponibles."""
    return os.cpu_count() or 4


logger = setup_logging()


class RedIMGApp:
    """Aplicación principal de RedIMG."""
    
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
    
    def __init__(self) -> None:
        logger.info("Iniciando RedIMG v%s", VERSION)
        
        self.root = ttk.Window(title="RedIMG", themename="darkly")
        self.root.withdraw()
        self.root.resizable(False, False)
        self.root.geometry("300x125")
        
        # 1. MODIFICAR EL MAPA DE COLORES DEL TEMA (Fuerza bruta para negro absoluto)
        # Esto cambia la definición base del tema darkly
        self.root.style.colors.bg = "#000000"
        self.root.style.colors.inputbg = "#000000"
        self.root.style.colors.selectbg = "#000000"
        
        # 2. Forzar negro absoluto en el root
        self.root.configure(background="#000000")
        
        self.BG_MAIN = "#000000"
        self.ACCENT = "#000000"
        
        # Forzar estilos globales a negro absoluto
        self.root.style.configure(".", background="#000000", fieldbackground="#000000")
        self.root.style.configure("TFrame", background="#000000")
        self.root.style.configure("TLabel", background="#000000", foreground="#FFFFFF")
        # Estilo para la barra de progreso (Celeste Eléctrico)
        self.root.style.configure(
            "info.Horizontal.TProgressbar", 
            thickness=8, 
            borderwidth=0, 
            troughcolor="#000000",
            background="#00FFFF"  # Celeste eléctrico
        )
        
        self._setup_dark_mode()
        
        self.processing_queue: queue.Queue = queue.Queue()
        self.is_processing = False
        self.cancel_requested = False
        
        if os.path.exists("RedIMG.ico"):
            try:
                self.root.iconbitmap("RedIMG.ico")
            except Exception:
                pass
        
        if windnd:
            windnd.hook_dropfiles(self.root, func=self.on_drop)
        else:
            logger.warning("windnd no disponible - Drag & Drop deshabilitado")
        
        self.setup_ui()
        self.centrar_ventana(self.root)
        
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        
        self.root.after(100, self.check_queue)
        self.root.after(500, lambda: setattr(self.rain_system, "running", True))
        
        logger.info("RedIMG iniciado correctamente")
    
    def _setup_dark_mode(self) -> None:
        """Configura el modo oscuro en Windows."""
        try:
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(1)), 4
            )
        except Exception:
            pass
    def setup_ui(self) -> None:
        """Configura la interfaz de usuario."""
        # Forzamos negro puro y eliminamos cualquier borde residual
        self.canvas_bg = tk.Canvas(
            self.root, 
            highlightthickness=0, 
            bg="#000000",
            background="#000000",
            bd=0, 
            relief="flat"
        )
        self.canvas_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.w_area = 300
        self.h_area = 129
        
        self.rain_system = PixelRain(self.root, self.canvas_bg, "#000000", self)
        self.rain_system.pre_create_particles()
        
        self.progress = ttk.Progressbar(
            self.root,
            bootstyle="info",
            maximum=100,
            value=0
        )
        # REPOSICIONAMIENTO: Un poco más arriba para asegurar que no se corte por el borde inferior
        self.canvas_bg.create_window(
            150, 118, window=self.progress, width=300, tags="ui"
        )
        
        self.id_lbl_resize = self.canvas_bg.create_text(
            150, 60,
            text="Arrastra y suelta carpetas e imágenes aquí",
            fill="#888888",
            font=("Arial", 9, "bold"),
            anchor="center",
            justify="center",
            tags="ui"
        )
        
        def on_canvas_click(event: tk.Event) -> None:
            tags = self.canvas_bg.gettags("current")
            if "ui" not in tags:
                self.on_select_file()
        
        self.canvas_bg.bind("<Button-1>", on_canvas_click)
        
        self.btn_about = ttk.Button(
            self.root,
            text="ABOUT",
            command=self.mostrar_about
        )
        
        font_micro = ("Arial", 7, "bold")
        self.root.style.configure(
            "Micro.TButton",
            font=font_micro,
            padding=1,
            background="#111111",
            foreground="#BBBBBB",
            borderwidth=0
        )
        self.root.style.map(
            "Micro.TButton",
            background=[("active", "#222222")],
            foreground=[("active", "#FFFFFF")]
        )
        self.btn_about.configure(style="Micro.TButton", cursor="hand2")
        self.canvas_bg.create_window(
            280, 10, window=self.btn_about, anchor="center", tags="ui"
        )
        

    
    def centrar_ventana(self, ventana: tk.Tk) -> None:
        """Centra la ventana en la pantalla."""
        ventana.update_idletasks()
        ancho = ventana.winfo_width()
        alto = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"+{x}+{y}")
    
    def check_queue(self) -> None:
        """Procesa mensajes de la cola de procesamiento."""
        try:
            while True:
                msg = self.processing_queue.get_nowait()
                if msg[0] == "progress":
                    self.progress["value"] = msg[1] * 100
                elif msg[0] == "done":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.progress["value"] = 0
                    self.notificar_usuario("Éxito", msg[1], "success")
                elif msg[0] == "error":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.notificar_usuario("Error", msg[1], "danger")
                elif msg[0] == "warning":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.notificar_usuario("Aviso", msg[1], "warning")
                elif msg[0] == "cancelled":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.progress["value"] = 0
                    self.notificar_usuario("Cancelado", msg[1], "info")
        except queue.Empty:
            pass
        finally:
            if not self.is_processing and not self.rain_system.running:
                self.rain_system.running = True
            self.root.after(30, self.check_queue)
    
    def notificar_usuario(self, titulo: str, mensaje: str, tipo: str = "info") -> None:
        """Muestra una notificación personalizada compacta que no bloquea la UI central."""
        notif = tk.Toplevel(self.root)
        notif.withdraw()
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)
        notif.configure(background="#111111")
        
        # Heredar icono de la ventana principal
        if os.path.exists("RedIMG.ico"):
            try:
                notif.iconbitmap("RedIMG.ico")
            except:
                pass

        # Colores según tipo
        colors = {
            "success": "#00FF99",
            "danger": "#FF3333",
            "warning": "#FFCC00",
            "info": "#00CCFF"
        }
        accent = colors.get(tipo, "#00CCFF")

        # Contenedor con borde de color
        frame = tk.Frame(notif, background="#111111", highlightbackground=accent, highlightthickness=1)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text=mensaje, font=("Arial", 9, "bold"),
            foreground="#FFFFFF", background="#111111",
            wraplength=250, pady=10, padx=15
        ).pack()

        # Posicionar justo debajo de la ventana principal
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        
        notif.update_idletasks()
        notif_w = notif.winfo_width()
        notif_h = notif.winfo_height()
        
        # Centrado respecto a la principal pero abajo
        pos_x = root_x + (root_w // 2) - (notif_w // 2)
        pos_y = root_y + root_h + 5
        
        notif.geometry(f"+{pos_x}+{pos_y}")
        notif.deiconify()
        
        # Se cierra sola después de 4 segundos
        self.root.after(4000, notif.destroy)

    def on_select_file(self) -> None:
        """Abre el selector de archivos."""
        if self.is_processing:
            return
        
        archivos = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("Todos", "*.*")
            ]
        )
        
        if archivos:
            self._start_processing(archivos)
    
    def on_drop(self, filenames: tuple) -> None:
        """Maneja el evento de arrastrar y soltar archivos."""
        if self.is_processing:
            return
        
        rutas_validas = []
        
        for f in filenames:
            if isinstance(f, bytes):
                f = f.decode("mbcs")
            
            if os.path.isfile(f):
                ext = os.path.splitext(f)[1].lower()
                if ext in self.SUPPORTED_FORMATS:
                    rutas_validas.append(f)
            elif os.path.isdir(f):
                for r, _, files in os.walk(f):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in self.SUPPORTED_FORMATS:
                            rutas_validas.append(os.path.join(r, file))
        
        if rutas_validas:
            self._start_processing(rutas_validas)
    
    def _start_processing(self, rutas: list) -> None:
        """Inicia el procesamiento de archivos."""
        self.is_processing = True
        self.cancel_requested = False
        self.rain_system.running = False
        logger.info("Iniciando procesamiento de %d archivos", len(rutas))
        threading.Thread(
            target=self.process_multiple_files,
            args=(rutas,),
            daemon=True
        ).start()
    
    def request_cancel(self) -> None:
        """Solicita la cancelación del procesamiento."""
        self.cancel_requested = True
        logger.info("Cancelación solicitada por el usuario")
    
    def corregir_orientacion(self, img: Image.Image) -> Image.Image:
        """Corrige la orientación de la imagen según los metadatos EXIF."""
        try:
            exif = img._getexif()
            if exif:
                orient = exif.get(274)
                if orient == 3:
                    img = img.rotate(180, expand=True)
                elif orient == 6:
                    img = img.rotate(270, expand=True)
                elif orient == 8:
                    img = img.rotate(90, expand=True)
        except Exception:
            pass
        return img
    
    def preparar_imagen(
        self,
        img: Image.Image,
        max_size: Optional[int] = None
    ) -> Image.Image:
        """
        Prepara la imagen: corrige orientación, redimensiona y convierte a RGB.
        
        Args:
            img: Imagen PIL a preparar
            max_size: Tamaño máximo del lado más largo
            
        Returns:
            Imagen procesada en modo RGB
        """
        if max_size is None:
            max_size = MAX_SIZE
        
        img = self.corregir_orientacion(img)
        ancho, alto = img.size
        
        if max(ancho, alto) > max_size:
            escala = max_size / max(ancho, alto)
            nuevo_tam = (int(ancho * escala), int(alto * escala))
            img = img.resize(nuevo_tam, Image.Resampling.LANCZOS)
            logger.debug("Imagen redimensionada a %dx%d", *nuevo_tam)
        
        if img.mode in ("RGBA", "P", "LA"):
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            elif img.mode == "LA":
                img = img.convert("RGBA")
            fondo.paste(img, mask=img.split()[-1])
            return fondo
        elif img.mode != "RGB":
            return img.convert("RGB")
        return img
    
    def optimizar_y_guardar(
        self,
        img: Image.Image,
        ruta_salida: str,
        max_weight_kb: Optional[int] = None
    ) -> None:
        """
        Optimiza la imagen usando búsqueda binaria para encontrar el peso ideal.
        
        Args:
            img: Imagen PIL a optimizar
            ruta_salida: Ruta donde se guardará la imagen
            max_weight_kb: Peso máximo en KB
        """
        if max_weight_kb is None:
            max_weight_kb = MAX_WEIGHT_KB
        
        max_size_bytes = max_weight_kb * 1024
        
        buffer_init = BytesIO()
        img.save(
            buffer_init,
            "JPEG",
            quality=95,
            optimize=True,
            progressive=True,
            subsampling="4:2:0"
        )
        
        if buffer_init.tell() <= max_size_bytes:
            with open(ruta_salida, "wb") as f:
                f.write(buffer_init.getvalue())
            buffer_init.close()
            return
        
        low, high = 10, 90
        final_buffer = buffer_init
        
        try:
            while low <= high:
                mid = (low + high) // 2
                buffer = BytesIO()
                img.save(
                    buffer,
                    "JPEG",
                    quality=mid,
                    optimize=True,
                    progressive=True,
                    subsampling="4:2:0"
                )
                
                if buffer.tell() <= max_size_bytes:
                    if final_buffer and final_buffer != buffer_init:
                        final_buffer.close()
                    final_buffer = buffer
                    low = mid + 1
                else:
                    buffer.close()
                    high = mid - 1
            
            with open(ruta_salida, "wb") as f:
                f.write(final_buffer.getvalue())
        finally:
            if final_buffer:
                final_buffer.close()
            if buffer_init and buffer_init != final_buffer:
                buffer_init.close()
    
    def process_multiple_files(self, rutas: list) -> None:
        """
        Procesa múltiples archivos de imagen en paralelo.
        
        Args:
            rutas: Lista de rutas de imágenes a procesar
        """
        try:
            total = len(rutas)
            if total == 0:
                return
            
            base_carpeta = os.path.dirname(rutas[0])
            salida_dir = os.path.join(base_carpeta, "RedIMG")
            os.makedirs(salida_dir, exist_ok=True)
            
            errores = []
            max_threads = get_max_threads()
            max_size = MAX_SIZE
            max_weight = MAX_WEIGHT_KB
            
            logger.info(
                "Procesando %d imágenes con %d hilos (max_size=%d, max_weight=%dKB)",
                total, max_threads, max_size, max_weight
            )
            
            def process_item(item: tuple) -> tuple:
                """Procesa un archivo individual. Retorna (éxito, nombre, error)."""
                if self.cancel_requested:
                    return (False, "", "Cancelado por usuario")
                
                idx, ruta = item
                try:
                    nombre_final = (
                        f"RedIMG_{idx:03d}.jpg"
                        if total > 1
                        else f"{os.path.splitext(os.path.basename(ruta))[0]}_RedIMG.jpg"
                    )
                    salida = os.path.join(salida_dir, nombre_final)
                    
                    with Image.open(ruta) as img:
                        img_proc = self.preparar_imagen(img, max_size)
                        self.optimizar_y_guardar(img_proc, salida, max_weight)
                    
                    logger.debug("Procesado: %s -> %s", ruta, nombre_final)
                    return (True, nombre_final, None)
                except Exception as e:
                    logger.error("Error procesando %s: %s", ruta, e)
                    return (False, os.path.basename(ruta), str(e))
            
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                items = list(enumerate(rutas, 1))
                futures = {executor.submit(process_item, item): item for item in items}
                completados = 0
                
                for future in as_completed(futures):
                    if self.cancel_requested:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    success, nombre, error = future.result()
                    if not success:
                        errores.append(f"{nombre}: {error}" if error else nombre)
                    
                    completados += 1
                    self.processing_queue.put(("progress", completados / total))
            
            if self.cancel_requested:
                self.processing_queue.put(
                    ("cancelled", f"Procesamiento cancelado.\n{completados} de {total} imágenes procesadas.")
                )
                return
            
            if not errores:
                msg = (
                    "¡Éxito! Todas las imágenes procesadas."
                    if total > 1
                    else "Imagen procesada con éxito."
                )
                msg += "\n\nLas fotos están en la carpeta /RedIMG"
                self.processing_queue.put(("done", msg))
                logger.info("Procesamiento completado: %d/%d imágenes", total, total)
            else:
                error_summary = "\n".join(errores[:10])
                if len(errores) > 10:
                    error_summary += f"\n...y {len(errores) - 10} errores más"
                self.processing_queue.put(
                    ("warning", f"Terminado con {len(errores)} errores.\n\n{error_summary}\n\nRevisa la carpeta /RedIMG")
                )
                logger.warning("Procesamiento completado con errores: %d/%d", total - len(errores), total)
        
        except Exception as e:
            logger.exception("Error en process_multiple_files: %s", e)
            self.processing_queue.put(("error", str(e)))
    
    def mostrar_about(self) -> None:
        """Muestra la ventana Acerca de."""
        try:
            if hasattr(self, "about_window") and self.about_window and self.about_window.winfo_exists():
                self.about_window.lift()
                return
            
            self.about_window = ttk.Toplevel(self.root)
            self.about_window.title("About")
            self.about_window.geometry("300x140")
            self.about_window.resizable(False, False)
            self.about_window.configure(background="#000000")
            self.about_window.overrideredirect(True)
            # Forzar estilo para las labels de la ventana about
            self.root.style.configure("About.TLabel", background="#000000", foreground="#B0B0B0")
            
            self.root.update_idletasks()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_w = self.root.winfo_width()
            
            x = main_x + main_w + 5
            y = main_y
            self.about_window.geometry(f"+{int(x)}+{int(y)}")
            self.about_window.geometry("300x140")
            
            self.root.after(200, self._set_about_focus)
            
            txt = (
                f"RedIMG v{VERSION}\n\n"
                "Redimencion y optimización rápida de imágenes.\n\n"
                "Arrastra y suelta tus imágenes o carpetas para procesarlas,\n"
                "o haz clic en la interfaz para seleccionarlas."
            )
            
            lbl_info = ttk.Label(
                self.about_window,
                text=txt,
                font=("Arial", 9),
                wraplength=280,
                style="About.TLabel",
                justify="center"
            )
            lbl_info.pack(pady=(20, 0), padx=10)
            
            link = ttk.Label(
                self.about_window,
                text="www.qwertyaserty.com",
                cursor="hand2",
                foreground="#00FF99",
                background="#000000",
                font=("Arial", 9, "underline")
            )
            link.pack(side="top", anchor="center", padx=10, pady=(15, 0))
            link.bind("<Button-1>", lambda e: webbrowser.open("https://qwertyaserty.com/"))
        
        except Exception as e:
            logger.error("Error al mostrar About: %s", e)
            messagebox.showerror("Error", f"No se pudo abrir About:\n{e}")
    

    def cerrar_about(self, event: Optional[tk.Event] = None) -> None:
        """Cierra la ventana Acerca de."""
        if hasattr(self, "about_window") and self.about_window and self.about_window.winfo_exists():
            self.about_window.destroy()
            self.about_window = None
    
    def _set_about_focus(self) -> None:
        """Configura el foco en la ventana About."""
        if hasattr(self, "about_window") and self.about_window and self.about_window.winfo_exists():
            try:
                self.about_window.focus_set()
                self.about_window.bind("<FocusOut>", self.cerrar_about)
            except Exception:
                pass


class Particle:
    """Partícula optimizada para el efecto de lluvia de píxeles."""
    
    def __init__(
        self,
        canvas: tk.Canvas,
        w: int,
        h: int,
        colors: List[str],
        cached_image: Optional[tk.PhotoImage] = None
    ) -> None:
        self.canvas = canvas
        self.w = w
        self.h = h
        self.radius = 1
        self.colors = colors
        self.cached_image = cached_image
        self.reset(initial=True)
        
        if cached_image:
            self.id = self.canvas.create_image(
                self.x, self.y,
                image=cached_image,
                anchor="nw",
                tags="rain"
            )
        else:
            self.id = self.canvas.create_oval(
                self.x, self.y,
                self.x + self.radius,
                self.y + self.radius,
                fill=self.color,
                outline="",
                tags="rain"
            )
    
    def reset(self, initial: bool = False) -> None:
        """Reinicia la partícula a una posición aleatoria y cambia su color."""
        self.x = random.randint(0, self.w)
        self.y = random.randint(-self.h, 0) if initial else -random.randint(5, 50)
        self.vy = random.uniform(2, 5)
        self.vx = random.uniform(-0.5, 0.5)
        self.bounces = 0
        self.max_bounces = 2
        
        # Cambiar color en cada reset para efecto dinámico
        self.color = random.choice(self.colors)
        if hasattr(self, "id") and not self.cached_image:
            self.canvas.itemconfig(self.id, fill=self.color)
    
    def update(self, wind: float = 0) -> bool:
        """
        Actualiza la posición de la partícula.
        Retorna True si la posición cambió, False si se reseteó.
        """
        new_x = self.x + self.vx + wind
        new_y = self.y + self.vy
        self.vy += 0.1
        
        floor_y = self.h - 10
        if new_y >= floor_y:
            if self.bounces < self.max_bounces:
                new_y = floor_y
                self.vy = -self.vy * 0.6
                self.bounces += 1
            else:
                self.reset()
                return False
        
        if new_y > self.h or new_x < -10 or new_x > self.w + 10:
            self.reset()
            return False
        
        self.x = new_x
        self.y = new_y
        return True


class PixelRain:
    """Sistema de animación optimizado de lluvia de píxeles."""
    
    def __init__(
        self,
        root: tk.Tk,
        canvas: tk.Canvas,
        bg: str,
        app: RedIMGApp
    ) -> None:
        self.root = root
        self.canvas = canvas
        self.bg = bg
        self.app = app
        self.particles: List[Particle] = []
        self.colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00",
            "#00FFFF", "#FF00FF", "#FFFFFF", "#FFA500"
        ]
        self.max_particles = 120  # Reducido para mejorar rendimiento al mover la ventana
        self._running = False
        self.cached_image: Optional[tk.PhotoImage] = None
        self._calc_queue: queue.Queue = queue.Queue()
        self._calc_thread: Optional[threading.Thread] = None
        self._frame_times: List[float] = []
        self._last_frame_time = 0.0
    
    def _create_cached_image(self) -> Optional[tk.PhotoImage]:
        """Crea una imagen en caché para las partículas."""
        try:
            img = tk.PhotoImage(width=2, height=2)
            img.put("#FFFFFF", to=(0, 0, 1, 1))
            img.put("#FFFFFF", to=(1, 0, 2, 1))
            img.put("#FFFFFF", to=(0, 1, 1, 2))
            img.put("#FFFFFF", to=(1, 1, 2, 2))
            return img
        except Exception:
            return None
    
    def _calc_worker(self) -> None:
        """Hilo de cálculo para actualizar posiciones de partículas."""
        while self._running:
            try:
                updates = []
                for p in self.particles:
                    p.update(0)
                    updates.append((p.id, p.x, p.y))
                
                if updates:
                    self._calc_queue.put(updates)
                
                time.sleep(0.015)  # ≈ 60 FPS de cálculo
            except Exception:
                pass
    
    def pre_create_particles(self) -> None:
        """Crea las partículas iniciales."""
        self.cached_image = None  # Desactivar imagen para permitir colores dinámicos
        
        try:
            self.root.tk.call('tk', 'scaling', 1.0)
        except Exception:
            pass
        
        for _ in range(self.max_particles):
            self.particles.append(
                Particle(self.canvas, 300, 125, self.colors, None)
            )
    
    def animate(self) -> None:
        """Animación de las partículas consumiendo la cola de cálculo."""
        if not self._running:
            return
        
        start_time = time.perf_counter()
        
        # Consumir SOLO la última actualización disponible para evitar lags acumulados
        latest_updates = None
        try:
            while not self._calc_queue.empty():
                latest_updates = self._calc_queue.get_nowait()
            
            if latest_updates:
                for pid, x, y in latest_updates:
                    if self.cached_image:
                        self.canvas.coords(pid, x, y)
                    else:
                        # Tamaño reducido de 1x1 para un efecto más fino
                        self.canvas.coords(pid, x, y, x + 1, y + 1)
        except Exception:
            pass
        
        # Perfilado y control de frames
        self._last_frame_time = time.perf_counter()
        
        target_interval = 32  # ~30 FPS: Equilibrio perfecto entre fluidez y consumo
        actual_elapsed = (time.perf_counter() - start_time) * 1000
        delay = max(1, target_interval - int(actual_elapsed))
        
        if delay < 5:
            self.root.after_idle(self.animate)
        else:
            self.root.after(delay, self.animate)
    
    @property
    def running(self) -> bool:
        """Retorna si la animación está activa."""
        return self._running
    
    @running.setter
    def running(self, value: bool) -> None:
        """Activa o desactiva la animación."""
        was = getattr(self, "_running", False)
        self._running = value
        
        if value and not was:
            self._calc_thread = threading.Thread(target=self._calc_worker, daemon=True)
            self._calc_thread.start()
            self.animate()
        elif not value and was:
            # El hilo se detendrá solo al chequear self._running
            pass


def main() -> None:
    """Punto de entrada principal."""
    app = RedIMGApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
