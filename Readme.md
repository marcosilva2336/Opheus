# Opheus - YouTube Audio Downloader

Opheus é uma aplicação que permite baixar áudio de vídeos do YouTube e atualizar os metadados de arquivos MP3. A aplicação utiliza a biblioteca `yt-dlp` para extrair informações dos vídeos do YouTube e baixar o áudio, e a biblioteca `mutagen` para manipular os metadados dos arquivos MP3.

## Funcionalidades

- **Download de Áudio do YouTube**: Baixa o áudio de vídeos do YouTube no formato MP3.
- **Atualização de Metadados**: Permite atualizar os metadados de arquivos MP3 existentes, incluindo título, artista, álbum, ano, gênero e capa do álbum.
- **Interface Gráfica**: Interface gráfica amigável construída com `tkinter`.

## Requisitos

- Python 3.x
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
    ```sh
    git clone https://github.com/seu-usuario/opheus.git
    cd opheus
    ```

2. Crie um ambiente virtual e ative-o:
    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. Instale as dependências:
    ```sh
    pip install -r requirements.txt
    ```

## Uso

1. Execute o script:
    ```sh
    python Opheus.py
    ```

2. **Baixar Áudio do YouTube**:
    - Insira as URLs dos vídeos do YouTube que deseja baixar na caixa de texto.
    - Clique no botão "Iniciar Download".
    - O áudio será baixado e os metadados serão extraídos automaticamente.

3. **Atualizar Metadados de MP3**:
    - Clique no botão "Atualizar Metadados de MP3".
    - Selecione o arquivo MP3 que deseja atualizar.
    - Preencha os campos desejados e clique no botão "Atualizar Metadados".

## Estrutura do Código

### Funções Principais

- [convert_to_mp3(input_file, output_file)](http://_vscodecontentref_/1): Converte um arquivo de áudio para o formato MP3 usando `ffmpeg`.
- `fetch_thumbnail(session, url)`: Faz o download da miniatura do vídeo de forma assíncrona.
- `download_audio(urls, output_folder)`: Faz o download do áudio em formato MP3 de uma lista de URLs do YouTube e salva a capa da música.
- `validate_metadata(audio)`: Valida os metadatas de um arquivo MP3.
- `update_metadata()`: Atualiza os metadados de um arquivo MP3 existente.
- `save_metadata()`: Salva os metadados atualizados no arquivo MP3.
- `start_download()`: Lê URLs e inicia o download.
- `run_asyncio_download(urls, output_folder)`: Executa o loop de eventos [asyncio](http://_vscodecontentref_/2) para baixar o áudio.

### Interface Gráfica

A interface gráfica é construída usando [tkinter](http://_vscodecontentref_/3) e inclui:
- Uma caixa de texto para inserir URLs do YouTube.
- Um botão para iniciar o download.
- Uma caixa de log para exibir mensagens de status.
- Um botão para atualizar metadados de arquivos MP3.
- Campos de entrada para atualizar título, artista, álbum, ano e gênero de arquivos MP3.

## Dependências

- `yt-dlp`: Biblioteca para baixar vídeos do YouTube.
- `Pillow`: Biblioteca para manipulação de imagens.
- `requests`: Biblioteca para fazer requisições HTTP.
- [mutagen](http://_vscodecontentref_/4): Biblioteca para manipulação de metadados de arquivos de mídia.
- [aiohttp](http://_vscodecontentref_/5): Biblioteca para fazer requisições HTTP assíncronas.

## Contribuição

1. Faça um fork do projeto.
2. Crie uma nova branch (`git checkout -b feature/nova-funcionalidade`).
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova funcionalidade'`).
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.