"""
INTERFAZ GRÁFICA INTERACTIVA - PROYECTO COMUNICACIONES 1
Análisis, Muestreo PCM, Modulación AM, Demodulación y Reconstrucción de Voz
"""

import os
import sys
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import tkinter as tk
from tkinter import ttk, messagebox

# Matplotlib para incrustar en Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Audio
try:
    import winsound
    HAVE_WINSOUND = True
except ImportError:
    HAVE_WINSOUND = False

try:
    import sounddevice as sd
    HAVE_SD = True
except ImportError:
    HAVE_SD = False


class AplicacionComunicaciones(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comunicaciones 1 - Simulador y Análisis de Señal de Voz")
        self.geometry("1180x820")
        self.minsize(980, 700)

        # Cargar y acondicionar señal de voz
        self.cargar_datos_audio()

        # Estilo ttk
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Configurar colores
        self.bg_color = "#f4f6f9"
        self.configure(bg=self.bg_color)

        # Contenedor superior con título y controles globales de reproducción
        self.crear_encabezado()

        # Cuaderno de pestañas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        # Crear pestañas temáticas
        self.crear_pestana_original()
        self.crear_pestana_pcm()
        self.crear_pestana_am()
        self.crear_pestana_fm()
        self.crear_pestana_demod()
        self.crear_pestana_comparacion()

    def cargar_datos_audio(self):
        ruta_wav = os.path.join("audio", "just_do_it.wav")
        if not os.path.exists(ruta_wav):
            # Si no existe, ejecutar conversión previa
            import subprocess
            subprocess.run([sys.executable, "procesamiento_voz.py"])

        self.fs, self.audio_orig = wav.read(ruta_wav)
        if self.audio_orig.ndim > 1:
            self.audio_orig = self.audio_orig[:, 0]
        if np.issubdtype(self.audio_orig.dtype, np.integer):
            self.audio_orig = self.audio_orig.astype(np.float32) / np.iinfo(self.audio_orig.dtype).max
        else:
            self.audio_orig = self.audio_orig.astype(np.float32)

        self.audio_orig = self.audio_orig / np.max(np.abs(self.audio_orig))
        self.N = len(self.audio_orig)
        self.duracion = self.N / self.fs
        self.tiempo = np.arange(self.N) / self.fs

        # Pre-filtrado para banda base de voz (3500 Hz)
        b, a = signal.butter(5, 3500 / (self.fs / 2), btype='low')
        self.m_t = signal.filtfilt(b, a, self.audio_orig)
        self.m_t = self.m_t / np.max(np.abs(self.m_t))

        # FFT base
        self.freqs = np.fft.rfftfreq(self.N, 1 / self.fs)
        self.fft_orig = np.abs(np.fft.rfft(self.audio_orig)) / self.N
        self.fft_orig_db = 20 * np.log10(np.maximum(self.fft_orig, 1e-6))

    def reproducir(self, nombre_archivo_o_data, fs=None):
        try:
            if isinstance(nombre_archivo_o_data, str):
                ruta = os.path.join("audio", nombre_archivo_o_data)
                if HAVE_WINSOUND and os.path.exists(ruta):
                    winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return
                elif HAVE_SD and os.path.exists(ruta):
                    fs_w, d_w = wav.read(ruta)
                    sd.play(d_w, fs_w)
                    return
            elif isinstance(nombre_archivo_o_data, np.ndarray) and HAVE_SD:
                sd.play(nombre_archivo_o_data, fs or self.fs)
                return
        except Exception as e:
            messagebox.showwarning("Audio", f"No se pudo reproducir el audio: {e}")

    def crear_encabezado(self):
        header_frame = tk.Frame(self, bg="#1e293b", padx=15, pady=10)
        header_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        lbl_tit = tk.Label(
            header_frame,
            text="Simulador Interactivo - Comunicaciones 1",
            font=("Segoe UI", 16, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        )
        lbl_tit.pack(side=tk.LEFT)

        lbl_sub = tk.Label(
            header_frame,
            text=f"| Audio: 'Just do it' | fs = {self.fs} Hz | Duración: {self.duracion:.2f} s",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#1e293b"
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        btn_box = tk.Frame(header_frame, bg="#1e293b")
        btn_box.pack(side=tk.RIGHT)

        btn_orig = tk.Button(
            btn_box, text="▶ Original", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=lambda: self.reproducir("just_do_it.wav")
        )
        btn_orig.pack(side=tk.LEFT, padx=4)

        btn_am = tk.Button(
            btn_box, text="▶ Modulada AM", bg="#8b5cf6", fg="white", font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=lambda: self.reproducir("senal_modulada_AM.wav")
        )
        btn_am.pack(side=tk.LEFT, padx=4)

        btn_fm = tk.Button(
            btn_box, text="▶ Modulada FM", bg="#d97706", fg="white", font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=lambda: self.reproducir("senal_modulada_FM.wav")
        )
        btn_fm.pack(side=tk.LEFT, padx=4)

        btn_rec = tk.Button(
            btn_box, text="▶ Reconstruida", bg="#10b981", fg="white", font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=lambda: self.reproducir("senal_reconstruida.wav")
        )
        btn_rec.pack(side=tk.LEFT, padx=4)

    # -------------------------------------------------------------------------
    # PESTAÑA 1: SEÑAL ORIGINAL
    # -------------------------------------------------------------------------
    def crear_pestana_original(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 1. Señal Original ")

        fig = Figure(figsize=(10, 6), dpi=100)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        ax1.plot(self.tiempo, self.audio_orig, color="#0284c7", lw=0.9)
        ax1.set_title("Forma de Onda en el Dominio del Tiempo x(t)", fontweight="bold")
        ax1.set_xlabel("Tiempo [segundos]")
        ax1.set_ylabel("Amplitud Normalizada")
        ax1.grid(True, linestyle="--", alpha=0.5)

        ax2.plot(self.freqs, self.fft_orig_db, color="#e11d48", lw=0.8)
        ax2.set_title("Espectro de Frecuencia (Transformada Rápida de Fourier - FFT)", fontweight="bold")
        ax2.set_xlabel("Frecuencia [Hz]")
        ax2.set_ylabel("Magnitud [dB]")
        ax2.set_xlim(0, 10000)
        ax2.grid(True, linestyle="--", alpha=0.5)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, tab)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    # -------------------------------------------------------------------------
    # PESTAÑA 2: MUESTREO Y DIGITALIZACIÓN PCM
    # -------------------------------------------------------------------------
    def crear_pestana_pcm(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 2. Muestreo y PCM ")

        ctrl_frame = tk.Frame(tab, bg="#e2e8f0", padx=10, pady=8)
        ctrl_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(ctrl_frame, text="Resolución de Cuantización (Bits):", bg="#e2e8f0", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.bits_var = tk.IntVar(value=8)
        bits_slider = tk.Scale(ctrl_frame, from_=2, to=16, orient=tk.HORIZONTAL, variable=self.bits_var, length=200, command=lambda v: self.actualizar_pcm())
        bits_slider.pack(side=tk.LEFT, padx=8)

        self.lbl_pcm_info = tk.Label(ctrl_frame, text="", bg="#e2e8f0", font=("Segoe UI", 9))
        self.lbl_pcm_info.pack(side=tk.LEFT, padx=15)

        btn_play_pcm = tk.Button(
            ctrl_frame, text="▶ Escuchar Cuantizado", bg="#d97706", fg="white", font=("Segoe UI", 9, "bold"),
            command=self.reproducir_pcm_actual
        )
        btn_play_pcm.pack(side=tk.RIGHT, padx=5)

        # Gráfica
        self.fig_pcm = Figure(figsize=(10, 6), dpi=100)
        self.ax_pcm1 = self.fig_pcm.add_subplot(2, 1, 1)
        self.ax_pcm2 = self.fig_pcm.add_subplot(2, 1, 2)
        self.fig_pcm.tight_layout()

        self.canvas_pcm = FigureCanvasTkAgg(self.fig_pcm, master=tab)
        self.canvas_pcm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.actualizar_pcm()

    def actualizar_pcm(self):
        n_bits = self.bits_var.get()
        L = 2 ** n_bits
        delta_q = 2.0 / (L - 1)

        indices = np.clip(np.round((self.audio_orig - (-1.0)) / delta_q), 0, L - 1)
        self.audio_pcm_actual = indices * delta_q - 1.0
        error = self.audio_orig - self.audio_pcm_actual
        sqnr = 10 * np.log10(np.mean(self.audio_orig**2) / max(np.mean(error**2), 1e-12))

        self.lbl_pcm_info.config(
            text=f"Niveles: {L} | Δ = {delta_q:.5f} | SQNR: {sqnr:.2f} dB"
        )

        # Zoom en 6 milisegundos
        mask = (self.tiempo >= 0.800) & (self.tiempo <= 0.806)
        t_ms = self.tiempo[mask] * 1000

        self.ax_pcm1.clear()
        self.ax_pcm2.clear()

        self.ax_pcm1.plot(t_ms, self.audio_orig[mask], label="Original Continua", color="#0284c7", lw=1.5)
        self.ax_pcm1.stem(t_ms, self.audio_orig[mask], linefmt="C0--", markerfmt="C0o", basefmt=" ", label="Muestras x[n]")
        self.ax_pcm1.step(t_ms, self.audio_pcm_actual[mask], where="mid", label=f"Cuantizado x_q[n] ({n_bits} bits)", color="#ea580c", lw=1.5)
        self.ax_pcm1.set_title(f"Muestreo y Cuantización Uniforme PCM ({n_bits} bits, {L} niveles)", fontweight="bold")
        self.ax_pcm1.set_ylabel("Amplitud")
        self.ax_pcm1.legend(loc="upper right")
        self.ax_pcm1.grid(True, linestyle="--", alpha=0.5)

        self.ax_pcm2.plot(t_ms, error[mask], color="#16a34a", label=f"Error e[n] = x[n] - x_q[n] (SQNR = {sqnr:.1f} dB)", lw=1.2)
        self.ax_pcm2.axhline(delta_q/2, color="red", linestyle=":", label=r"Límites $\pm \Delta/2$")
        self.ax_pcm2.axhline(-delta_q/2, color="red", linestyle=":")
        self.ax_pcm2.set_title("Ruido de Cuantización", fontweight="bold")
        self.ax_pcm2.set_xlabel("Tiempo [milisegundos]")
        self.ax_pcm2.set_ylabel("Error")
        self.ax_pcm2.legend(loc="upper right")
        self.ax_pcm2.grid(True, linestyle="--", alpha=0.5)

        self.fig_pcm.tight_layout()
        self.canvas_pcm.draw_idle()

    def reproducir_pcm_actual(self):
        self.reproducir(self.audio_pcm_actual.astype(np.float32))

    # -------------------------------------------------------------------------
    # PESTAÑA 3: MODULACIÓN AM
    # -------------------------------------------------------------------------
    def crear_pestana_am(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 3. Modulación AM ")

        ctrl_frame = tk.Frame(tab, bg="#e2e8f0", padx=10, pady=8)
        ctrl_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(ctrl_frame, text="Portadora fc [Hz]:", bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.fc_var = tk.DoubleVar(value=8000.0)
        fc_slider = tk.Scale(ctrl_frame, from_=2000, to=15000, resolution=500, orient=tk.HORIZONTAL, variable=self.fc_var, length=180, command=lambda v: self.actualizar_am())
        fc_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(ctrl_frame, text="Índice ka:", bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 3))
        self.ka_var = tk.DoubleVar(value=0.8)
        ka_slider = tk.Scale(ctrl_frame, from_=0.1, to=1.5, resolution=0.05, orient=tk.HORIZONTAL, variable=self.ka_var, length=140, command=lambda v: self.actualizar_am())
        ka_slider.pack(side=tk.LEFT, padx=5)

        self.lbl_am_status = tk.Label(ctrl_frame, text="", bg="#e2e8f0", font=("Segoe UI", 9, "bold"))
        self.lbl_am_status.pack(side=tk.LEFT, padx=10)

        btn_play_am = tk.Button(
            ctrl_frame, text="▶ Escuchar AM Sintetizada", bg="#7c3aed", fg="white", font=("Segoe UI", 9, "bold"),
            command=self.reproducir_am_actual
        )
        btn_play_am.pack(side=tk.RIGHT, padx=5)

        # Gráfica con los 4 pasos solicitados ordenados:
        # 1. Señal original (la voz)
        # 2. Señal portadora
        # 3. Portadora y por encima la señal original
        # 4. Multiplicación (señal modulada)
        self.fig_am = Figure(figsize=(11, 7.5), dpi=100)
        self.ax_am1 = self.fig_am.add_subplot(4, 1, 1)
        self.ax_am2 = self.fig_am.add_subplot(4, 1, 2)
        self.ax_am3 = self.fig_am.add_subplot(4, 1, 3)
        self.ax_am4 = self.fig_am.add_subplot(4, 1, 4)
        self.fig_am.tight_layout()

        self.canvas_am = FigureCanvasTkAgg(self.fig_am, master=tab)
        self.canvas_am.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.actualizar_am()

    def actualizar_am(self):
        fc = self.fc_var.get()
        ka = self.ka_var.get()

        if ka > 1.0:
            self.lbl_am_status.config(text=f"SOBREMODULACIÓN (ka={ka*100:.0f}%)", fg="#dc2626")
        else:
            self.lbl_am_status.config(text=f"Modulación Normal (ka={ka*100:.0f}%)", fg="#16a34a")

        # Portadora
        portadora = np.cos(2 * np.pi * fc * self.tiempo)
        # Señal modulada por producto y por envolvente
        self.s_mod_producto = self.m_t * portadora
        envolvente = 1.0 + ka * self.m_t
        self.s_am_actual = envolvente * portadora

        # Ventana para zoom nítido (30 ms)
        mask = (self.tiempo >= 0.820) & (self.tiempo <= 0.850)
        t_ms = (self.tiempo[mask] - 0.820) * 1000

        self.ax_am1.clear()
        self.ax_am2.clear()
        self.ax_am3.clear()
        self.ax_am4.clear()

        # 1. Señal original (la voz)
        self.ax_am1.plot(t_ms, self.m_t[mask], color="#0284c7", lw=1.8, label="m(t): Señal de Voz")
        self.ax_am1.set_title("1. Señal Original (La Voz / Moduladora m(t))", fontsize=9, fontweight="bold", loc="left")
        self.ax_am1.set_ylabel("m(t)", fontsize=8)
        self.ax_am1.grid(True, linestyle="--", alpha=0.45)
        self.ax_am1.legend(loc="upper right", fontsize=8)

        # 2. Señal portadora
        self.ax_am2.plot(t_ms, portadora[mask], color="#9333ea", lw=1.1, label=f"c(t) (fc = {fc:.0f} Hz)")
        self.ax_am2.set_title(f"2. Señal Portadora c(t) = cos(2π·fc·t)", fontsize=9, fontweight="bold", loc="left")
        self.ax_am2.set_ylabel("c(t)", fontsize=8)
        self.ax_am2.grid(True, linestyle="--", alpha=0.45)
        self.ax_am2.legend(loc="upper right", fontsize=8)

        # 3. La portadora y por encima la señal original (moduladora)
        self.ax_am3.plot(t_ms, portadora[mask], color="#d8b4fe", lw=0.8, alpha=0.7, label="Portadora c(t)")
        self.ax_am3.plot(t_ms, self.m_t[mask], color="#0284c7", lw=2.2, label="Original m(t) (Por encima)")
        self.ax_am3.plot(t_ms, -self.m_t[mask], color="#0284c7", lw=1.0, linestyle=":", alpha=0.7)
        self.ax_am3.set_title("3. Portadora con la Señal Original Superpuesta por Encima", fontsize=9, fontweight="bold", loc="left")
        self.ax_am3.set_ylabel("Superposición", fontsize=8)
        self.ax_am3.grid(True, linestyle="--", alpha=0.45)
        self.ax_am3.legend(loc="upper right", fontsize=8)

        # 4. Señal resultante de multiplicar moduladora y portadora (Señal Modulada)
        self.ax_am4.plot(t_ms, self.s_mod_producto[mask], color="#ea580c", lw=1.2, label="s(t) = m(t) · c(t) (Modulada)")
        self.ax_am4.plot(t_ms, np.abs(self.m_t[mask]), color="#0284c7", lw=1.2, linestyle="--", alpha=0.6, label="Envolvente |m(t)|")
        self.ax_am4.plot(t_ms, -np.abs(self.m_t[mask]), color="#0284c7", lw=1.2, linestyle="--", alpha=0.6)
        self.ax_am4.set_title("4. Señal Resultante de Multiplicar Moduladora y Portadora (Señal Modulada)", fontsize=9, fontweight="bold", loc="left")
        self.ax_am4.set_xlabel("Tiempo [milisegundos]", fontsize=9, fontweight="bold")
        self.ax_am4.set_ylabel("s(t)", fontsize=8)
        self.ax_am4.grid(True, linestyle="--", alpha=0.45)
        self.ax_am4.legend(loc="upper right", fontsize=8)

        self.fig_am.tight_layout()
        self.canvas_am.draw_idle()

    def reproducir_am_actual(self):
        norm = self.s_am_actual / np.max(np.abs(self.s_am_actual))
        self.reproducir(norm.astype(np.float32))

    # -------------------------------------------------------------------------
    # PESTAÑA: MODULACIÓN FM
    # -------------------------------------------------------------------------
    def crear_pestana_fm(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 4. Modulación FM ")

        ctrl_frame = tk.Frame(tab, bg="#e2e8f0", padx=10, pady=8)
        ctrl_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(ctrl_frame, text="Portadora fc [Hz]:", bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.fc_fm_var = tk.DoubleVar(value=1800.0)
        fc_slider = tk.Scale(ctrl_frame, from_=1000, to=4000, resolution=100, orient=tk.HORIZONTAL, variable=self.fc_fm_var, length=150, command=lambda v: self.actualizar_fm())
        fc_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(ctrl_frame, text="Desviación Δf [Hz]:", bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(8, 3))
        self.df_fm_var = tk.DoubleVar(value=1000.0)
        df_slider = tk.Scale(ctrl_frame, from_=200, to=1500, resolution=50, orient=tk.HORIZONTAL, variable=self.df_fm_var, length=150, command=lambda v: self.actualizar_fm())
        df_slider.pack(side=tk.LEFT, padx=5)

        self.lbl_fm_info = tk.Label(ctrl_frame, text="", bg="#e2e8f0", font=("Segoe UI", 9, "bold"), fg="#d97706")
        self.lbl_fm_info.pack(side=tk.LEFT, padx=10)

        btn_play_fm = tk.Button(
            ctrl_frame, text="▶ Escuchar FM", bg="#d97706", fg="white", font=("Segoe UI", 9, "bold"),
            command=self.reproducir_fm_actual
        )
        btn_play_fm.pack(side=tk.RIGHT, padx=5)

        # Gráfica de 4 pasos FM
        self.fig_fm = Figure(figsize=(11, 7.5), dpi=100)
        self.ax_fm1 = self.fig_fm.add_subplot(4, 1, 1)
        self.ax_fm2 = self.fig_fm.add_subplot(4, 1, 2)
        self.ax_fm3 = self.fig_fm.add_subplot(4, 1, 3)
        self.ax_fm4 = self.fig_fm.add_subplot(4, 1, 4)
        self.fig_fm.tight_layout()

        self.canvas_fm = FigureCanvasTkAgg(self.fig_fm, master=tab)
        self.canvas_fm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.actualizar_fm()

    def actualizar_fm(self):
        fc = self.fc_fm_var.get()
        df = self.df_fm_var.get()
        kf = df

        self.lbl_fm_info.config(text=f"Carson B_FM ≈ {2*(df + 3000):.0f} Hz (Amplitud Constante)")

        integral_m = np.cumsum(self.m_t) / self.fs
        c_t = np.cos(2 * np.pi * fc * self.tiempo)
        fi_t = fc + kf * self.m_t
        fase_fm = 2 * np.pi * fc * self.tiempo + 2 * np.pi * kf * integral_m
        self.s_fm_actual = np.cos(fase_fm)

        mask = (self.tiempo >= 0.820) & (self.tiempo <= 0.850)
        t_ms = (self.tiempo[mask] - 0.820) * 1000

        self.ax_fm1.clear()
        self.ax_fm2.clear()
        self.ax_fm3.clear()
        self.ax_fm4.clear()

        # 1. Moduladora
        self.ax_fm1.plot(t_ms, self.m_t[mask], color="#0284c7", lw=1.8, label="m(t): Señal de Voz")
        self.ax_fm1.set_title("1. Señal Original (La Voz / Moduladora m(t))", fontsize=9, fontweight="bold", loc="left")
        self.ax_fm1.set_ylabel("m(t)", fontsize=8)
        self.ax_fm1.grid(True, linestyle="--", alpha=0.45)
        self.ax_fm1.legend(loc="upper right", fontsize=8)

        # 2. Portadora Pura
        self.ax_fm2.plot(t_ms, c_t[mask], color="#9333ea", lw=1.1, label=f"c(t) (fc = {fc:.0f} Hz)")
        self.ax_fm2.set_title("2. Señal Portadora Sin Modular (Frecuencia Constante)", fontsize=9, fontweight="bold", loc="left")
        self.ax_fm2.set_ylabel("c(t)", fontsize=8)
        self.ax_fm2.grid(True, linestyle="--", alpha=0.45)
        self.ax_fm2.legend(loc="upper right", fontsize=8)

        # 3. Frecuencia instantánea
        self.ax_fm3.plot(t_ms, fi_t[mask], color="#16a34a", lw=1.8, label="fi(t) = fc + kf·m(t)")
        self.ax_fm3.axhline(fc, color="#9333ea", linestyle="--", alpha=0.6, label=f"fc = {fc:.0f} Hz")
        self.ax_fm3.set_title("3. Frecuencia Instantánea gobernada por la voz", fontsize=9, fontweight="bold", loc="left")
        self.ax_fm3.set_ylabel("Frecuencia [Hz]", fontsize=8)
        self.ax_fm3.grid(True, linestyle="--", alpha=0.45)
        self.ax_fm3.legend(loc="upper right", fontsize=8)

        # 4. Señal Modulada FM
        self.ax_fm4.plot(t_ms, self.s_fm_actual[mask], color="#d97706", lw=1.2, label="s_FM(t)")
        self.ax_fm4.axhline(1.0, color="#ef4444", linestyle=":", alpha=0.6)
        self.ax_fm4.axhline(-1.0, color="#ef4444", linestyle=":", alpha=0.6)
        self.ax_fm4.set_title("4. Señal Modulada FM (Amplitud Constante, Frecuencia Variable)", fontsize=9, fontweight="bold", loc="left")
        self.ax_fm4.set_xlabel("Tiempo [milisegundos]", fontsize=9, fontweight="bold")
        self.ax_fm4.set_ylabel("s_FM(t)", fontsize=8)
        self.ax_fm4.grid(True, linestyle="--", alpha=0.45)
        self.ax_fm4.legend(loc="upper right", fontsize=8)

        self.fig_fm.tight_layout()
        self.canvas_fm.draw_idle()

    def reproducir_fm_actual(self):
        self.reproducir(self.s_fm_actual.astype(np.float32))

    # -------------------------------------------------------------------------
    # PESTAÑA 4: DEMODULACIÓN COHERENTE
    # -------------------------------------------------------------------------
    def crear_pestana_demod(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 4. Demodulación ")

        ctrl_frame = tk.Frame(tab, bg="#e2e8f0", padx=10, pady=8)
        ctrl_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(ctrl_frame, text="Filtro Pasa-Bajos [Hz]:", bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.f_filtro_var = tk.DoubleVar(value=3800.0)
        filtro_slider = tk.Scale(ctrl_frame, from_=1500, to=8000, resolution=200, orient=tk.HORIZONTAL, variable=self.f_filtro_var, length=200, command=lambda v: self.actualizar_demod())
        filtro_slider.pack(side=tk.LEFT, padx=5)

        btn_play_demod = tk.Button(
            ctrl_frame, text="▶ Escuchar Demodulada", bg="#059669", fg="white", font=("Segoe UI", 9, "bold"),
            command=self.reproducir_demod_actual
        )
        btn_play_demod.pack(side=tk.RIGHT, padx=5)

        # Gráfica
        self.fig_demod = Figure(figsize=(10, 6), dpi=100)
        self.ax_dem1 = self.fig_demod.add_subplot(2, 1, 1)
        self.ax_dem2 = self.fig_demod.add_subplot(2, 1, 2)
        self.fig_demod.tight_layout()

        self.canvas_demod = FigureCanvasTkAgg(self.fig_demod, master=tab)
        self.canvas_demod.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.actualizar_demod()

    def actualizar_demod(self):
        fc = self.fc_var.get()
        f_corte = self.f_filtro_var.get()

        # Multiplicación coherente
        v_t = self.s_am_actual * (2.0 * np.cos(2 * np.pi * fc * self.tiempo))

        # Filtro pasa-bajos
        b, a = signal.butter(6, min(f_corte, (self.fs/2)-100) / (self.fs / 2), btype='low')
        v_filt = signal.filtfilt(b, a, v_t)
        self.m_demod_actual = v_filt - np.mean(v_filt)
        if np.max(np.abs(self.m_demod_actual)) > 0:
            self.m_demod_actual = self.m_demod_actual / np.max(np.abs(self.m_demod_actual))

        self.ax_dem1.clear()
        self.ax_dem2.clear()

        mask = (self.tiempo >= 0.800) & (self.tiempo <= 0.806)
        t_ms = self.tiempo[mask] * 1000

        self.ax_dem1.plot(t_ms, v_t[mask], color="#a855f7", lw=0.9, label=r"$v(t) = s_{AM}(t) \cdot 2\cos(2\pi f_c t)$")
        self.ax_dem1.plot(t_ms, v_filt[mask], color="#059669", lw=1.8, label="Salida del Filtro Pasa Bajos")
        self.ax_dem1.set_title("Detección Coherente y Etapa de Filtrado", fontweight="bold")
        self.ax_dem1.set_ylabel("Amplitud")
        self.ax_dem1.legend(loc="upper right")
        self.ax_dem1.grid(True, linestyle="--", alpha=0.5)

        self.ax_dem2.plot(self.tiempo, self.m_demod_actual, color="#059669", lw=0.9, label="Señal Recuperada m_rec(t)")
        self.ax_dem2.set_title("Señal Demodulada Final (Sin componente DC, Normalizada)", fontweight="bold")
        self.ax_dem2.set_xlabel("Tiempo [segundos]")
        self.ax_dem2.set_ylabel("Amplitud")
        self.ax_dem2.legend(loc="upper right")
        self.ax_dem2.grid(True, linestyle="--", alpha=0.5)

        self.fig_demod.tight_layout()
        self.canvas_demod.draw_idle()

    def reproducir_demod_actual(self):
        self.reproducir(self.m_demod_actual.astype(np.float32))

    # -------------------------------------------------------------------------
    # PESTAÑA 5: COMPARACIÓN Y MÉTRICAS
    # -------------------------------------------------------------------------
    def crear_pestana_comparacion(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 5. Comparación y Métricas ")

        info_frame = tk.Frame(tab, bg="#1e293b", padx=15, pady=8)
        info_frame.pack(fill=tk.X, side=tk.TOP)

        # Calcular métricas iniciales
        mse = np.mean((self.m_t - self.m_demod_actual)**2)
        snr = 10 * np.log10(np.mean(self.m_t**2) / max(mse, 1e-12))
        corr = np.corrcoef(self.m_t, self.m_demod_actual)[0, 1]

        lbl_metricas = tk.Label(
            info_frame,
            text=f"Correlación (r): {corr:.5f}  |  MSE: {mse:.6e}  |  SNR: {snr:.2f} dB",
            font=("Segoe UI", 11, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        lbl_metricas.pack(side=tk.LEFT)

        btn_play_both = tk.Button(
            info_frame, text="▶ Escuchar Original vs Reconstruida", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"),
            command=self.reproducir_comparativa
        )
        btn_play_both.pack(side=tk.RIGHT)

        # Gráfica
        fig = Figure(figsize=(10, 6), dpi=100)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        ax1.plot(self.tiempo, self.m_t, label="Original m(t)", color="#0284c7", lw=1.0, alpha=0.85)
        ax1.plot(self.tiempo, self.m_demod_actual, label="Reconstruida", color="#10b981", lw=0.9, linestyle="--", alpha=0.85)
        ax1.set_title("Superposición Temporal Completa", fontweight="bold")
        ax1.set_xlabel("Tiempo [segundos]")
        ax1.set_ylabel("Amplitud")
        ax1.legend(loc="upper right")
        ax1.grid(True, linestyle="--", alpha=0.5)

        # Zoom de 30 ms
        mask = (self.tiempo >= 1.00) & (self.tiempo <= 1.03)
        t_ms = self.tiempo[mask] * 1000
        ax2.plot(t_ms, self.m_t[mask], label="Original", color="#0284c7", lw=1.8)
        ax2.plot(t_ms, self.m_demod_actual[mask], label="Reconstruida", color="#10b981", lw=1.4, linestyle="--")
        ax2.set_title("Detalle Ampliado (Zoom 30 ms)", fontweight="bold")
        ax2.set_xlabel("Tiempo [milisegundos]")
        ax2.set_ylabel("Amplitud")
        ax2.legend(loc="upper right")
        ax2.grid(True, linestyle="--", alpha=0.5)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, tab)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def reproducir_comparativa(self):
        self.reproducir("just_do_it.wav")
        self.after(2600, lambda: self.reproducir("senal_reconstruida.wav"))


if __name__ == "__main__":
    app = AplicacionComunicaciones()
    app.mainloop()
