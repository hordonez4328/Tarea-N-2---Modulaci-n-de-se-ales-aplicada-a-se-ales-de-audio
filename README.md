# Tarea Nº 2 - Modulación de señales aplicada a señales de audio.

Este repositorio  enfocado en la adquisición, análisis en el dominio del tiempo y la frecuencia, muestreo y digitalización (PCM), modulación analógica en amplitud (AM) y frecuencia (FM), demodulación coherente y reconstrucción de una señal de audio real (frase *"Just do it"*, ~2.38 segundos).

---

##  Contenido del Proyecto

1. **Grabación y Adquisición:**
   - Señal original en audio/video decodificada a WAV PCM 16-bit mono ($f_s = 48{,}000\text{ Hz}$).
2. **Análisis de Señal:**
   - Dominio del tiempo y Transformada Rápida de Fourier (FFT).
   - Cálculo del ancho de banda de energía al 99% ($B_{99\%} \approx 3{,}200\text{ Hz}$).
3. **Muestreo y Digitalización (PCM):**
   - Discretización temporal $x[n]$.
   - Cuantización uniforme de 8 bits ($L = 256$ niveles).
   - Cálculo del ruido de cuantización y relación señal a ruido de cuantización ($\text{SQNR} \approx 47.9\text{ dB}$).
4. **Modulación en Amplitud (AM - 4 Pasos):**
   - Moduladora $m(t)$ (voz).
   - Portadora $c(t)$ a $f_c = 8\text{ kHz}$.
   - Portadora con envolvente superpuesta ($1 + k_a m(t)$).
   - Señal resultante modulada $s_{\text{AM}}(t)$ con índice $k_a = 0.8$.
5. **Modulación en Frecuencia (FM - 4 Pasos):**
   - Moduladora $m(t)$ y Portadora $c(t)$ a $f_c = 6\text{ kHz}$.
   - Variación de la Frecuencia Instantánea $f_i(t) = f_c + k_f m(t)$ con $\Delta f = 2{,}500\text{ Hz}$.
   - Señal modulada $s_{\text{FM}}(t)$ de amplitud rigurosamente constante con ciclos comprimidos y dilatados.
6. **Demodulación y Reconstrucción:**
   - **Demodulación AM:** Mezclador coherente + filtro pasabajo Butterworth de 5.º orden + bloqueo DC.
   - **Demodulación FM:** Discriminador mediante transformada analítica de Hilbert + diferenciación de fase instantánea + filtro pasabajo.
   - **Métricas de Fidelidad:** Correlación de Pearson ($r > 0.99$), Error Cuadrático Medio ($\text{MSE}$) y relación $\text{SNR}$.

---

##  Estructura del Repositorio

```text
├── audio/                                   # Archivos de audio WAV de cada etapa
│   ├── just_do_it.wav                       # Audio original normalizado
│   ├── senal_digitalizada_pcm_8bits.wav     # Audio cuantizado a 8 bits
│   ├── senal_modulada_AM.wav                # Señal modulada en amplitud
│   ├── senal_demodulada_AM.wav              # Audio recuperado de AM
│   ├── senal_modulada_FM.wav                # Señal modulada en frecuencia
│   ├── senal_demodulada_FM.wav              # Audio recuperado de FM (r = 0.996)
│   └── senal_reconstruida.wav               # Audio final reconstruido
├── graficas/                                # Figuras exportadas en alta resolución (300 DPI)
│   ├── 1_senal_original_tiempo_frecuencia.png
│   ├── 2_muestreo_y_digitalizacion_pcm.png
│   ├── 3_modulacion_am_tiempo_espectro.png
│   ├── secuencia_modulacion_4_pasos.png
│   ├── secuencia_modulacion_FM_4_pasos.png
│   ├── comparativa_AM_vs_FM.png
│   ├── 4_demodulacion_proceso.png
│   └── 5_comparacion_original_vs_reconstruida.png
├── procesamiento_voz.py                     # Script CLI principal con todo el pipeline
├── interfaz_interactiva.py                  # Interfaz gráfica de escritorio (Tkinter + Matplotlib)
├── visualizador_interactivo.html            # Dashboard web interactivo (Web Audio API + Canvas)
├── procesamiento_voz.ipynb                  # Jupyter Notebook completo con fórmulas y audios
├── ejecutar.bat                             # Menú rápido para Windows
├── requirements.txt                         # Dependencias del proyecto
└── README.md                                # Documentación del proyecto
```

---

##  Instalación y Requisitos

Se requiere Python 3.10 o superior (recomendado Python 3.13):

```bash
pip install -r requirements.txt
```

---

##  Formas de Ejecución

### Opción 1: Menú Automático en Windows
Haz doble clic sobre el archivo `ejecutar.bat` para acceder al menú interactivo:
- `1`: Abrir la interfaz gráfica interactiva de escritorio.
- `2`: Abrir el visualizador interactivo en tu navegador web.
- `3`: Abrir el Jupyter Notebook.
- `4`: Ejecutar el script CLI completo.
- `5 - 11`: Reproducir directamente cualquiera de los 7 audios del proyecto.

### Opción 2: Simulador Web en el Navegador
Abre el archivo `visualizador_interactivo.html` en cualquier navegador web moderno o sirve la carpeta localmente:
```bash
python -m http.server 8000
```
Y visita [http://localhost:8000/visualizador_interactivo.html](http://localhost:8000/visualizador_interactivo.html).

### Opción 3: Interfaz Gráfica de Escritorio (GUI)
```bash
python interfaz_interactiva.py
```

### Opción 4: Pipeline Completo por Consola (CLI)
```bash
python procesamiento_voz.py
```

---

## Métricas de Desempeño Obtenidas

| Etapa | Métrica | Valor Obtenido | Calidad |
| :--- | :--- | :--- | :--- |
| **PCM (8 bits)** | $\text{SQNR}$ | **$47.9\text{ dB}$** | Excelente inteligibilidad |
| **Demodulación AM** | Correlación ($r$) | **$0.9987$** | Reconstrucción casi idéntica |
| **Demodulación FM** | Correlación ($r$) | **$0.9963$** | Alta fidelidad sonora |
| **Reconstrucción Final**| $\text{MSE}$ | **$5.07 \times 10^{-4}$** | Distorsión imperceptible |

---

## Autor
- **Harold Ordoñez** - *Universidad Tecnológica de Pereira (UTP)*
