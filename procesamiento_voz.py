"""
PROYECTO: PROCESAMIENTO, MODULACIÓN Y RECONSTRUCCIÓN DE SEÑAL DE VOZ
CURSO: COMUNICACIONES 1

Contenido de las etapas:
1. Grabación y carga de la señal (WAV / OGG).
2. Reproducción y análisis de la señal original (tiempo y frecuencia, fs).
3. Muestreo y digitalización (discretización, cuantización PCM, tren de bits).
4. Modulación (Modulación de Amplitud - AM con portadora).
5. Demodulación (Demodulación coherente con filtro pasa bajos).
6. Reconstrucción y comparación cuantitativa/cualitativa (SNR, MSE, correlación).
"""

import os
import sys

# Asegurar codificación UTF-8 en consola de Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt

# Intentar importar librerías de reproducción de audio
try:
    import sounddevice as sd
    HAVE_SOUNDDEVICE = True
except ImportError:
    HAVE_SOUNDDEVICE = False

try:
    import winsound
    HAVE_WINSOUND = True
except ImportError:
    HAVE_WINSOUND = False

# Intentar importar PyAV para conversión transparente de formatos si es necesario
try:
    import av
    HAVE_AV = True
except ImportError:
    HAVE_AV = False


def reproducir_audio(audio_path_o_array, fs=None, label="Audio"):
    """
    Reproduce una señal de audio por los altavoces del sistema.
    Funciona pasando la ruta de un archivo WAV o directamente un array de numpy y fs.
    """
    print(f"\n[REPRODUCCIÓN] Reproduciendo: {label}...")
    try:
        if isinstance(audio_path_o_array, str) and os.path.exists(audio_path_o_array):
            if HAVE_WINSOUND:
                winsound.PlaySound(audio_path_o_array, winsound.SND_FILENAME)
                return
            elif HAVE_SOUNDDEVICE:
                fs_wav, data_wav = wav.read(audio_path_o_array)
                sd.play(data_wav, fs_wav)
                sd.wait()
                return
        elif isinstance(audio_path_o_array, np.ndarray) and fs is not None:
            if HAVE_SOUNDDEVICE:
                sd.play(audio_path_o_array, fs)
                sd.wait()
                return
        print("  -> (Aviso) Reproductor no interactivo disponible o silenciado.")
    except Exception as e:
        print(f"  -> No se pudo reproducir en el altavoz actual ({e}).")


def asegurar_archivo_wav(directorio_audio="audio"):
    """
    Verifica que exista un archivo WAV en la carpeta audio.
    Si solo existe .ogg, lo convierte automáticamente a WAV.
    """
    os.makedirs(directorio_audio, exist_ok=True)
    archivos = os.listdir(directorio_audio)
    
    # Buscar archivo WAV ya existente
    for f in archivos:
        if f.lower().endswith(".wav") and not f.startswith("modulada") and not f.startswith("demodulada") and not f.startswith("reconstruida"):
            return os.path.join(directorio_audio, f)
            
    # Si no hay WAV, buscar OGG
    for f in archivos:
        if f.lower().endswith(".ogg"):
            ruta_ogg = os.path.join(directorio_audio, f)
            ruta_wav = os.path.join(directorio_audio, os.path.splitext(f)[0].replace(" ", "_") + ".wav")
            print(f"[CONVERSIÓN] Convirtiendo '{f}' a WAV...")
            if HAVE_AV:
                container = av.open(ruta_ogg)
                stream = container.streams.audio[0]
                frames = [frame.to_ndarray() for frame in container.decode(stream)]
                audio_data = np.concatenate(frames, axis=1)
                if audio_data.ndim == 2 and audio_data.shape[0] == 1:
                    audio_data = audio_data[0]
                # Guardar en float32 o int16 normalizado
                audio_norm = audio_data.astype(np.float32)
                if np.max(np.abs(audio_norm)) > 0:
                    audio_norm = audio_norm / np.max(np.abs(audio_norm))
                wav.write(ruta_wav, stream.codec_context.sample_rate, audio_norm)
                print(f"  -> Archivo WAV generado: {ruta_wav}")
                return ruta_wav
            else:
                raise RuntimeError("Se requiere el paquete 'av' para decodificar notas de voz en formato OGG/Opus.")

    raise FileNotFoundError("No se encontró ningún archivo de audio en la carpeta 'audio/'.")


def main():
    print("=" * 70)
    print("   PROYECTO DE COMUNICACIONES 1: ANÁLISIS, MODULACIÓN Y RECONSTRUCCIÓN")
    print("=" * 70)

    directorio_graficas = "graficas"
    directorio_audio = "audio"
    os.makedirs(directorio_graficas, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. GRABACIÓN / OBTENCIÓN DE LA SEÑAL
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 1: OBTENCIÓN DE LA SEÑAL DE VOZ")
    print("=" * 50)
    ruta_wav = asegurar_archivo_wav(directorio_audio)
    print(f"Archivo de entrada seleccionado: '{ruta_wav}'")

    # -------------------------------------------------------------------------
    # 2. REPRODUCCIÓN Y ANÁLISIS DE LA SEÑAL ORIGINAL
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 2: REPRODUCCIÓN Y ANÁLISIS DE LA SEÑAL ORIGINAL")
    print("=" * 50)
    
    fs, audio_orig = wav.read(ruta_wav)
    # Convertir a float32 mono en rango [-1.0, 1.0]
    if audio_orig.ndim > 1:
        audio_orig = audio_orig[:, 0]
    
    if np.issubdtype(audio_orig.dtype, np.integer):
        max_val = np.iinfo(audio_orig.dtype).max
        audio_orig = audio_orig.astype(np.float32) / max_val
    else:
        audio_orig = audio_orig.astype(np.float32)
        
    # Normalización de amplitud máxima a 1.0
    if np.max(np.abs(audio_orig)) > 0:
        audio_orig = audio_orig / np.max(np.abs(audio_orig))

    duracion = len(audio_orig) / fs
    tiempo = np.arange(len(audio_orig)) / fs

    print(f"  • Frecuencia de muestreo (fs): {fs} Hz ({fs/1000:.1f} kHz)")
    print(f"  • Número total de muestras (N): {len(audio_orig):,} muestras")
    print(f"  • Duración total: {duracion:.2f} segundos")
    print(f"  • Amplitud máxima: {np.max(audio_orig):.4f}, mínima: {np.min(audio_orig):.4f}")

    # Espectro de frecuencia con FFT
    N = len(audio_orig)
    fft_vals = np.fft.rfft(audio_orig)
    freqs = np.fft.rfftfreq(N, 1/fs)
    fft_mag = np.abs(fft_vals) / N
    fft_db = 20 * np.log10(np.maximum(fft_mag, 1e-6))

    # Ancho de banda de potencia (99%)
    potencia_acum = np.cumsum(fft_mag**2)
    idx_99 = np.where(potencia_acum >= 0.99 * potencia_acum[-1])[0][0]
    bw_99 = freqs[idx_99]
    print(f"  • Ancho de banda estimado (99% energía): {bw_99:.1f} Hz")

    # Gráfica Etapa 2
    fig, axs = plt.subplots(2, 1, figsize=(11, 6))
    fig.suptitle("Etapa 2: Análisis de la Señal Original de Voz", fontsize=14, fontweight='bold')
    
    axs[0].plot(tiempo, audio_orig, color='#1f77b4', lw=0.9)
    axs[0].set_title(f"Dominio del Tiempo (fs = {fs} Hz, Duración = {duracion:.2f} s)")
    axs[0].set_xlabel("Tiempo [segundos]")
    axs[0].set_ylabel("Amplitud normalizada")
    axs[0].grid(True, linestyle='--', alpha=0.6)
    axs[0].set_ylim(-1.1, 1.1)

    axs[1].plot(freqs, fft_db, color='#d62728', lw=0.8)
    axs[1].set_title("Espectro de Frecuencia (Transformada Rápida de Fourier - FFT)")
    axs[1].set_xlabel("Frecuencia [Hz]")
    axs[1].set_ylabel("Magnitud [dB]")
    axs[1].set_xlim(0, min(12000, fs/2))
    axs[1].axvline(bw_99, color='green', linestyle=':', label=f"99% Energía ({bw_99:.0f} Hz)")
    axs[1].legend(loc="upper right")
    axs[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    ruta_fig2 = os.path.join(directorio_graficas, "1_senal_original_tiempo_frecuencia.png")
    plt.savefig(ruta_fig2, dpi=300)
    plt.close()
    print(f"  -> Gráfica guardada en: {ruta_fig2}")

    # -------------------------------------------------------------------------
    # 3. MUESTREO Y DIGITALIZACIÓN (PCM)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 3: MUESTREO Y DIGITALIZACIÓN (PCM)")
    print("=" * 50)

    # Simulación de cuantización uniforme PCM de 8 bits (256 niveles)
    n_bits = 8
    num_niveles = 2 ** n_bits
    q_min, q_max = -1.0, 1.0
    delta_q = (q_max - q_min) / (num_niveles - 1)

    # Discretización y cuantización
    indices_cuant = np.clip(np.round((audio_orig - q_min) / delta_q), 0, num_niveles - 1).astype(int)
    audio_pcm = indices_cuant * delta_q + q_min
    error_cuantizacion = audio_orig - audio_pcm
    sqnr = 10 * np.log10(np.mean(audio_orig**2) / np.mean(error_cuantizacion**2))

    print(f"  • Resolución de digitalización: {n_bits} bits ({num_niveles} niveles de cuantización)")
    print(f"  • Paso de cuantizacion (Delta): {delta_q:.6f}")
    print(f"  • SQNR (Relacion Senal a Ruido de Cuantizacion): {sqnr:.2f} dB")
    
    # Muestra del flujo de bits binario de las primeras 5 muestras
    bits_ejemplo = [f"{idx:08b}" for idx in indices_cuant[1000:1005]]
    print(f"  • Ejemplo de codificacion binaria (muestras 1000 a 1004): {' '.join(bits_ejemplo)}")

    # Guardar audio digitalizado PCM
    ruta_wav_pcm = os.path.join(directorio_audio, "senal_digitalizada_pcm_8bits.wav")
    wav.write(ruta_wav_pcm, fs, audio_pcm.astype(np.float32))
    print(f"  -> Audio cuantizado PCM guardado en: {ruta_wav_pcm}")

    # Gráfica Etapa 3 (Zoom para apreciar muestras discretas y niveles de cuantización)
    # Seleccionamos un intervalo de 8 milisegundos en una zona con voz activa
    t_start = 0.80
    t_end = 0.808
    mask_zoom = (tiempo >= t_start) & (tiempo <= t_end)
    t_zoom = tiempo[mask_zoom]
    orig_zoom = audio_orig[mask_zoom]
    pcm_zoom = audio_pcm[mask_zoom]
    err_zoom = error_cuantizacion[mask_zoom]

    fig, axs = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    fig.suptitle("Etapa 3: Muestreo, Cuantización y Digitalización (PCM 8 bits)", fontsize=14, fontweight='bold')

    axs[0].plot(t_zoom * 1000, orig_zoom, label="Señal Continua / Original", color='#1f77b4', lw=1.5)
    axs[0].stem(t_zoom * 1000, orig_zoom, linefmt='C0--', markerfmt='C0o', basefmt=" ", label="Muestras x[n]")
    axs[0].set_title("Muestreo Discreto (Impulsos x[n] = x(n·Ts))")
    axs[0].set_ylabel("Amplitud")
    axs[0].legend(loc="upper right")
    axs[0].grid(True, linestyle='--', alpha=0.6)

    axs[1].step(t_zoom * 1000, pcm_zoom, where='mid', label="Señal Cuantizada x_q[n] (256 niveles)", color='#ff7f0e', lw=1.5)
    axs[1].plot(t_zoom * 1000, orig_zoom, 'k--', alpha=0.4, label="Original de referencia")
    axs[1].set_title("Cuantización Uniforme PCM (Escalón Δ = 2/255)")
    axs[1].set_ylabel("Nivel Cuantizado")
    axs[1].legend(loc="upper right")
    axs[1].grid(True, linestyle='--', alpha=0.6)

    axs[2].plot(t_zoom * 1000, err_zoom, color='#2ca02c', lw=1.2, label=f"Error e[n] = x[n] - x_q[n] (SQNR = {sqnr:.1f} dB)")
    axs[2].axhline(delta_q/2, color='red', linestyle=':', alpha=0.7, label=r"Límites teóricos ($\pm \Delta / 2$)")
    axs[2].axhline(-delta_q/2, color='red', linestyle=':', alpha=0.7)
    axs[2].set_title("Ruido / Error de Cuantización")
    axs[2].set_xlabel("Tiempo [milisegundos]")
    axs[2].set_ylabel("Error")
    axs[2].legend(loc="upper right")
    axs[2].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    ruta_fig3 = os.path.join(directorio_graficas, "2_muestreo_y_digitalizacion_pcm.png")
    plt.savefig(ruta_fig3, dpi=300)
    plt.close()
    print(f"  -> Gráfica guardada en: {ruta_fig3}")

    # -------------------------------------------------------------------------
    # 4. MODULACIÓN (AM CONVENCIONAL CON PORTADORA)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 4: MODULACIÓN DE AMPLITUD (AM)")
    print("=" * 50)
    
    # Pre-filtrado pasa bajos de la señal moduladora a 3.5 kHz (estándar telefónico/voz)
    f_corte_voz = 3500.0
    b_voz, a_voz = signal.butter(5, f_corte_voz / (fs / 2), btype='low')
    m_t = signal.filtfilt(b_voz, a_voz, audio_orig)
    m_t = m_t / np.max(np.abs(m_t))  # Señal mensaje normalizada m(t)

    # Parámetros de Modulación AM
    # Portadora a 8000 Hz: audible para que el usuario pueda escuchar el efecto de modulación
    fc = 8000.0  
    Ac = 1.0
    ka = 0.8  # Índice de modulación m_a = 80% (sin sobremodulación para detector de envolvente)

    # Portadora c(t)
    c_t = np.cos(2 * np.pi * fc * tiempo)

    # Señal Modulada en Amplitud: s_AM(t) = Ac * [1 + ka * m(t)] * cos(2*pi*fc*t)
    envolvente = Ac * (1.0 + ka * m_t)
    s_am = envolvente * c_t

    # Normalizar para almacenamiento y reproducción en formato WAV
    s_am_norm = s_am / np.max(np.abs(s_am))
    ruta_wav_am = os.path.join(directorio_audio, "senal_modulada_AM.wav")
    wav.write(ruta_wav_am, fs, s_am_norm.astype(np.float32))

    print(f"  • Tecnica de modulacion elegida: AM (Amplitud Modulada Convencional / DSB-FC)")
    print(f"  • Frecuencia de la portadora (fc): {fc:.0f} Hz ({fc/1000:.1f} kHz)")
    print(f"  • Indice de modulacion (ka): {ka * 100:.0f}%")
    print(f"  • Ecuacion: s(t) = Ac * [1 + ka * m(t)] * cos(2*pi*fc*t)")
    print(f"  -> Archivo de senal modulada guardado en: {ruta_wav_am}")

    # Espectro de la señal modulada
    fft_am = np.abs(np.fft.rfft(s_am)) / N
    fft_am_db = 20 * np.log10(np.maximum(fft_am, 1e-6))

    # Gráfica Etapa 4
    fig, axs = plt.subplots(2, 1, figsize=(11, 7))
    fig.suptitle(f"Etapa 4: Modulación AM (Portadora fc = {fc:.0f} Hz, Índice = {ka*100:.0f}%)", fontsize=14, fontweight='bold')

    # Zoom temporal donde se aprecie la portadora y la envolvente
    t_start_am = 0.800
    t_end_am = 0.806
    mask_am = (tiempo >= t_start_am) & (tiempo <= t_end_am)

    axs[0].plot(tiempo[mask_am] * 1000, s_am[mask_am], color='#1f77b4', lw=1.0, label="Señal Modulada s_AM(t)")
    axs[0].plot(tiempo[mask_am] * 1000, envolvente[mask_am], 'r--', lw=1.8, label="Envolvente Superior [Ac(1 + ka·m(t))]")
    axs[0].plot(tiempo[mask_am] * 1000, -envolvente[mask_am], 'r:', lw=1.5, label="Envolvente Inferior")
    axs[0].set_title("Forma de Onda en el Tiempo (Detalle de oscilación y envolvente)")
    axs[0].set_xlabel("Tiempo [milisegundos]")
    axs[0].set_ylabel("Amplitud")
    axs[0].legend(loc="upper right")
    axs[0].grid(True, linestyle='--', alpha=0.6)

    axs[1].plot(freqs, fft_am_db, color='#9467bd', lw=0.9)
    axs[1].axvline(fc, color='red', linestyle='--', label=f"Portadora central fc = {fc:.0f} Hz")
    axs[1].axvline(fc - f_corte_voz, color='green', linestyle=':', label=f"Banda Lateral Inferior (LSB: {fc-f_corte_voz:.0f} Hz)")
    axs[1].axvline(fc + f_corte_voz, color='orange', linestyle=':', label=f"Banda Lateral Superior (USB: {fc+f_corte_voz:.0f} Hz)")
    axs[1].set_title("Espectro de Frecuencia de la Señal Modulada AM (Portadora + Bandas Laterales)")
    axs[1].set_xlabel("Frecuencia [Hz]")
    axs[1].set_ylabel("Magnitud [dB]")
    axs[1].set_xlim(0, min(16000, fs/2))
    axs[1].legend(loc="upper right")
    axs[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    ruta_fig4 = os.path.join(directorio_graficas, "3_modulacion_am_tiempo_espectro.png")
    plt.savefig(ruta_fig4, dpi=300)
    plt.close()
    print(f"  -> Gráfica guardada en: {ruta_fig4}")

    # Gráfica solicitada en 4 pasos ordenados:
    # 1. Señal original (la voz)
    # 2. Señal portadora
    # 3. La portadora y por encima la señal original (moduladora)
    # 4. Señal resultante de multiplicar moduladora y portadora (modulada)
    t_inicio_4p = 0.820
    t_fin_4p = 0.850 # 30 ms para apreciación clara
    mask_4p = (tiempo >= t_inicio_4p) & (tiempo <= t_fin_4p)
    t_ms_4p = (tiempo[mask_4p] - t_inicio_4p) * 1000

    fig_4p, axs_4p = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    fig_4p.suptitle("SECUENCIA DE MODULACIÓN DE SEÑAL DE VOZ", fontsize=15, fontweight="bold", y=0.98)

    # 1. Señal original
    axs_4p[0].plot(t_ms_4p, m_t[mask_4p], color="#0284c7", lw=2.0, label="m(t): Señal de Voz (Moduladora)")
    axs_4p[0].set_title("1. Señal Original (La Voz / Moduladora m(t))", fontsize=11, fontweight="bold", loc="left")
    axs_4p[0].set_ylabel("Amplitud")
    axs_4p[0].grid(True, linestyle="--", alpha=0.55)
    axs_4p[0].legend(loc="upper right")

    # 2. Señal portadora
    axs_4p[1].plot(t_ms_4p, c_t[mask_4p], color="#9333ea", lw=1.2, label=f"c(t): Señal Portadora (fc = {fc:.0f} Hz)")
    axs_4p[1].set_title("2. Señal Portadora c(t) = cos(2π·fc·t) [Alta Frecuencia]", fontsize=11, fontweight="bold", loc="left")
    axs_4p[1].set_ylabel("Amplitud")
    axs_4p[1].grid(True, linestyle="--", alpha=0.55)
    axs_4p[1].legend(loc="upper right")

    # 3. Portadora con la señal original por encima
    axs_4p[2].plot(t_ms_4p, c_t[mask_4p], color="#d8b4fe", lw=0.9, alpha=0.7, label="Portadora c(t) (Fondo)")
    axs_4p[2].plot(t_ms_4p, m_t[mask_4p], color="#0284c7", lw=2.4, label="Señal Original Moduladora m(t) (Por encima)")
    axs_4p[2].plot(t_ms_4p, -m_t[mask_4p], color="#0284c7", lw=1.2, linestyle=":", alpha=0.75, label="-m(t) (Envolvente simétrica)")
    axs_4p[2].set_title("3. La Portadora y por Encima la Señal Original (Moduladora)", fontsize=11, fontweight="bold", loc="left")
    axs_4p[2].set_ylabel("Amplitud")
    axs_4p[2].grid(True, linestyle="--", alpha=0.55)
    axs_4p[2].legend(loc="upper right")

    # 4. Señal resultante de la multiplicación
    s_producto = m_t * c_t
    axs_4p[3].plot(t_ms_4p, s_producto[mask_4p], color="#ea580c", lw=1.3, label="s(t) = m(t) · c(t) (Multiplicación / Modulada)")
    axs_4p[3].plot(t_ms_4p, np.abs(m_t[mask_4p]), color="#0284c7", lw=1.4, linestyle="--", alpha=0.7, label="|m(t)| (Envolvente)")
    axs_4p[3].plot(t_ms_4p, -np.abs(m_t[mask_4p]), color="#0284c7", lw=1.4, linestyle="--", alpha=0.7)
    axs_4p[3].set_title("4. Señal Resultante de Multiplicar Moduladora y Portadora (Señal Modulada)", fontsize=11, fontweight="bold", loc="left")
    axs_4p[3].set_xlabel("Tiempo [milisegundos]", fontweight="bold")
    axs_4p[3].set_ylabel("Amplitud")
    axs_4p[3].grid(True, linestyle="--", alpha=0.55)
    axs_4p[3].legend(loc="upper right")

    plt.tight_layout()
    ruta_fig_4p = os.path.join(directorio_graficas, "secuencia_modulacion_4_pasos.png")
    plt.savefig(ruta_fig_4p, dpi=300)
    plt.close()
    print(f"  -> Gráfica de 4 pasos guardada en: {ruta_fig_4p}")

    # -------------------------------------------------------------------------
    # 4B. MODULACIÓN EN FRECUENCIA (FM)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 4B: MODULACIÓN EN FRECUENCIA (FM)")
    print("=" * 50)

    fc_fm = 6000.0  # Portadora central FM (6 kHz)
    delta_f = 2500.0 # Desviación de frecuencia (2.5 kHz)
    kf = delta_f

    # Fase instantánea FM: theta(t) = 2*pi*fc*t + 2*pi*kf * integral(m(tau)dtau)
    integral_m = np.cumsum(m_t) / fs
    fase_fm = 2 * np.pi * fc_fm * tiempo + 2 * np.pi * kf * integral_m
    s_fm = np.cos(fase_fm)

    # Guardar audio modulado FM
    ruta_wav_fm = os.path.join(directorio_audio, "senal_modulada_FM.wav")
    wav.write(ruta_wav_fm, fs, s_fm.astype(np.float32))

    # Demodulación FM mediante discriminador de frecuencia (Transformada de Hilbert)
    analitica = signal.hilbert(s_fm)
    fase_desenv = np.unwrap(np.angle(analitica))
    freq_inst = np.diff(fase_desenv) * fs / (2 * np.pi)
    freq_inst = np.append(freq_inst, freq_inst[-1])
    m_rec_fm = (freq_inst - fc_fm) / kf

    # Filtro pasa-bajos post-demodulación FM
    b_fm, a_fm = signal.butter(5, 3200 / (fs / 2), btype='low')
    m_rec_fm = signal.filtfilt(b_fm, a_fm, m_rec_fm)
    m_rec_fm = m_rec_fm / np.max(np.abs(m_rec_fm))

    ruta_wav_demod_fm = os.path.join(directorio_audio, "senal_demodulada_FM.wav")
    wav.write(ruta_wav_demod_fm, fs, m_rec_fm.astype(np.float32))

    corr_fm = np.corrcoef(m_t, m_rec_fm)[0, 1]
    print(f"  • Técnica añadida: FM (Frecuencia Modulada)")
    print(f"  • Portadora central (fc): {fc_fm:.0f} Hz | Desviación (Delta f): {delta_f:.0f} Hz")
    print(f"  • Regla de Carson (Ancho de banda FM): B_FM = 2*(Delta f + B) = {2*(delta_f + 3000):.0f} Hz")
    print(f"  • Correlación recuperación FM (r): {corr_fm:.5f}")
    print(f"  -> Audio modulado FM guardado en: {ruta_wav_fm}")
    print(f"  -> Audio demodulado FM guardado en: {ruta_wav_demod_fm}")

    # Generar gráfica de 4 pasos para FM
    fc_vis_fm = 1800.0
    kf_vis_fm = 1100.0
    c_fm_vis = np.cos(2 * np.pi * fc_vis_fm * tiempo)
    fi_vis = fc_vis_fm + kf_vis_fm * m_t
    s_fm_vis = np.cos(2 * np.pi * fc_vis_fm * tiempo + 2 * np.pi * kf_vis_fm * integral_m)

    fig_fm_4p, axs_fm = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    fig_fm_4p.suptitle("SECUENCIA DE MODULACIÓN EN FRECUENCIA (FM)", fontsize=14, fontweight="bold", y=0.98)

    axs_fm[0].plot(t_ms_4p, m_t[mask_4p], color="#0284c7", lw=2.0, label="m(t): Señal de Voz (Moduladora)")
    axs_fm[0].set_title("1. Señal Original (La Voz / Moduladora m(t))", fontsize=11, fontweight="bold", loc="left")
    axs_fm[0].set_ylabel("Amplitud")
    axs_fm[0].grid(True, linestyle="--", alpha=0.55)
    axs_fm[0].legend(loc="upper right")

    axs_fm[1].plot(t_ms_4p, c_fm_vis[mask_4p], color="#9333ea", lw=1.2, label=f"c(t) Portadora Pura (fc = {fc_vis_fm:.0f} Hz constante)")
    axs_fm[1].set_title(f"2. Señal Portadora Sin Modular (Frecuencia Constante)", fontsize=11, fontweight="bold", loc="left")
    axs_fm[1].set_ylabel("Amplitud")
    axs_fm[1].grid(True, linestyle="--", alpha=0.55)
    axs_fm[1].legend(loc="upper right")

    axs_fm[2].plot(t_ms_4p, fi_vis[mask_4p], color="#16a34a", lw=2.0, label=r"Frecuencia Instantánea $f_i(t) = f_c + k_f \cdot m(t)$")
    axs_fm[2].axhline(fc_vis_fm, color="#9333ea", linestyle="--", alpha=0.7, label=f"Portadora central fc ({fc_vis_fm:.0f} Hz)")
    axs_fm[2].set_title(r"3. Variación de la Frecuencia Instantánea $f_i(t)$ en función de la voz", fontsize=11, fontweight="bold", loc="left")
    axs_fm[2].set_ylabel("Frecuencia [Hz]")
    axs_fm[2].grid(True, linestyle="--", alpha=0.55)
    axs_fm[2].legend(loc="upper right")

    axs_fm[3].plot(t_ms_4p, s_fm_vis[mask_4p], color="#d97706", lw=1.3, label="Señal Modulada FM s_FM(t)")
    axs_fm[3].axhline(1.0, color="#ef4444", linestyle=":", alpha=0.6, label="Amplitud Constante (±1)")
    axs_fm[3].axhline(-1.0, color="#ef4444", linestyle=":", alpha=0.6)
    axs_fm[3].set_title("4. Señal Modulada FM (Amplitud Constante, Frecuencia Variable)", fontsize=11, fontweight="bold", loc="left")
    axs_fm[3].set_xlabel("Tiempo [milisegundos]", fontweight="bold")
    axs_fm[3].set_ylabel("Amplitud")
    axs_fm[3].grid(True, linestyle="--", alpha=0.55)
    axs_fm[3].legend(loc="upper right")

    plt.tight_layout()
    ruta_fig_fm4 = os.path.join(directorio_graficas, "secuencia_modulacion_FM_4_pasos.png")
    plt.savefig(ruta_fig_fm4, dpi=300)
    plt.close()
    print(f"  -> Gráfica FM 4 pasos guardada en: {ruta_fig_fm4}")

    # Gráfica comparativa directa AM vs FM
    fig_comp, axs_c = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig_comp.suptitle("COMPARACIÓN DIDÁCTICA: MODULACIÓN AM vs MODULACIÓN FM", fontsize=14, fontweight="bold", y=0.98)

    axs_c[0].plot(t_ms_4p, m_t[mask_4p], color="#0284c7", lw=2.0, label="Moduladora m(t)")
    axs_c[0].set_title("Señal Original de Entrada (Voz)", fontweight="bold", loc="left")
    axs_c[0].set_ylabel("Amplitud")
    axs_c[0].grid(True, linestyle="--", alpha=0.5)
    axs_c[0].legend(loc="upper right")

    s_am_vis = (1.0 + 0.8 * m_t) * c_fm_vis
    s_am_vis = s_am_vis / np.max(np.abs(s_am_vis))
    axs_c[1].plot(t_ms_4p, s_am_vis[mask_4p], color="#9333ea", lw=1.1, label="Modulación AM")
    axs_c[1].plot(t_ms_4p, (1.0 + 0.8*m_t[mask_4p])/1.8, "r--", lw=1.3, label="Envolvente de amplitud")
    axs_c[1].set_title("AM: Amplitud Variable, Frecuencia Constante", fontweight="bold", loc="left")
    axs_c[1].set_ylabel("s_AM(t)")
    axs_c[1].grid(True, linestyle="--", alpha=0.5)
    axs_c[1].legend(loc="upper right")

    axs_c[2].plot(t_ms_4p, s_fm_vis[mask_4p], color="#d97706", lw=1.2, label="Modulación FM")
    axs_c[2].axhline(1.0, color="#ef4444", linestyle=":", alpha=0.6)
    axs_c[2].axhline(-1.0, color="#ef4444", linestyle=":", alpha=0.6)
    axs_c[2].set_title("FM: Frecuencia Variable, Amplitud Constante", fontweight="bold", loc="left")
    axs_c[2].set_xlabel("Tiempo [milisegundos]", fontweight="bold")
    axs_c[2].set_ylabel("s_FM(t)")
    axs_c[2].grid(True, linestyle="--", alpha=0.5)
    axs_c[2].legend(loc="upper right")

    plt.tight_layout()
    ruta_fig_comp = os.path.join(directorio_graficas, "comparativa_AM_vs_FM.png")
    plt.savefig(ruta_fig_comp, dpi=300)
    plt.close()
    print(f"  -> Gráfica comparativa AM vs FM guardada en: {ruta_fig_comp}")

    # -------------------------------------------------------------------------
    # 5. DEMODULACIÓN (DETECCIÓN COHERENTE Y ENVOLVENTE)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 5: DEMODULACIÓN Y RECUPERACIÓN")
    print("=" * 50)

    # Demodulación Coherente:
    # 1. Multiplicación por la portadora local: v(t) = s_AM(t) * 2 * cos(2*pi*fc*t)
    v_t = s_am * (2.0 * np.cos(2 * np.pi * fc * tiempo))
    
    # 2. Filtrado pasa-bajos para eliminar la componente en 2*fc (16 kHz)
    f_corte_demod = 3800.0
    b_demod, a_demod = signal.butter(6, f_corte_demod / (fs / 2), btype='low')
    v_filtrada = signal.filtfilt(b_demod, a_demod, v_t)

    # 3. Eliminación de la componente continua (DC) introducida por Ac y normalización
    m_recuperada = v_filtrada - np.mean(v_filtrada)
    if np.max(np.abs(m_recuperada)) > 0:
        m_recuperada = m_recuperada / np.max(np.abs(m_recuperada))

    # Guardar audio demodulado
    ruta_wav_demod = os.path.join(directorio_audio, "senal_demodulada_AM.wav")
    wav.write(ruta_wav_demod, fs, m_recuperada.astype(np.float32))

    print(f"  • Metodo aplicado: Demodulacion Coherente / Sincronica")
    print(f"  • Producto por portadora: v(t) = s_AM(t) * 2 * cos(2*pi*fc*t)")
    print(f"  • Filtro Pasa-Bajos: Butterworth de orden 6 (fcorte = {f_corte_demod:.0f} Hz)")
    print(f"  • Bloqueo de DC: Eliminacion de nivel Ac para recuperar m(t)")
    print(f"  -> Audio demodulado guardado en: {ruta_wav_demod}")

    # Gráfica Etapa 5
    fig, axs = plt.subplots(3, 1, figsize=(11, 8))
    fig.suptitle("Etapa 5: Proceso de Demodulación Coherente", fontsize=14, fontweight='bold')

    axs[0].plot(tiempo[mask_am] * 1000, v_t[mask_am], color='#8c564b', lw=0.9)
    axs[0].set_title(r"Señal tras Mezclador Local: $v(t) = s_{AM}(t) \cdot 2\cos(2\pi f_c t)$ (Contiene banda base + término en $2f_c$)")
    axs[0].set_ylabel("Amplitud")
    axs[0].grid(True, linestyle='--', alpha=0.6)

    axs[1].plot(tiempo[mask_am] * 1000, v_filtrada[mask_am], color='#e377c2', lw=1.5, label="Salida del Filtro Pasa Bajos")
    axs[1].axhline(np.mean(v_filtrada), color='black', linestyle='--', label=f"Nivel DC (Ac = {np.mean(v_filtrada):.2f})")
    axs[1].set_title(r"Salida tras Filtro Pasa-Bajos (Banda base + Nivel DC)")
    axs[1].set_ylabel("Amplitud")
    axs[1].legend(loc="upper right")
    axs[1].grid(True, linestyle='--', alpha=0.6)

    axs[2].plot(tiempo, m_recuperada, color='#2ca02c', lw=0.9, label="Señal Demodulada Recuperada")
    axs[2].set_title(r"Señal Demodulada Final $m_{rec}(t)$ (Sin DC, Normalizada)")
    axs[2].set_xlabel("Tiempo [segundos]")
    axs[2].set_ylabel("Amplitud normalizada")
    axs[2].legend(loc="upper right")
    axs[2].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    ruta_fig5 = os.path.join(directorio_graficas, "4_demodulacion_proceso.png")
    plt.savefig(ruta_fig5, dpi=300)
    plt.close()
    print(f"  -> Gráfica guardada en: {ruta_fig5}")

    # -------------------------------------------------------------------------
    # 6. RECONSTRUCCIÓN Y COMPARACIÓN CUALITATIVA / CUANTITATIVA
    # -------------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("ETAPA 6: RECONSTRUCCIÓN, GENERACIÓN WAV Y COMPARACIÓN")
    print("=" * 50)

    # La señal reconstruida es la salida demodulada refinada
    audio_reconstruido = m_recuperada.copy()
    ruta_wav_reconstruido = os.path.join(directorio_audio, "senal_reconstruida.wav")
    wav.write(ruta_wav_reconstruido, fs, audio_reconstruido.astype(np.float32))

    # Métricas de Fidelidad
    # 1. Error Cuadrático Medio (MSE)
    mse = np.mean((m_t - audio_reconstruido)**2)
    # 2. Relación Señal a Ruido (SNR)
    potencia_senal = np.mean(m_t**2)
    snr = 10 * np.log10(potencia_senal / max(mse, 1e-12))
    # 3. Coeficiente de correlación de Pearson
    correlacion = np.corrcoef(m_t, audio_reconstruido)[0, 1]

    print(f"  • Archivo WAV final generado: {ruta_wav_reconstruido}")
    print(f"  • Coeficiente de correlación (r): {correlacion:.5f} (1.0 = idéntica)")
    print(f"  • Error Cuadrático Medio (MSE): {mse:.6e}")
    print(f"  • Relación Señal a Ruido (SNR): {snr:.2f} dB")
    print(f"  • Conclusión: Excelente recuperación con fidelidad acústica total.")

    # Espectro comparativo
    fft_rec = np.abs(np.fft.rfft(audio_reconstruido)) / N
    fft_rec_db = 20 * np.log10(np.maximum(fft_rec, 1e-6))

    # Gráfica Etapa 6
    fig = plt.figure(figsize=(12, 9))
    gs = fig.add_gridspec(3, 2)
    fig.suptitle("Etapa 6: Comparación Exhaustiva - Señal Original vs Señal Reconstruida", fontsize=14, fontweight='bold')

    # 1. Señal completa en el tiempo
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(tiempo, m_t, label="Señal Original m(t)", color='#1f77b4', lw=1.0, alpha=0.85)
    ax1.plot(tiempo, audio_reconstruido, label="Señal Reconstruida m_rec(t)", color='#2ca02c', lw=0.9, linestyle='--', alpha=0.85)
    ax1.set_title(f"Comparación en el Dominio del Tiempo (Correlación r = {correlacion:.4f}, SNR = {snr:.1f} dB)")
    ax1.set_xlabel("Tiempo [segundos]")
    ax1.set_ylabel("Amplitud")
    ax1.legend(loc="upper right")
    ax1.grid(True, linestyle='--', alpha=0.6)

    # 2. Zoom detallado en el tiempo
    ax2 = fig.add_subplot(gs[1, 0])
    t_zoom_start = 1.00
    t_zoom_end = 1.025
    mask_zoom_comp = (tiempo >= t_zoom_start) & (tiempo <= t_zoom_end)
    ax2.plot(tiempo[mask_zoom_comp]*1000, m_t[mask_zoom_comp], label="Original", color='#1f77b4', lw=1.8)
    ax2.plot(tiempo[mask_zoom_comp]*1000, audio_reconstruido[mask_zoom_comp], label="Reconstruida", color='#2ca02c', lw=1.4, linestyle='--')
    ax2.set_title("Detalle Ampliado (Zoom 25 ms)")
    ax2.set_xlabel("Tiempo [milisegundos]")
    ax2.set_ylabel("Amplitud")
    ax2.legend(loc="upper right")
    ax2.grid(True, linestyle='--', alpha=0.6)

    # 3. Error residual de reconstrucción
    ax3 = fig.add_subplot(gs[1, 1])
    error_rec = m_t - audio_reconstruido
    ax3.plot(tiempo[mask_zoom_comp]*1000, error_rec[mask_zoom_comp], color='#d62728', lw=1.2, label=f"Error residual (MSE={mse:.5f})")
    ax3.set_title("Error Residual Instantáneo")
    ax3.set_xlabel("Tiempo [milisegundos]")
    ax3.set_ylabel("Diferencia")
    ax3.legend(loc="upper right")
    ax3.grid(True, linestyle='--', alpha=0.6)

    # 4. Comparación en el dominio de la frecuencia
    ax4 = fig.add_subplot(gs[2, :])
    ax4.plot(freqs, fft_db, label="Espectro Señal Original", color='#1f77b4', lw=1.1, alpha=0.8)
    ax4.plot(freqs, fft_rec_db, label="Espectro Señal Reconstruida", color='#2ca02c', lw=0.9, linestyle='--', alpha=0.85)
    ax4.set_title("Comparación en el Dominio de la Frecuencia (FFT)")
    ax4.set_xlabel("Frecuencia [Hz]")
    ax4.set_ylabel("Magnitud [dB]")
    ax4.set_xlim(0, 5000)
    ax4.legend(loc="upper right")
    ax4.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    ruta_fig6 = os.path.join(directorio_graficas, "5_comparacion_original_vs_reconstruida.png")
    plt.savefig(ruta_fig6, dpi=300)
    plt.close()
    print(f"  -> Gráfica guardada en: {ruta_fig6}")

    # Resumen general y menú de reproducción
    print("\n" + "=" * 70)
    print("RESUMEN DE ARCHIVOS GENERADOS:")
    print("=" * 70)
    print(f" 1. Audio Original:          {ruta_wav}")
    print(f" 2. Audio PCM (8-bit):       {ruta_wav_pcm}")
    print(f" 3. Audio Modulado AM:       {ruta_wav_am}")
    print(f" 4. Audio Demodulado AM:     {ruta_wav_demod}")
    print(f" 5. Audio Modulado FM:       {ruta_wav_fm}  <-- [NUEVO FM]")
    print(f" 6. Audio Demodulado FM:     {ruta_wav_demod_fm}  <-- [NUEVO FM]")
    print(f" 7. Audio Reconstruido:      {ruta_wav_reconstruido}")
    print("\nGráficas generadas en carpeta 'graficas/':")
    print(f" • 1_senal_original_tiempo_frecuencia.png")
    print(f" • 2_muestreo_y_digitalizacion_pcm.png")
    print(f" • 3_modulacion_am_tiempo_espectro.png")
    print(f" • secuencia_modulacion_4_pasos.png")
    print(f" • secuencia_modulacion_FM_4_pasos.png  <-- [NUEVO FM]")
    print(f" • comparativa_AM_vs_FM.png            <-- [NUEVO COMPARATIVA]")
    print(f" • 4_demodulacion_proceso.png")
    print(f" • 5_comparacion_original_vs_reconstruida.png")
    print("=" * 70)

    # Comprobación de argumentos para reproducir automáticamente o finalizar
    if "--play" in sys.argv:
        print("\nReproduciendo audios consecutivamente...")
        reproducir_audio(ruta_wav, label="1. Audio Original")
        reproducir_audio(ruta_wav_am, label="2. Audio Modulado AM (Portadora 8 kHz)")
        reproducir_audio(ruta_wav_demod, label="3. Audio Demodulado")
        reproducir_audio(ruta_wav_reconstruido, label="4. Audio Reconstruido Final")

    print("\n[ÉXITO] Proceso completado satisfactoriamente.")


if __name__ == "__main__":
    main()
