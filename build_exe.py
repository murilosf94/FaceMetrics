import PyInstaller.__main__
import mediapipe as mp
import os

# Localiza a pasta do mediapipe
mp_path = os.path.dirname(mp.__file__)

PyInstaller.__main__.run([
    'FaceMetrics.py', # Troque pelo nome do seu arquivo principal
    '--onefile',     # Gera apenas um arquivo .exe
    '--windowed',    # Não abre o console preto ao iniciar
    f'--add-data={mp_path};mediapipe/',
    '--icon=./icone/logofacemetrics.ico', # Substitua pelo caminho do seu ícone, se desejar
    '--name=FaceMetrics', # Nome do seu executável
])