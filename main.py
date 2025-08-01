from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import subprocess
import os
import glob

app = FastAPI()

DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "youtube.com_cookies.txt"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def limpar_downloads_antigos(ext):
    # Remove arquivos antigos do tipo ext para evitar confusão
    arquivos = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"*.{ext}"))
    for arq in arquivos:
        try:
            os.remove(arq)
        except:
            pass

def baixar_audio(video_url: str):
    limpar_downloads_antigos("mp3")
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--cookies", COOKIE_FILE,
        "-o", output_template,
        video_url
    ]

    subprocess.run(command, check=True)

    # Depois de baixar, pegar o arquivo mp3 mais recente na pasta
    arquivos = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*.mp3"))
    if not arquivos:
        raise Exception("Erro: arquivo mp3 não encontrado após download.")
    arquivo_baixado = max(arquivos, key=os.path.getctime)
    return arquivo_baixado

def baixar_video(video_url: str):
    limpar_downloads_antigos("mp4")
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

    command = [
        "yt-dlp",
        "-f", "best[ext=mp4]",
        "--cookies", COOKIE_FILE,
        "-o", output_template,
        video_url
    ]

    subprocess.run(command, check=True)

    arquivos = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*.mp4"))
    if not arquivos:
        raise Exception("Erro: arquivo mp4 não encontrado após download.")
    arquivo_baixado = max(arquivos, key=os.path.getctime)
    return arquivo_baixado

@app.get("/baixar/audio")
def route_audio(url: str = Query(...)):
    try:
        caminho = baixar_audio(url)
        return FileResponse(caminho, filename=os.path.basename(caminho))
    except Exception as e:
        return {"erro": str(e)}

@app.get("/baixar/video")
def route_video(url: str = Query(...)):
    try:
        caminho = baixar_video(url)
        return FileResponse(caminho, filename=os.path.basename(caminho))
    except Exception as e:
        return {"erro": str(e)}

