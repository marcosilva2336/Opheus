import os
from tkinter import Tk, Label, Button, Text, Scrollbar, END, filedialog, messagebox, Entry, Frame
import yt_dlp
from threading import Thread
from PIL import Image
import aiohttp
import asyncio
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, TCON
import subprocess
import re

# Adicionando FFmpeg ao PATH dentro do código
os.environ["PATH"] = r"C:\ffmpeg-7.1-essentials_build\ffmpeg-7.1-essentials_build\bin" + ";" + os.environ["PATH"]

def convert_to_mp3(input_file, output_file):
    """
    Converte um arquivo de áudio para o formato mp3 usando ffmpeg.
    """
    command = [r"C:\ffmpeg-7.1-essentials_build\ffmpeg-7.1-essentials_build\bin\ffmpeg", '-i', input_file, '-q:a', '0', output_file]
    subprocess.run(command, check=True)

async def fetch_thumbnail(session, url):
    async with session.get(url) as response:
        return await response.read()

async def download_audio(urls, output_folder):
    """
    Faz o download do áudio em formato mp3 de uma lista de URLs do YouTube.
    Usa yt-dlp para baixar o áudio e salva a capa da música.
    """
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                    'quiet': False,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    if not info_dict:
                        log_text.insert(END, f"❌ Não foi possível extrair informações de: {url}\n")
                        continue

                    title = info_dict.get('title', None)
                    artist = info_dict.get('artist', None) or info_dict.get('uploader', None)
                    album = info_dict.get('album', None)
                    year = info_dict.get('release_year', None)
                    genre = info_dict.get('genre', None)
                    thumbnail_url = info_dict.get('thumbnail', None)

                    # Tentar extrair informações adicionais da descrição do vídeo
                    description = info_dict.get('description', '')
                    if not album:
                        album_match = re.search(r'Álbum: (.+)', description)
                        if album_match:
                            album = album_match.group(1)
                    if not genre:
                        genre_match = re.search(r'Gênero: (.+)', description)
                        if genre_match:
                            genre = genre_match.group(1)
                    if not year:
                        year_match = re.search(r'Ano: (\d{4})', description)
                        if year_match:
                            year = year_match.group(1)

                    if not title or not artist:
                        log_text.insert(END, f"❌ Falta informações importantes do vídeo: {url}\n")
                        continue

                    log_text.insert(END, f"✔️ Informações extraídas para o vídeo: {title} - {artist}\n")

                    img_path = None
                    if thumbnail_url:
                        img_data = await fetch_thumbnail(session, thumbnail_url)
                        img = Image.open(BytesIO(img_data))
                        img_path = os.path.join(output_folder, f"{title}_cover.jpg")
                        img.save(img_path)

                    ydl.download([url])

                    audio_file_path = os.path.join(output_folder, f"{title}.mp3")
                    if not os.path.exists(audio_file_path):
                        log_text.insert(END, f"❌ Arquivo {title}.mp3 não foi baixado corretamente.\n")
                        continue

                    audio = MP3(audio_file_path, ID3=ID3)
                    if audio.tags is None:
                        audio.add_tags()

                    audio.tags.add(TIT2(encoding=3, text=title))
                    audio.tags.add(TPE1(encoding=3, text=artist))
                    audio.tags.add(TALB(encoding=3, text=album if album else 'Unknown Album'))
                    audio.tags.add(TDRC(encoding=3, text=str(year) if year else 'Unknown Year'))
                    if genre:
                        audio.tags.add(TCON(encoding=3, text=genre))

                    if img_path:
                        with open(img_path, "rb") as img_file:
                            cover_data = img_file.read()
                            audio.tags.add(APIC(
                                encoding=3,
                                mime='image/jpeg',
                                type=3,
                                desc=u'Cover',
                                data=cover_data
                            ))

                        audio.save()

                    validation_log = validate_metadata(audio)
                    log_text.insert(END, f"✔️ Download concluído: {title} - {artist}\n")
                    log_text.insert(END, validation_log)

                    if img_path:
                        log_text.insert(END, f"📸 Capa salva como: {img_path}\n")
            except Exception as e:
                log_text.insert(END, f"❌ Erro ao baixar {url}: {e}\n")
    
    log_text.insert(END, "🟢 Todos os downloads concluídos!\n")

def validate_metadata(audio):
    """
    Função que valida as metadatas de um arquivo MP3.
    """
    validation_log = ""
    try:
        title = audio.tags.get('TIT2', None)
        artist = audio.tags.get('TPE1', None)
        album = audio.tags.get('TALB', None)
        year = audio.tags.get('TDRC', None)
        genre = audio.tags.get('TCON', None)

        if not title:
            validation_log += "❌ Título não encontrado.\n"
        else:
            validation_log += f"✔️ Título: {title}\n"

        if not artist:
            validation_log += "❌ Artista não encontrado.\n"
        else:
            validation_log += f"✔️ Artista: {artist}\n"

        if not album:
            validation_log += "❌ Álbum não encontrado.\n"
        else:
            validation_log += f"✔️ Álbum: {album}\n"

        if not year:
            validation_log += "❌ Ano não encontrado.\n"
        else:
            validation_log += f"✔️ Ano: {year}\n"

        if not genre:
            validation_log += "❌ Gênero não encontrado.\n"
        else:
            validation_log += f"✔️ Gênero: {genre}\n"

        cover = audio.tags.getall('APIC')
        if cover:
            validation_log += "✔️ Capa encontrada.\n"
        else:
            validation_log += "❌ Capa não encontrada.\n"

    except Exception as e:
        validation_log = f"❌ Erro na validação das metadatas: {e}\n"
    
    return validation_log

def update_metadata():
    """
    Função para atualizar os metadados de um arquivo MP3 existente.
    """
    file_path = filedialog.askopenfilename(title="Selecione o arquivo MP3", filetypes=[("MP3 Files", "*.mp3")])
    if not file_path:
        return

    global audio
    audio = MP3(file_path, ID3=ID3)

    title_entry.delete(0, END)
    title_entry.insert(0, audio.tags.get('TIT2', ''))

    artist_entry.delete(0, END)
    artist_entry.insert(0, audio.tags.get('TPE1', ''))

    album_entry.delete(0, END)
    album_entry.insert(0, audio.tags.get('TALB', ''))

    year_entry.delete(0, END)
    year_entry.insert(0, audio.tags.get('TDRC', ''))

    genre_entry.delete(0, END)
    genre_entry.insert(0, audio.tags.get('TCON', ''))

    update_button.config(text="Atualizar Metadados", command=save_metadata)

    frame_download.grid_remove()
    frame_update.grid(row=0, column=0, padx=10, pady=10)

def save_metadata():
    """
    Função para salvar os metadados atualizados no arquivo MP3.
    """
    global audio
    audio.tags.add(TIT2(encoding=3, text=title_entry.get()))
    audio.tags.add(TPE1(encoding=3, text=artist_entry.get()))
    audio.tags.add(TALB(encoding=3, text=album_entry.get()))
    audio.tags.add(TDRC(encoding=3, text=year_entry.get()))
    audio.tags.add(TCON(encoding=3, text=genre_entry.get()))

    audio.save()
    messagebox.showinfo("Sucesso", "Metadados atualizados com sucesso!")

    update_button.config(text="Selecionar MP3 para Atualizar Metadados", command=update_metadata)

    frame_update.grid_remove()
    frame_download.grid(row=0, column=0, padx=10, pady=10)

def start_download():
    """
    Função chamada ao clicar no botão de download. Lê URLs e inicia o download.
    """
    urls = urls_input.get("1.0", END).strip().split("\n")
    urls = [url.strip() for url in urls if url.strip()]

    if not urls:
        messagebox.showwarning("Aviso", "Por favor, insira pelo menos uma URL!")
        return

    output_folder = filedialog.askdirectory(title="Selecione a pasta de destino")
    if not output_folder:
        messagebox.showwarning("Aviso", "Por favor, selecione uma pasta de destino!")
        return

    log_text.insert(END, "🔵 Iniciando downloads...\n")
    Thread(target=run_asyncio_download, args=(urls, output_folder)).start()

def run_asyncio_download(urls, output_folder):
    asyncio.run(download_audio(urls, output_folder))

# Interface Gráfica
app = Tk()
app.title("Opheus - YouTube Audio Downloader")
app.geometry("700x600")
app.resizable(False, False)

# Frame para download
frame_download = Frame(app)
frame_download.grid(row=0, column=0, padx=10, pady=10)

Label(frame_download, text="Insira as URLs do YouTube (uma por linha):", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

# Caixa de texto para as URLs
urls_input = Text(frame_download, height=10, width=70, font=("Arial", 12))
urls_input.grid(row=1, column=0, columnspan=2, pady=10)

# Adicionando a barra de rolagem
scrollbar = Scrollbar(frame_download, command=urls_input.yview)
scrollbar.grid(row=1, column=2, sticky='ns')
urls_input.config(yscrollcommand=scrollbar.set)

# Botão de download
Button(frame_download, text="Iniciar Download", font=("Arial", 14), command=start_download).grid(row=2, column=0, columnspan=2, pady=20)

# Caixa de log
log_text = Text(frame_download, height=10, width=70, wrap="word")
log_text.grid(row=3, column=0, columnspan=2, pady=10)

scrollbar = Scrollbar(frame_download, command=log_text.yview)
scrollbar.grid(row=3, column=2, sticky='ns')
log_text.config(yscrollcommand=scrollbar.set)

# Botão para mudar para o frame de atualização de metadados
Button(frame_download, text="Atualizar Metadados de MP3", font=("Arial", 14), command=update_metadata).grid(row=4, column=0, columnspan=2, pady=10)

# Frame para atualização de metadados
frame_update = Frame(app)

Label(frame_update, text="Título:", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky='e')
title_entry = Entry(frame_update, font=("Arial", 12))
title_entry.grid(row=0, column=1, pady=5, sticky='w')

Label(frame_update, text="Artista:", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky='e')
artist_entry = Entry(frame_update, font=("Arial", 12))
artist_entry.grid(row=1, column=1, pady=5, sticky='w')

Label(frame_update, text="Álbum:", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky='e')
album_entry = Entry(frame_update, font=("Arial", 12))
album_entry.grid(row=2, column=1, pady=5, sticky='w')

Label(frame_update, text="Ano:", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky='e')
year_entry = Entry(frame_update, font=("Arial", 12))
year_entry.grid(row=3, column=1, pady=5, sticky='w')

Label(frame_update, text="Gênero:", font=("Arial", 12)).grid(row=4, column=0, pady=5, sticky='e')
genre_entry = Entry(frame_update, font=("Arial", 12))
genre_entry.grid(row=4, column=1, pady=5, sticky='w')

# Botão para selecionar e atualizar metadados de um arquivo MP3 existente
update_button = Button(frame_update, text="Selecionar MP3 para Atualizar Metadados", font=("Arial", 14), command=update_metadata)
update_button.grid(row=5, column=0, columnspan=2, pady=10)

# Garantir que o layout da janela está bem configurado
app.mainloop()