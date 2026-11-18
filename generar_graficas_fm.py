import os
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt

os.makedirs("graficas", exist_ok=True)
os.makedirs("audio", exist_ok=True)

# 1. Cargar señal de voz original
fs, audio = wav.read("audio/just_do_it.wav")
if audio.ndim > 1:
    audio = audio[:, 0]
audio = audio.astype(np.float32)
audio = audio / np.max(np.abs(audio))

# Pre-filtrado a 3000 Hz
b, a = signal.butter(5, 3000 / (fs / 2), btype='low')
m_t = signal.filtfilt(b, a, audio)
m_t = m_t / np.max(np.abs(m_t))
tiempo = np.arange(len(m_t)) / fs

# Parámetros de FM
# Usamos fc = 2000 Hz y delta_f = 1200 Hz para que en la gráfica se distingan visualmente
# los cambios de período (compresión y expansión de la onda)
fc_vis = 1800.0
delta_f_vis = 1100.0
kf_vis = delta_f_vis

# Integral de m(t)
integral_m = np.cumsum(m_t) / fs

# Señal Portadora pura
c_t = np.cos(2 * np.pi * fc_vis * tiempo)

# Frecuencia instantánea: fi(t) = fc + kf * m(t)
fi_t = fc_vis + kf_vis * m_t

# Señal Modulada FM: s_FM(t) = Ac * cos(2*pi*fc*t + 2*pi*kf * integral(m))
fase_fm = 2 * np.pi * fc_vis * tiempo + 2 * np.pi * kf_vis * integral_m
s_fm_vis = np.cos(fase_fm)

# También señal AM para la gráfica comparativa
s_am_vis = (1.0 + 0.8 * m_t) * c_t
s_am_vis = s_am_vis / np.max(np.abs(s_am_vis))

# Ventana para zoom nítido (30 ms)
t_inicio = 0.820
t_fin = 0.850
mask = (tiempo >= t_inicio) & (tiempo <= t_fin)
t_ms = (tiempo[mask] - t_inicio) * 1000

# -----------------------------------------------------------------------------
# FIGURA 1: SECUENCIA DE MODULACIÓN FM EN 4 PASOS
# -----------------------------------------------------------------------------
fig, axs = plt.subplots(4, 1, figsize=(13, 11), sharex=True)
fig.suptitle("SECUENCIA DE MODULACIÓN EN FRECUENCIA (FM)", fontsize=15, fontweight="bold", y=0.98)

# 1. Señal original (la voz / moduladora)
axs[0].plot(t_ms, m_t[mask], color="#0284c7", lw=2.0, label="m(t): Señal de Voz (Moduladora)")
axs[0].set_title("1. Señal Original (La Voz / Moduladora m(t))", fontsize=11, fontweight="bold", loc="left", pad=6)
axs[0].set_ylabel("Amplitud", fontsize=10)
axs[0].grid(True, linestyle="--", alpha=0.55)
axs[0].set_ylim(-1.15, 1.15)
axs[0].legend(loc="upper right")

# 2. Señal Portadora sin modular
axs[1].plot(t_ms, c_t[mask], color="#9333ea", lw=1.2, label=f"c(t) = cos(2π·fc·t)  (fc = {fc_vis:.0f} Hz constante)")
axs[1].set_title(f"2. Señal Portadora Sin Modular (Frecuencia Constante fc = {fc_vis:.0f} Hz)", fontsize=11, fontweight="bold", loc="left", pad=6)
axs[1].set_ylabel("Amplitud", fontsize=10)
axs[1].grid(True, linestyle="--", alpha=0.55)
axs[1].set_ylim(-1.15, 1.15)
axs[1].legend(loc="upper right")

# 3. Frecuencia instantánea gobernada por la moduladora
axs[2].plot(t_ms, fi_t[mask], color="#16a34a", lw=2.0, label=r"Frecuencia Instantánea $f_i(t) = f_c + k_f \cdot m(t)$")
axs[2].axhline(fc_vis, color="#9333ea", linestyle="--", alpha=0.7, label=f"Portadora central fc ({fc_vis:.0f} Hz)")
axs[2].set_title(r"3. Variación de la Frecuencia Instantánea $f_i(t)$ en función de la voz", fontsize=11, fontweight="bold", loc="left", pad=6)
axs[2].set_ylabel("Frecuencia [Hz]", fontsize=10)
axs[2].grid(True, linestyle="--", alpha=0.55)
axs[2].legend(loc="upper right")

# 4. Señal Modulada FM
axs[3].plot(t_ms, s_fm_vis[mask], color="#d97706", lw=1.3, label=r"$s_{FM}(t) = \cos(2\pi f_c t + 2\pi k_f \int m(\tau)d\tau)$")
axs[3].axhline(1.0, color="#ef4444", linestyle=":", alpha=0.6, label="Envolvente de amplitud constante (Ac = ±1)")
axs[3].axhline(-1.0, color="#ef4444", linestyle=":", alpha=0.6)
axs[3].set_title("4. Señal Modulada FM (Amplitud Constante, Frecuencia Variable: Compresión/Expansión)", fontsize=11, fontweight="bold", loc="left", pad=6)
axs[3].set_xlabel("Tiempo [milisegundos]", fontsize=11, fontweight="bold")
axs[3].set_ylabel("Amplitud", fontsize=10)
axs[3].grid(True, linestyle="--", alpha=0.55)
axs[3].set_ylim(-1.25, 1.25)
axs[3].legend(loc="upper right")

plt.tight_layout()
ruta_fig_fm = "graficas/secuencia_modulacion_FM_4_pasos.png"
plt.savefig(ruta_fig_fm, dpi=300)
plt.close()
print(f"Figura FM de 4 pasos guardada: {ruta_fig_fm}")

# -----------------------------------------------------------------------------
# FIGURA 2: COMPARATIVA DIDÁCTICA AM vs FM
# -----------------------------------------------------------------------------
fig_comp, axs_c = plt.subplots(3, 1, figsize=(13, 8.5), sharex=True)
fig_comp.suptitle("COMPARACIÓN TÉCNICA: MODULACIÓN AM vs MODULACIÓN FM", fontsize=15, fontweight="bold", y=0.98)

# 1. Moduladora
axs_c[0].plot(t_ms, m_t[mask], color="#0284c7", lw=2.0, label="m(t): Señal Original de Voz")
axs_c[0].set_title("Señal Moduladora de Entrada m(t)", fontweight="bold", loc="left")
axs_c[0].set_ylabel("Amplitud")
axs_c[0].grid(True, linestyle="--", alpha=0.5)
axs_c[0].legend(loc="upper right")

# 2. AM
axs_c[1].plot(t_ms, s_am_vis[mask], color="#9333ea", lw=1.1, label="Modulación AM: Amplitud Variable, Frecuencia Fija")
axs_c[1].plot(t_ms, (1.0 + 0.8*m_t[mask])/1.8, "r--", lw=1.3, label="Envolvente de Amplitud")
axs_c[1].set_title("Modulación de Amplitud (AM)  ➔  La información viaja en la ENVOLVENTE de amplitud", fontweight="bold", loc="left")
axs_c[1].set_ylabel("s_AM(t)")
axs_c[1].grid(True, linestyle="--", alpha=0.5)
axs_c[1].legend(loc="upper right")

# 3. FM
axs_c[2].plot(t_ms, s_fm_vis[mask], color="#d97706", lw=1.2, label="Modulación FM: Frecuencia Variable, Amplitud Constante")
axs_c[2].axhline(1.0, color="#ef4444", linestyle=":", alpha=0.6)
axs_c[2].axhline(-1.0, color="#ef4444", linestyle=":", alpha=0.6)
axs_c[2].set_title("Modulación de Frecuencia (FM)  ➔  La información viaja en el ESPACIADO (frecuencia)", fontweight="bold", loc="left")
axs_c[2].set_xlabel("Tiempo [milisegundos]", fontweight="bold")
axs_c[2].set_ylabel("s_FM(t)")
axs_c[2].grid(True, linestyle="--", alpha=0.5)
axs_c[2].legend(loc="upper right")

plt.tight_layout()
ruta_fig_comp = "graficas/comparativa_AM_vs_FM.png"
plt.savefig(ruta_fig_comp, dpi=300)
plt.close()
print(f"Figura Comparativa AM vs FM guardada: {ruta_fig_comp}")
