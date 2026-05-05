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
import gc
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
import json

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

try:
    import rawpy
except ImportError:
    rawpy = None

try:
    import pillow_avif
except ImportError:
    pass

try:
    import windnd
except ImportError:
    windnd = None


VERSION = "3.6.0"

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


def get_resource_path(relative_path: str) -> str:
    """Obtiene la ruta absoluta al recurso, compatible con desarrollo y Nuitka/PyInstaller."""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # Nuitka o ejecución normal: usamos la carpeta del ejecutable o del script
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_max_threads() -> int:
    """Retorna el número máximo de hilos disponibles."""
    return os.cpu_count() or 4


logger = setup_logging()


class RedIMGApp:
    """Aplicación principal de RedIMG."""
    
    SUPPORTED_FORMATS = {
        ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp",
        ".heic", ".heif", ".cr2", ".nef", ".arw", ".dng"
    }
    
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
        # Estilo para la barra de progreso (Color del icono RedIMG)
        self.root.style.configure(
            "info.Horizontal.TProgressbar", 
            thickness=8, 
            borderwidth=0, 
            troughcolor="#000000",
            background="#FF1A55"
        )
        
        self._setup_dark_mode()
        
        self.processing_queue: queue.Queue = queue.Queue()
        self.is_processing = False
        self.cancel_requested = False
        self._notif_window = None
        
        self.config = {
            "target_size_kb": 780,
            "format": "jpg",
            "webp_mode": "lossless"
        }
        self.load_config()
        
        icon_path = get_resource_path("RedIMG.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
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
    
    def load_config(self) -> None:
        """Carga la configuración desde config.json."""
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                logger.error("Error cargando config.json: %s", e)

    def save_config(self) -> None:
        """Guarda la configuración actual en config.json."""
        config_path = "config.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error("Error guardando config.json: %s", e)

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
        
        self.id_lbl_time = self.canvas_bg.create_text(
            150, 80,
            text="",
            fill="#00FF99",
            font=("Arial", 8),
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
        
        self.id_btn_config = self.canvas_bg.create_text(
            15, 115,
            text="⚙",
            fill="#BBBBBB",
            font=("Arial", 12),
            anchor="se",
            tags=("ui", "config_btn")
        )
        self.canvas_bg.tag_bind("config_btn", "<Button-1>", lambda e: self.mostrar_config())
        self.canvas_bg.tag_bind("config_btn", "<Enter>", lambda e: (self.canvas_bg.itemconfig(self.id_btn_config, fill="#FFFFFF"), self.canvas_bg.config(cursor="hand2")))
        self.canvas_bg.tag_bind("config_btn", "<Leave>", lambda e: (self.canvas_bg.itemconfig(self.id_btn_config, fill="#BBBBBB"), self.canvas_bg.config(cursor="")))
        

    
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
                    if len(msg) > 2:
                        self.canvas_bg.itemconfig(self.id_lbl_time, text=f"Estimado: {msg[2]}")
                elif msg[0] == "done":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.progress["value"] = 0
                    self.canvas_bg.itemconfig(self.id_lbl_time, text="")
                    self.notificar_usuario("Éxito", msg[1], "success")
                elif msg[0] == "error":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.notificar_usuario("Error", msg[1], "danger")
                elif msg[0] == "warning":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.canvas_bg.itemconfig(self.id_lbl_time, text="")
                    self.notificar_usuario("Aviso", msg[1], "warning")
                elif msg[0] == "cancelled":
                    self.is_processing = False
                    self.rain_system.running = True
                    self.progress["value"] = 0
                    self.canvas_bg.itemconfig(self.id_lbl_time, text="")
                    self.notificar_usuario("Cancelado", msg[1], "info")
        except queue.Empty:
            pass
        finally:
            if not self.is_processing and not self.rain_system.running:
                self.rain_system.running = True
            self.root.after(30, self.check_queue)
    
    def notificar_usuario(self, titulo: str, mensaje: str, tipo: str = "info") -> None:
        """Muestra una notificación personalizada compacta que no bloquea la UI central."""
        if getattr(self, "_notif_window", None) and self._notif_window.winfo_exists():
            self._notif_window.destroy()
        notif = tk.Toplevel(self.root)
        self._notif_window = notif
        notif.withdraw()
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)
        notif.configure(background="#111111")
        
        # Heredar icono de la ventana principal
        icon_path = get_resource_path("RedIMG.ico")
        if os.path.exists(icon_path):
            try:
                notif.iconbitmap(icon_path)
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
        self.root.after(4000, lambda: notif.destroy() if notif.winfo_exists() else None)

    def on_select_file(self) -> None:
        """Abre el selector de archivos."""
        if self.is_processing:
            return
        
        archivos = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp *.heic *.heif *.cr2 *.nef *.arw *.dng"),
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
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception as e:
            logger.debug("Fallo en exif_transpose, intentando método manual: %s", e)
            try:
                exif = img.getexif()
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
        max_weight_kb: Optional[int] = None,
        out_format: str = "jpg",
        webp_mode: str = "lossy"
    ) -> None:
        """
        Optimiza la imagen usando búsqueda binaria para encontrar el peso ideal.
        
        Args:
            img: Imagen PIL a optimizar
            ruta_salida: Ruta donde se guardará la imagen
            max_weight_kb: Peso máximo en KB (0 para sin límite)
            out_format: Formato de salida ("jpg", "webp", "avif")
            webp_mode: Modo de WebP ("lossy", "lossless")
        """
        if max_weight_kb is None:
            max_weight_kb = self.config.get("target_size_kb", 780)
            
        is_unlimited = max_weight_kb <= 0
        max_size_bytes = max_weight_kb * 1024 if not is_unlimited else float('inf')
        
        # Guardado sin límite o inicial
        buffer_init = BytesIO()
        
        if out_format == "webp":
            if webp_mode == "lossless":
                img.save(buffer_init, "WEBP", lossless=True)
            else:
                img.save(buffer_init, "WEBP", quality=95, method=6)
        elif out_format == "avif":
            try:
                img.save(buffer_init, "AVIF", quality=90)
            except Exception as e:
                logger.error("Error guardando AVIF inicial, cayendo a JPG: %s", e)
                out_format = "jpg"
                img.save(buffer_init, "JPEG", quality=95, optimize=True, progressive=True, subsampling="4:2:0")
        elif out_format == "png":
            img.save(buffer_init, "PNG", optimize=True, compress_level=9)
        else: # jpg
            img.save(buffer_init, "JPEG", quality=95, optimize=True, progressive=True, subsampling="4:2:0")
            
        if is_unlimited or buffer_init.tell() <= max_size_bytes:
            with open(ruta_salida, "wb") as f:
                f.write(buffer_init.getvalue())
            buffer_init.close()
            return
            
        # Búsqueda binaria para ajustar calidad
        low, high = 10, 90
        final_buffer = None
        smallest_buffer = None
        iterations = 0
        
        try:
            while low <= high and iterations < 6:
                iterations += 1
                mid = (low + high) // 2
                buffer = BytesIO()
                
                if out_format == "png":
                    # Mapear mid (10 a 90) a colores (2 a 256) para PNG
                    colores = int(2 + (mid - 10) * 254 / 80)
                    img_q = img.quantize(colors=colores)
                    img_q.save(buffer, "PNG", optimize=True, compress_level=9)
                elif out_format == "webp":
                    img.save(buffer, "WEBP", quality=mid, method=6)
                elif out_format == "avif":
                    try:
                        img.save(buffer, "AVIF", quality=mid)
                    except:
                        buffer.close()
                        break # Falla AVIF a mitad, usamos el último bueno
                else: # jpg
                    img.save(buffer, "JPEG", quality=mid, optimize=True, progressive=True, subsampling="4:2:0")
                
                size = buffer.tell()
                
                # Mantener el buffer más pequeño generado por si nunca alcanzamos la meta
                if smallest_buffer is None or size < smallest_buffer.tell():
                    if smallest_buffer:
                        smallest_buffer.close()
                    smallest_buffer = BytesIO(buffer.getvalue())
                
                if size <= max_size_bytes:
                    if final_buffer:
                        final_buffer.close()
                    final_buffer = buffer
                    if size >= max_size_bytes * 0.90:
                        break
                    low = mid + 1
                else:
                    buffer.close()
                    high = mid - 1
            
            buffer_to_save = final_buffer if final_buffer else smallest_buffer
            if not buffer_to_save:
                buffer_to_save = buffer_init
                
            with open(ruta_salida, "wb") as f:
                f.write(buffer_to_save.getvalue())
        finally:
            if final_buffer:
                final_buffer.close()
            if smallest_buffer:
                smallest_buffer.close()
            if buffer_init:
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
            nombre_contexto = os.path.basename(base_carpeta)
            if not nombre_contexto:
                nombre_contexto = "Procesado"
            
            # Nombre de la carpeta de salida (ya no es harcodeado "RedIMG")
            salida_dir_name = f"{nombre_contexto}_Proc"
            salida_dir = os.path.join(base_carpeta, salida_dir_name)
            os.makedirs(salida_dir, exist_ok=True)
            
            errores = []
            max_threads = get_max_threads()
            max_weight = self.config.get("target_size_kb", 780)
            
            # Dimensiones escaladas según el peso elegido
            if max_weight <= 0:
                max_size = float('inf') # Sin límite, sin redimensión
            elif max_weight <= 780:
                max_size = 1600         # Mínimo establecido
            elif max_weight <= 1024:
                max_size = 2048         # Para 1MB
            else:
                max_size = 3072         # Para 2MB o superior
                
            out_format = self.config.get("format", "jpg").lower()
            webp_mode = self.config.get("webp_mode", "lossy")
            
            if out_format not in ["jpg", "webp", "avif", "png"]:
                out_format = "jpg"
            
            # Formatear extension
            ext_map = {"jpg": ".jpg", "webp": ".webp", "avif": ".avif", "png": ".png"}
            out_ext = ext_map.get(out_format, ".jpg")
            
            logger.info(
                "Procesando %d imágenes con %d hilos (max_size=%d, max_weight=%dKB, formato=%s)",
                total, max_threads, max_size, max_weight, out_format
            )
            
            start_time = time.time()
            
            def process_item(item: tuple) -> tuple:
                """Procesa un archivo individual. Retorna (éxito, nombre, error)."""
                if self.cancel_requested:
                    return (False, "", "Cancelado por usuario")
                
                idx, ruta = item
                try:
                    if total > 1:
                        # Procesamiento en lote: NombreDirectorio_001
                        nombre_base = f"{nombre_contexto}_{idx:03d}"
                    else:
                        # Procesamiento individual: NombreArchivo_Proc
                        nombre_base = f"{os.path.splitext(os.path.basename(ruta))[0]}_Proc"
                    
                    nombre_final = nombre_base + out_ext
                    salida = os.path.join(salida_dir, nombre_final)
                    
                    ext = os.path.splitext(ruta)[1].lower()
                    if ext in (".cr2", ".nef", ".arw", ".dng") and rawpy is not None:
                        with rawpy.imread(ruta) as raw:
                            rgb = raw.postprocess()
                            img = Image.fromarray(rgb)
                            img_proc = self.preparar_imagen(img, max_size)
                            self.optimizar_y_guardar(img_proc, salida, max_weight, out_format, webp_mode)
                            img.close()
                    else:
                        with Image.open(ruta) as img:
                            img_proc = self.preparar_imagen(img, max_size)
                            self.optimizar_y_guardar(img_proc, salida, max_weight, out_format, webp_mode)
                    
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
                    
                    # Calcular tiempo estimado
                    elapsed = time.time() - start_time
                    avg_time_per_img = elapsed / completados
                    remaining_imgs = total - completados
                    est_remaining_sec = avg_time_per_img * remaining_imgs
                    
                    if est_remaining_sec > 60:
                        est_time_str = f"{int(est_remaining_sec//60)}m {int(est_remaining_sec%60)}s"
                    else:
                        est_time_str = f"{int(est_remaining_sec)}s"
                        
                    self.processing_queue.put(("progress", completados / total, est_time_str))
                    if completados % 50 == 0:
                        gc.collect()
            
            if self.cancel_requested:
                self.processing_queue.put(
                    ("cancelled", f"Procesamiento cancelado.\n{completados} de {total} imágenes procesadas.")
                )
                return
            
            if not errores:
                msg = (
                    f"Procesadas {total} imágenes."
                    if total > 1
                    else "Imagen procesada con éxito."
                )
                self.processing_queue.put(("done", msg))
                logger.info("Procesamiento completado: %d/%d imágenes", total, total)
            else:
                error_summary = "\n".join(errores[:10])
                if len(errores) > 10:
                    error_summary += f"\n...y {len(errores) - 10} errores más"
                self.processing_queue.put(
                    ("warning", f"Terminado con {len(errores)} errores.\n\n{error_summary}\n\nRevisa la carpeta /{salida_dir_name}")
                )
                logger.warning("Procesamiento completado con errores: %d/%d", total - len(errores), total)
            
            gc.collect()
        
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
            self.about_window.geometry("300x156")
            self.about_window.resizable(False, False)
            self.about_window.configure(background="#000000")
            self.about_window.overrideredirect(True)
            self.about_window.attributes("-topmost", True)
            # Forzar estilo para las labels de la ventana about
            self.root.style.configure("About.TLabel", background="#000000", foreground="#B0B0B0")
            
            self.root.update_idletasks()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_w = self.root.winfo_width()
            main_h = self.root.winfo_height()
            
            title_bar_h = self.root.winfo_rooty() - main_y
            if title_bar_h < 0 or title_bar_h > 50:
                title_bar_h = 31
                
            total_h = main_h + title_bar_h
            
            x = main_x + main_w + 5
            y = main_y
            self.about_window.geometry(f"300x{total_h}+{int(x)}+{int(y)}")
            
            self.root.after(200, self._set_about_focus)
            
            lbl_title = ttk.Label(
                self.about_window,
                text=f"RedIMG v{VERSION}",
                font=("Arial", 9, "bold"),
                foreground="#00FF99",
                background="#000000",
                justify="center"
            )
            lbl_title.pack(pady=(15, 0), padx=10)
            
            txt = (
                "Redimensionado y optimización rápida de imágenes.\n"
                "Arrastra tus imágenes en la interfaz para\n"
                "procesarlas, convertirlas y enviarlas fácilmente."
            )
            
            lbl_info = ttk.Label(
                self.about_window,
                text=txt,
                font=("Arial", 9),
                wraplength=280,
                style="About.TLabel",
                justify="center"
            )
            lbl_info.pack(pady=(5, 0), padx=10)
            
            exts = sorted([f.replace('.', '').upper() for f in self.SUPPORTED_FORMATS])
            mid = len(exts) // 2
            text_exts = ", ".join(exts[:mid]) + ",\n" + ", ".join(exts[mid:])
            
            lbl_formats = ttk.Label(
                self.about_window,
                text=text_exts,
                font=("Arial", 8),
                wraplength=280,
                style="About.TLabel",
                justify="center"
            )
            lbl_formats.pack(pady=(12, 0), padx=10)
            
            link = ttk.Label(
                self.about_window,
                text="QwertyAserty",
                cursor="hand2",
                foreground="#00FF99",
                background="#000000",
                font=("Arial", 9, "underline")
            )
            link.pack(side="top", anchor="center", padx=10, pady=(12, 0))
            link.bind("<Button-1>", lambda e: webbrowser.open("https://qwertyaserty.com/"))
        
        except Exception as e:
            logger.error("Error al mostrar About: %s", e)
            messagebox.showerror("Error", f"No se pudo abrir About:\n{e}")
    

    def cerrar_about(self, event: Optional[tk.Event] = None) -> None:
        """Cierra la ventana Acerca de."""
        if hasattr(self, "about_window") and self.about_window and self.about_window.winfo_exists():
            if event:
                try:
                    x, y = self.about_window.winfo_pointerxy()
                    x0 = self.about_window.winfo_rootx()
                    y0 = self.about_window.winfo_rooty()
                    x1 = x0 + self.about_window.winfo_width()
                    y1 = y0 + self.about_window.winfo_height()
                    if x0 <= x <= x1 and y0 <= y <= y1:
                        return
                except Exception:
                    pass
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

    def mostrar_config(self) -> None:
        """Muestra la ventana de Configuración (Settings)."""
        try:
            if hasattr(self, "config_window") and self.config_window and self.config_window.winfo_exists():
                self.config_window.lift()
                return
            
            self.config_window = ttk.Toplevel(self.root)
            self.config_window.title("Configuración")
            self.config_window.geometry("300x156")
            self.config_window.resizable(False, False)
            self.config_window.configure(background="#000000")
            self.config_window.overrideredirect(True)
            self.config_window.attributes("-topmost", True)
            
            self.root.update_idletasks()
            main_x = self.canvas_bg.winfo_rootx()
            main_y = self.canvas_bg.winfo_rooty()
            main_h = self.canvas_bg.winfo_height()
            
            x = main_x
            y = main_y + main_h
            self.config_window.geometry(f"300x165+{int(x)}+{int(y)}")
            
            self.root.after(200, self._set_config_focus)
            
            # Content of Config
            container = tk.Frame(self.config_window, bg="#000000")
            container.pack(fill="both", expand=True, padx=20, pady=15)
            
            # 1. Preset Slider para Target Size
            size_frame = tk.Frame(container, bg="#000000")
            size_frame.pack(fill="x", pady=(0, 15))
            
            lbl_size = ttk.Label(size_frame, text="Tamaño:", background="#000000", foreground="#FFFFFF", font=("Arial", 10, "bold"))
            lbl_size.pack(side="left")
            
            presets = [("780KB", 780), ("1MB", 1024), ("2MB", 2048), ("Sin límite", 0)]
            
            def get_preset_idx(kb):
                for i, (_, val) in enumerate(presets):
                    if kb == val: return i
                return 0
                
            current_idx = get_preset_idx(self.config.get("target_size_kb", 780))
            
            self.var_size = tk.IntVar(master=self.config_window, value=current_idx)
            lbl_size_val = ttk.Label(size_frame, text=presets[current_idx][0], background="#000000", foreground="#FFFFFF", font=("Arial", 10, "bold"))
            lbl_size_val.pack(side="right")
            
            def on_slider_change(val):
                idx = round(float(val))
                self.var_size.set(idx)
                lbl_size_val.config(text=presets[idx][0])
                self.config["target_size_kb"] = presets[idx][1]
                self.save_config()
                
            slider = ttk.Scale(container, from_=0, to=len(presets)-1, variable=self.var_size, orient="horizontal", command=on_slider_change, bootstyle="info")
            slider.pack(fill="x", pady=(0, 2))
            
            ticks_canvas = tk.Canvas(container, height=8, bg="#000000", highlightthickness=0)
            ticks_canvas.pack(fill="x", pady=(0, 15))
            
            def draw_ticks(event):
                ticks_canvas.delete("all")
                w = event.width
                pad = 8 # Margen interno del thumb del slider
                usable_w = w - (pad * 2)
                if usable_w > 0:
                    for i in range(len(presets)):
                        x = pad + (usable_w * i / (len(presets) - 1))
                        ticks_canvas.create_line(x, 0, x, 6, fill="#00FF99", width=2)
                        
            ticks_canvas.bind("<Configure>", draw_ticks)
            
            # 2. Formato de Salida
            lbl_format = ttk.Label(container, text="Convertir a:", background="#000000", foreground="#00FF99", font=("Arial", 10, "bold"))
            lbl_format.pack(anchor="w", pady=(0, 10))
            
            format_frame = tk.Frame(container, bg="#000000")
            format_frame.pack(fill="x")
            
            self.var_format = tk.StringVar(master=self.config_window, value=self.config.get("format", "jpg"))
            
            def on_format_change():
                fmt = self.var_format.get()
                self.config["format"] = fmt
                if fmt == "webp":
                    self.config["webp_mode"] = "lossless"
                self.save_config()
                
            # Establecer WebP Lossless por defecto al cargar si era lossy
            if self.config.get("format") == "webp":
                self.config["webp_mode"] = "lossless"
                self.save_config()
            
            rb_jpg = ttk.Radiobutton(format_frame, text="JPG", variable=self.var_format, value="jpg", command=on_format_change, bootstyle="success-toolbutton")
            rb_png = ttk.Radiobutton(format_frame, text="PNG", variable=self.var_format, value="png", command=on_format_change, bootstyle="success-toolbutton")
            rb_webp = ttk.Radiobutton(format_frame, text="WebP", variable=self.var_format, value="webp", command=on_format_change, bootstyle="success-toolbutton")
            rb_avif = ttk.Radiobutton(format_frame, text="AVIF", variable=self.var_format, value="avif", command=on_format_change, bootstyle="success-toolbutton")
            
            rb_jpg.pack(side="left", expand=True, fill="x", padx=3)
            rb_png.pack(side="left", expand=True, fill="x", padx=3)
            rb_webp.pack(side="left", expand=True, fill="x", padx=3)
            rb_avif.pack(side="left", expand=True, fill="x", padx=3)

        except Exception as e:
            logger.error("Error al mostrar Config: %s", e)
            messagebox.showerror("Error", f"No se pudo abrir Config:\n{e}")

    def cerrar_config(self, event: Optional[tk.Event] = None) -> None:
        """Cierra la ventana Config."""
        if hasattr(self, "config_window") and self.config_window and self.config_window.winfo_exists():
            if event:
                try:
                    x, y = self.config_window.winfo_pointerxy()
                    x0 = self.config_window.winfo_rootx()
                    y0 = self.config_window.winfo_rooty()
                    x1 = x0 + self.config_window.winfo_width()
                    y1 = y0 + self.config_window.winfo_height()
                    if x0 <= x <= x1 and y0 <= y <= y1:
                        return
                except Exception:
                    pass
            self.config_window.destroy()
            self.config_window = None

    def _set_config_focus(self) -> None:
        """Configura el foco en la ventana Config."""
        if hasattr(self, "config_window") and self.config_window and self.config_window.winfo_exists():
            try:
                self.config_window.focus_set()
                self.config_window.bind("<FocusOut>", self.cerrar_config)
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
        if random.random() < 0.90:
            self.x = random.randint(0, self.w // 2)
        else:
            self.x = random.randint(self.w // 2, self.w)
            
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
        self.max_particles = 60  # Reducido para mejorar rendimiento y simplicidad
        self._running = False
    
    def pre_create_particles(self) -> None:
        """Crea las partículas iniciales."""
        try:
            self.root.tk.call('tk', 'scaling', 1.0)
        except Exception:
            pass
        
        for _ in range(self.max_particles):
            self.particles.append(
                Particle(self.canvas, 300, 125, self.colors, None)
            )
    
    def animate(self) -> None:
        """Animación de las partículas simplificada sin hilos extra."""
        if not self._running:
            return
        
        start_time = time.perf_counter()
        
        try:
            for p in self.particles:
                p.update(0)
                self.canvas.coords(p.id, p.x, p.y, p.x + 1, p.y + 1)
        except Exception:
            pass
        
        target_interval = 33  # ~30 FPS
        actual_elapsed = (time.perf_counter() - start_time) * 1000
        delay = max(1, target_interval - int(actual_elapsed))
        
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
            self.animate()
        elif not value and was:
            # El hilo se detendrá solo al chequear self._running
            pass


def main() -> None:
    """Punto de entrada principal."""
    try:
        app = RedIMGApp()
        app.root.mainloop()
    except Exception as e:
        logger.exception("Error fatal durante la ejecución: %s", e)
        # Mostrar error en una ventana simple si es posible
        try:
            import messagebox
            messagebox.showerror("Error Fatal", f"La aplicación se cerró por un error inesperado:\n{e}")
        except:
            pass


if __name__ == "__main__":
    main()
