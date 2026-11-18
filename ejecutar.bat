@echo off
chcp 65001 > nul
title Proyecto Comunicaciones 1 - Simulador y Procesamiento de Voz

:menu
cls
echo ======================================================================
echo    PROYECTO COMUNICACIONES 1: NOTA DE VOZ 
echo ======================================================================
echo.
echo  [1] Abrir Interfaz Gráfica de Escritorio (Sliders y osciloscopio en vivo)
echo  [2] Abrir Laboratorio Web Interactivo en el Navegador (HTML5 + Web Audio)
echo  [3] Abrir Cuaderno Interactivo Jupyter Notebook (.ipynb)
echo  [4] Re-ejecutar Análisis y Regenerar todas las Gráficas y Audios WAV
echo.
echo  --- REPRODUCCIÓN DIRECTA DE AUDIOS ---
echo  [5] Escuchar Audio Original ("Just do it")
echo  [6] Escuchar Señal Digitalizada PCM (8 bits)
echo  [7] Escuchar Señal Modulada AM (Portadora 8 kHz)
echo  [8] Escuchar Señal Demodulada AM
echo  [9] Escuchar Señal Modulada FM (Frecuencia Modulada) [NUEVO]
echo  [10] Escuchar Señal Demodulada FM [NUEVO]
echo  [11] Escuchar Señal Reconstruida Final
echo.
echo  [0] Salir
echo ======================================================================
set /p opcion="Seleccione una opción (0-11): "

if "%opcion%"=="1" (
    echo.
    echo Iniciando Interfaz Gráfica interactiva de escritorio...
    py -3.13 interfaz_interactiva.py
    goto menu
)
if "%opcion%"=="2" (
    echo.
    echo Abriendo Laboratorio Web en el navegador predeterminado...
    start visualizador_interactivo.html
    goto menu
)
if "%opcion%"=="3" (
    echo.
    echo Iniciando Jupyter Notebook...
    py -3.13 -m jupyter notebook procesamiento_voz.ipynb
    goto menu
)
if "%opcion%"=="4" (
    echo.
    echo Ejecutando procesamiento completo...
    py -3.13 procesamiento_voz.py
    pause
    goto menu
)
if "%opcion%"=="5" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\just_do_it.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="6" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\senal_digitalizada_pcm_8bits.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="7" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\senal_modulada_AM.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="8" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\senal_demodulada_AM.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="9" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\senal_modulada_FM.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="10" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\senal_demodulada_FM.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="11" (
    powershell -c "(New-Object Media.SoundPlayer 'audio\senal_reconstruida.wav').PlaySync()"
    goto menu
)
if "%opcion%"=="0" (
    exit
)

goto menu
