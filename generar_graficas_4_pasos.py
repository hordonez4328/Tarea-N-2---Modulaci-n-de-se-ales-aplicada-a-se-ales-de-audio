import os
import sys
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt

os.makedirs("graficas", exist_ok=True)

# 1. Cargar señal original
fs, audio = wav.read("audio/just_do_it.wav")
if audio.ndim > 1:
    audio = audio[:, 0]
audio = audio.astype(np.float32)
audio = audio / np.max(np.abs(audio))

# Filtrado pasa-bajos de la voz a 3500 Hz para banda base limpia
b, a = signal.butter(5, 3500 / (fs / 2), btype='low')
m_t = signal.filtfilt(b, a, audio)
m_t = m_t / np.max(np.abs(m_t))

tiempo = np.arange(len(m_t)) / fs

# 2. Señal portadora
fc = 2000.0  # Frecuencia de portadora que permite visibilidad perfecta de ciclos y envolvente
c_t = np.cos(2 * np.pi * fc * tiempo)

# 3. Señal resultante de multiplicar moduladora (voz) y portadora
# s(t) = m(t) * c(t) (Modulación Producto / DSB-SC)
# Y también en AM convencional: s_am(t) = (1 + ka * m(t)) * c(t)
ka = 0.8
envolvente_am = 1.0 + ka * m_t
s_mod_am = envolvente_am * c_t
s_mod_producto = m_t * c_t

# Ventana para visualización nítida (30 milisegundos en fonema activo)
t_inicio = 0.820
t_fin = 0.850
mask = (tiempo >= t_inicio) & (tiempo <= t_fin)
t_ms = (tiempo[mask] - t_inicio) * 1000

# -----------------------------------------------------------------------------
# FIGURA PRINCIPAL: SECUENCIA DE 4 PASOS SOLICITADA POR EL USUARIO
# -----------------------------------------------------------------------------
fig, axs = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
fig.suptitle("SECUENCIA DE MODULACIÓN DE SEÑAL DE VOZ", fontsize=15, fontweight="bold", y=0.98)

# 1. Señal original (la voz / moduladora)
axs[0].plot(t_ms, m_t[mask], color="#0284c7", lw=2.0, label="m(t): Señal de Voz (Moduladora)")
axs[0].set_title("1. Señal Original (La Voz / Moduladora m(t))", fontsize=12, fontweight="bold", loc="left", pad=6)
axs[0].set_ylabel("Amplitud normalizada", fontsize=10)
axs[0].grid(True, linestyle="--", alpha=0.55)
axs[0].set_ylim(-1.15, 1.15)
axs[0].legend(loc="upper right", framealpha=0.9)

# 2. Señal portadora
axs[1].plot(t_ms, c_t[mask], color="#9333ea", lw=1.2, label=f"c(t): Señal Portadora (fc = {fc:.0f} Hz)")
axs[1].set_title(f"2. Señal Portadora c(t) = cos(2π·fc·t)  [Alta Frecuencia]", fontsize=12, fontweight="bold", loc="left", pad=6)
axs[1].set_ylabel("Amplitud", fontsize=10)
axs[1].grid(True, linestyle="--", alpha=0.55)
axs[1].set_ylim(-1.15, 1.15)
axs[1].legend(loc="upper right", framealpha=0.9)

# 3. La portadora y por encima se vea la señal original la moduladora
axs[2].plot(t_ms, c_t[mask], color="#d8b4fe", lw=0.9, alpha=0.75, label="Portadora c(t) (Fondo)")
axs[2].plot(t_ms, m_t[mask], color="#0284c7", lw=2.5, label="Señal Original Moduladora m(t) (Por encima)")
axs[2].plot(t_ms, -m_t[mask], color="#0284c7", lw=1.4, linestyle=":", alpha=0.8, label="-m(t) (Envolvente simétrica)")
axs[2].set_title("3. La Portadora y por Encima la Señal Original (Moduladora)", fontsize=12, fontweight="bold", loc="left", pad=6)
axs[2].set_ylabel("Amplitud", fontsize=10)
axs[2].grid(True, linestyle="--", alpha=0.55)
axs[2].set_ylim(-1.25, 1.25)
axs[2].legend(loc="upper right", framealpha=0.9)

# 4. Señal resultante de multiplicar moduladora (señal original) y portadora resultado señal modulada
axs[3].plot(t_ms, s_mod_producto[mask], color="#ea580c", lw=1.3, label="s(t) = m(t) · c(t)  (Multiplicación / Modulada)")
axs[3].plot(t_ms, np.abs(m_t[mask]), color="#0284c7", lw=1.5, linestyle="--", alpha=0.8, label="|m(t)| (Envolvente de amplitud)")
axs[3].plot(t_ms, -np.abs(m_t[mask]), color="#0284c7", lw=1.5, linestyle="--", alpha=0.8)
axs[3].set_title("4. Señal Resultante de Multiplicar Moduladora y Portadora (Señal Modulada)", fontsize=12, fontweight="bold", loc="left", pad=6)
axs[3].set_xlabel("Tiempo [milisegundos]", fontsize=11, fontweight="bold")
axs[3].set_ylabel("Amplitud", fontsize=10)
axs[3].grid(True, linestyle="--", alpha=0.55)
axs[3].set_ylim(-1.25, 1.25)
axs[3].legend(loc="upper right", framealpha=0.9)

plt.tight_layout()
ruta_fig = "graficas/secuencia_modulacion_4_pasos.png"
plt.savefig(ruta_fig, dpi=300)
plt.close()
print(f"Figura 4 pasos guardada: {ruta_fig}")


# -----------------------------------------------------------------------------
# FIGURA COMPLETA: VISTA GLOBAL (2.38 s) + VISTA DETALLE ZOOM (30 ms)
# -----------------------------------------------------------------------------
fig2, axs2 = plt.subplots(4, 2, figsize=(15, 11))
fig2.suptitle("SECUENCIA DE MODULACIÓN: VISTA GLOBAL (2.38 s) vs DETALLE (30 ms)", fontsize=15, fontweight="bold")

# Fila 1: Moduladora
axs2[0, 0].plot(tiempo, m_t, color="#0284c7", lw=0.9)
axs2[0, 0].axvspan(t_inicio, t_fin, color="#fef08a", alpha=0.5, label="Zona de zoom")
axs2[0, 0].set_title("1. Moduladora (Completa 2.38 s)", fontweight="bold")
axs2[0, 0].set_ylabel("m(t)")
axs2[0, 0].grid(True, linestyle="--", alpha=0.5)
axs2[0, 0].legend(loc="upper right")

axs2[0, 1].plot(t_ms, m_t[mask], color="#0284c7", lw=2.0)
axs2[0, 1].set_title("1. Moduladora (Zoom 30 ms)", fontweight="bold")
axs2[0, 1].grid(True, linestyle="--", alpha=0.5)

# Fila 2: Portadora
axs2[1, 0].plot(tiempo[:2000], c_t[:2000], color="#9333ea", lw=0.7)
axs2[1, 0].set_title("2. Portadora (Primeros 40 ms)", fontweight="bold")
axs2[1, 0].set_ylabel("c(t)")
axs2[1, 0].grid(True, linestyle="--", alpha=0.5)

axs2[1, 1].plot(t_ms, c_t[mask], color="#9333ea", lw=1.2)
axs2[1, 1].set_title("2. Portadora (Zoom 30 ms)", fontweight="bold")
axs2[1, 1].grid(True, linestyle="--", alpha=0.5)

# Fila 3: Portadora con moduladora por encima
axs2[2, 0].plot(tiempo, m_t, color="#0284c7", lw=1.2, label="m(t)")
axs2[2, 0].set_title("3. Envolvente sobre Portadora (Global)", fontweight="bold")
axs2[2, 0].set_ylabel("Superposición")
axs2[2, 0].grid(True, linestyle="--", alpha=0.5)

axs2[2, 1].plot(t_ms, c_t[mask], color="#d8b4fe", lw=0.9, alpha=0.75, label="c(t)")
axs2[2, 1].plot(t_ms, m_t[mask], color="#0284c7", lw=2.4, label="m(t)")
axs2[2, 1].plot(t_ms, -m_t[mask], color="#0284c7", lw=1.2, linestyle=":")
axs2[2, 1].set_title("3. Portadora con Moduladora por Encima (Zoom)", fontweight="bold")
axs2[2, 1].grid(True, linestyle="--", alpha=0.5)
axs2[2, 1].legend(loc="upper right")

# Fila 4: Señal Modulada
axs2[3, 0].plot(tiempo, s_mod_producto, color="#ea580c", lw=0.7)
axs2[3, 0].set_title("4. Señal Modulada s(t) = m(t)·c(t) (Global)", fontweight="bold")
axs2[3, 0].set_xlabel("Tiempo [segundos]")
axs2[3, 0].set_ylabel("s(t)")
axs2[3, 0].grid(True, linestyle="--", alpha=0.5)

axs2[3, 1].plot(t_ms, s_mod_producto[mask], color="#ea580c", lw=1.3)
axs2[3, 1].plot(t_ms, np.abs(m_t[mask]), color="#0284c7", lw=1.5, linestyle="--")
axs2[3, 1].plot(t_ms, -np.abs(m_t[mask]), color="#0284c7", lw=1.5, linestyle="--")
axs2[3, 1].set_title("4. Señal Modulada (Zoom con Envolvente)", fontweight="bold")
axs2[3, 1].set_xlabel("Tiempo [milisegundos]")
axs2[3, 1].grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
ruta_fig2 = "graficas/secuencia_modulacion_completa_y_zoom.png"
plt.savefig(ruta_fig2, dpi=300)
plt.close()
print(f"Figura comparativa completa guardada: {ruta_fig2}")
