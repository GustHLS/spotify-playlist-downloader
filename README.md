# 🎵 DownloaderPy - Spotify Playlist Downloader

DownloaderPy é uma aplicação desktop desenvolvida em Python que permite baixar músicas de playlists do Spotify utilizando o YouTube como fonte de áudio. A aplicação possui uma interface gráfica amigável construída com Kivy.

## ✨ Funcionalidades

- Baixar músicas completas de playlists do Spotify
- Interface gráfica intuitiva
- Salvar credenciais do Spotify para uso futuro
- Visualização em tempo real do progresso de download
- Possibilidade de cancelar downloads em andamento
- Organização automática das músicas em pastas por playlist

## 📋 Requisitos

- Python 3.6 ou superior
- FFmpeg (instruções de instalação abaixo)
- Credenciais de API do Spotify (Client ID e Client Secret)

## 🔧 Instalação

### 1. Clone o repositório ou baixe os arquivos

```
git clone https://github.com/seu-usuario/downloaderPy.git
cd downloaderPy
```

### 2. Instale as dependências

```
pip install -r requirements.txt
```

### 3. Instale o FFmpeg

O FFmpeg é necessário para converter os arquivos de áudio para o formato MP3. Siga os passos abaixo para instalá-lo no Windows:

1. Baixe o FFmpeg do link: [https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z)
2. Extraia o arquivo 7z para um local permanente (ex: `C:\Program Files\ffmpeg`)
3. Configure as variáveis de ambiente do Windows:
   - Clique com o botão direito em "Este Computador" ou "Meu Computador" e selecione "Propriedades"
   - Clique em "Configurações avançadas do sistema"
   - Clique no botão "Variáveis de Ambiente"
   - Na seção "Variáveis do sistema", encontre a variável "Path" e clique em "Editar"
   - Clique em "Novo" e adicione o caminho para a pasta bin do FFmpeg (ex: `C:\Program Files\ffmpeg\bin`)
   - Clique em "OK" para fechar todas as janelas

4. Verifique a instalação abrindo um novo prompt de comando e digitando:
   ```
   ffmpeg -version
   ```

## 🔑 Configuração da API do Spotify

Para usar esta aplicação, você precisa de credenciais da API do Spotify:

1. Acesse [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Faça login com sua conta do Spotify
3. Crie um novo aplicativo
4. Obtenha o Client ID e Client Secret
5. Insira essas credenciais na aplicação

## 🚀 Como usar

1. Execute o programa:
   ```
   python main.py
   ```

2. Insira seu Client ID e Client Secret do Spotify
3. Cole a URL da playlist do Spotify que deseja baixar
4. Defina o diretório de download (ou use o padrão)
5. Clique em "Baixar Músicas"
6. Aguarde o download ser concluído

## 📝 Detalhes da Implementação

O arquivo `main.py` contém toda a lógica da aplicação:

- **Classe DownloadMusicApp**: Classe principal que herda de `App` do Kivy
- **Interface Gráfica**: Construída com widgets do Kivy (BoxLayout, TextInput, Button, etc.)
- **Gerenciamento de Credenciais**: Salva e carrega credenciais do Spotify em um arquivo JSON
- **Processo de Download**: Executado em uma thread separada para não bloquear a interface
- **Conexão com Spotify**: Utiliza a biblioteca `spotipy` para acessar a API do Spotify
- **Download de Músicas**: Utiliza `yt_dlp` para buscar e baixar músicas do YouTube
- **Conversão para MP3**: Utiliza FFmpeg (via yt_dlp) para converter os arquivos para MP3

## ⚠️ Observações

- Use esta aplicação apenas para baixar conteúdo que você tem direito de acessar
- Respeite os direitos autorais e os termos de serviço das plataformas
- A aplicação é para uso educacional e pessoal

## 📜 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.