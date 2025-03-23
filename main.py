import os
import re
import time
import threading
import json
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty


class DownloadMusicApp(App):
    # Propriedades para atualização da interface
    current_progress = StringProperty("")
    current_song = StringProperty("")
    
    def __init__(self, **kwargs):
        super(DownloadMusicApp, self).__init__(**kwargs)
        self.credentials_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
        self.client_id = ""
        self.client_secret = ""
        self.load_credentials()
        self.download_thread = None
        self.is_downloading = False
    
    def load_credentials(self):
        """ Carrega as credenciais do arquivo JSON se existir """
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    credentials = json.load(f)
                    self.client_id = credentials.get("client_id", "")
                    self.client_secret = credentials.get("client_secret", "")
            except Exception as e:
                print(f"Erro ao carregar credenciais: {str(e)}")
    
    def save_credentials(self):
        """ Salva as credenciais no arquivo JSON """
        try:
            credentials = {
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar credenciais: {str(e)}")
    
    def build(self):
        Window.clearcolor = (0.05, 0.1, 0.2, 1)
        
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Campos de entrada
        self.client_id_input = TextInput(hint_text="Client ID", multiline=False, text=self.client_id)
        self.client_secret_input = TextInput(hint_text="Client Secret", multiline=False, password=True, text=self.client_secret)
        self.playlist_url_input = TextInput(hint_text="Playlist URL", multiline=False)
        self.download_dir_input = TextInput(text="musicas_baixadas", multiline=False)

        # Botões de ação
        buttons_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 0.2))
        
        self.download_button = Button(text="Baixar Músicas", size_hint=(0.5, 1), padding=[20, 20])
        self.download_button.bind(on_press=self.start_download)
        
        self.cancel_button = Button(text="Cancelar", size_hint=(0.5, 1), padding=[20, 20])
        self.cancel_button.bind(on_press=self.cancel_download)
        self.cancel_button.disabled = True
        
        buttons_layout.add_widget(self.download_button)
        buttons_layout.add_widget(self.cancel_button)

        # Área de progresso
        self.progress_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=5)
        self.progress_label = Label(text="", font_size='16sp', halign='center', valign='middle')
        self.song_label = Label(text="", font_size='14sp', halign='center', valign='middle')
        self.progress_layout.add_widget(self.progress_label)
        self.progress_layout.add_widget(self.song_label)
        
        # Log de saída
        self.log_output = Label(text="", size_hint_y=None, markup=True)
        self.log_output.bind(texture_size=self.log_output.setter('size'))
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.scroll.add_widget(self.log_output)

        # Adiciona os widgets ao layout
        self.layout.add_widget(Label(text="Client ID:", color=(1, 1, 1, 1), size_hint_y=None, height=30))
        self.layout.add_widget(self.client_id_input)
        self.layout.add_widget(Label(text="Client Secret:", color=(1, 1, 1, 1), size_hint_y=None, height=30))
        self.layout.add_widget(self.client_secret_input)
        self.layout.add_widget(Label(text="Playlist URL:", color=(1, 1, 1, 1), size_hint_y=None, height=30))
        self.layout.add_widget(self.playlist_url_input)
        self.layout.add_widget(Label(text="Diretório de Download:", color=(1, 1, 1, 1), size_hint_y=None, height=30))
        self.layout.add_widget(self.download_dir_input)
        self.layout.add_widget(buttons_layout)
        self.layout.add_widget(self.progress_layout)
        self.layout.add_widget(self.scroll)

        return self.layout

    def log(self, message):
        """ Atualiza a interface com mensagens de log """
        def update_log(dt):
            self.log_output.text += f"\n{message}"
            self.scroll.scroll_y = 0  # Mantém o scroll no final
        
        # Usa o Clock para atualizar a UI no thread principal
        Clock.schedule_once(update_log, 0)
        
    def update_progress(self, current, total, song_name):
        """ Atualiza o progresso na interface """
        def update(dt):
            self.progress_label.text = f"Baixando {current}/{total}..."
            self.song_label.text = song_name
        
        # Usa o Clock para atualizar a UI no thread principal
        Clock.schedule_once(update, 0)

    def start_download(self, instance):
        """ Inicia o processo de download das músicas em uma thread separada """
        # Desabilita o botão para evitar múltiplos downloads
        self.download_button.disabled = True
        self.cancel_button.disabled = False
        self.is_downloading = True
        
        # Salva as credenciais se foram alteradas
        new_client_id = self.client_id_input.text.strip()
        new_client_secret = self.client_secret_input.text.strip()
        
        if new_client_id != self.client_id or new_client_secret != self.client_secret:
            self.client_id = new_client_id
            self.client_secret = new_client_secret
            self.save_credentials()
        
        # Inicia o download em uma thread separada
        self.download_thread = threading.Thread(target=self._download_process, daemon=True)
        self.download_thread.start()
        
    def cancel_download(self, instance):
        """ Cancela o processo de download em andamento """
        if self.is_downloading:
            self.is_downloading = False
            self.log("Download cancelado pelo usuário.")
            self.update_progress("", "", "")
            self.enable_download_button()
    
    def _download_process(self):
        """ Processo de download executado em uma thread separada """
        client_id = self.client_id_input.text.strip()
        client_secret = self.client_secret_input.text.strip()
        playlist_url = self.playlist_url_input.text.strip()
        download_dir = self.download_dir_input.text.strip()
        
        # Verifica se o download foi cancelado
        if not self.is_downloading:
            return

        if not client_id or not client_secret or not playlist_url:
            self.log("Preencha todos os campos antes de iniciar.")
            self.enable_download_button()
            return
            
        # Valida o formato da URL da playlist
        if not playlist_url.startswith("https://open.spotify.com/playlist/"):
            self.log("URL da Playlist inválida.")
            self.enable_download_button()
            return

        self.log("Conectando ao Spotify...")
        
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
            self.log("Conectado ao Spotify!")
        except Exception as e:
            self.log(f"Erro ao conectar ao Spotify: {str(e)}")
            self.enable_download_button()
            return

        # Obtendo músicas da playlist
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            playlist_info = sp.playlist(playlist_id)  # Obtém detalhes da playlist
            nome_playlist = playlist_info['name']

            musicas = []
            offset = 0
            limit = 100  # Spotify permite no máximo 100 por requisição

            while True:
                playlist_data = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                tracks = playlist_data["items"]

                if not tracks:
                    break  # Sai do loop quando não houver mais músicas

                for track in tracks:
                    if track["track"]:  # Evita possíveis erros com músicas removidas
                        musicas.append({
                            "nome": track["track"]["name"],
                            "artistas": ", ".join([artista["name"] for artista in track["track"]["artists"]]),
                            "query": f"{track['track']['name']} {', '.join([artista['name'] for artista in track['track']['artists']])}"
                        })

                offset += limit  # Atualiza o offset para buscar o próximo lote

            self.log(f"Playlist: {nome_playlist} ({len(musicas)} músicas)")

        except spotipy.exceptions.SpotifyException as e:
            # Verifica se é o erro HTTP 400 específico de ID inválido
            if "400" in str(e) and "Invalid base62 id" in str(e):
                self.log("URL da Playlist inválida.")
            else:
                self.log(f"Erro ao obter a playlist: {str(e)}")
            self.enable_download_button()
            return
        except Exception as e:
            self.log(f"Erro ao obter a playlist: {str(e)}")
            self.enable_download_button()
            return

        # Criando diretório de download
        pasta_playlist = os.path.join(download_dir, re.sub(r'[\\/*?:"<>|]', '', nome_playlist))
        os.makedirs(pasta_playlist, exist_ok=True)

        # Baixando músicas
        for i, musica in enumerate(musicas, 1):
            # Verifica se o download foi cancelado
            if not self.is_downloading:
                return
                
            nome_arquivo = re.sub(r'[\\/*?:"<>|]', '', f"{musica['artistas']} - {musica['nome']}")
            
            # Atualiza o progresso na interface
            self.update_progress(i, len(musicas), musica['nome'])
            self.log(f"\n[{i}/{len(musicas)}] Baixando: {nome_arquivo}...")

            if os.path.exists(os.path.join(pasta_playlist, nome_arquivo + ".mp3")):
                self.log(f"Já existe: {nome_arquivo}.mp3")
                continue

            if self.baixar_musica(musica["query"], pasta_playlist, nome_arquivo):
                self.log("Download concluído!")
                time.sleep(1)  # Reduzido para melhorar a responsividade
                
            # Verifica novamente se o download foi cancelado
            if not self.is_downloading:
                return

        if self.is_downloading:  # Só mostra a mensagem de finalização se não foi cancelado
            self.log("\nDownloads finalizados!")
        self.update_progress("", "", "")
        self.is_downloading = False
        self.enable_download_button()
        
    def enable_download_button(self):
        """ Reativa o botão de download e desativa o botão de cancelar """
        def enable(dt):
            self.download_button.disabled = False
            self.cancel_button.disabled = True
        Clock.schedule_once(enable, 0)

    def baixar_musica(self, query, download_path, nome_arquivo):
        """ Baixa uma música do YouTube e a converte para MP3 """
        output_template = os.path.join(download_path, f"{nome_arquivo}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',  # Qualidade de áudio desejada
            }],
            'postprocessor_args': ['-metadata', 'title=' + nome_arquivo],
            'noplaylist': True,
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f"ytsearch:{query}"])
                return True
            except Exception as e:
                print(f"Erro ao baixar {query}: {str(e)}")
                return False


if __name__ == "__main__":
    DownloadMusicApp().run()