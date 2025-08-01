from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import glob
from urllib.parse import urlparse, urlunparse

app = FastAPI()

DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "youtube.com_cookies.txt"

# Criar pasta de downloads se não existir
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ✅ Recriar o arquivo cookies a partir da variável de ambiente
cookies_env = os.getenv("YT_COOKIES")
if cookies_env:
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookies_env)

# ✅ Função para limpar parâmetros extras da URL
def limpar_url(url: str) -> str:
    parsed = urlparse(url)
    url_limpa = urlunparse(parsed._replace(query=''))
    return url_limpa

def limpar_downloads_antigos(ext):
    arquivos = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"*.{ext}"))
    for arq in arquivos:
        try:
            os.remove(arq)
        except:
            pass

def baixar_audio(video_url: str):
    limpar_downloads_antigos("mp3")
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

    # ✅ Limpar URL
    video_url = limpar_url(video_url)

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

    arquivos = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*.mp3"))
    if not arquivos:
        raise Exception("Erro: arquivo mp3 não encontrado após download.")
    arquivo_baixado = max(arquivos, key=os.path.getctime)
    return arquivo_baixado

def baixar_video(video_url: str):
    limpar_downloads_antigos("mp4")
    output_template = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

    # ✅ Limpar URL
    video_url = limpar_url(video_url)

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

@app.get("/")
def home():
    return JSONResponse(content={"mensagem": "Servidor online. Use /baixar/audio ou /baixar/video com ?url="})

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

