import sys
import os
import config
from api_clients import ApiClients
from mutagen import File as MutagenFile
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLabel, QMessageBox, 
                               QTabWidget, QFileDialog, QDateTimeEdit, QSizePolicy)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ScrobblerApp(QMainWindow):
    def __init__(self, api_handler: ApiClients):
        super().__init__()
        self.api_handler = api_handler
        self.setWindowTitle("Manual Discogs Scrobbler")
        self.setWindowIcon(QIcon(resource_path("favicon.ico")))
        
        self.resize(900, 600)
        center_point = QApplication.primaryScreen().availableGeometry().center()
        self.move(center_point - self.frameGeometry().center())

        self.tab_widget = QTabWidget()
        self.manual_tab = QWidget()
        self.files_tab = QWidget()
        self.tab_widget.addTab(self.manual_tab, "DISCOGS")
        self.tab_widget.addTab(self.files_tab, "FILES")
        self.setCentralWidget(self.tab_widget)

        self.setup_manual_tab()
        self.setup_files_tab()

    def _create_track_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["", "#", "ARTIST", "ALBUM", "TITLE", "DURATION"])
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(5, 70)
        return table

    def _create_time_layout(self) -> tuple[QHBoxLayout, QDateTimeEdit]:
        time_layout = QHBoxLayout()
        time_label = QLabel("Scrobble End Time:")
        time_edit = QDateTimeEdit()
        time_edit.setCalendarPopup(True)
        time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        time_edit.setDateTime(QDateTime.currentDateTime())
        set_time_button = QPushButton("SET CURRENT TIME")

        time_layout.addWidget(time_label)
        time_layout.addWidget(time_edit)
        time_layout.addWidget(set_time_button)
        time_layout.addStretch()
        
        set_time_button.clicked.connect(
            lambda: time_edit.setDateTime(QDateTime.currentDateTime())
        )
        return time_layout, time_edit

    def setup_manual_tab(self):
        self.release_id_input = QLineEdit()
        self.release_id_input.setPlaceholderText("Enter full release ID, e.g. [r123456789]")
        self.fetch_button = QPushButton("IMPORT")
        self.clear_button = QPushButton("CLEAR")
        self.scrobble_button = QPushButton("SCROBBLE")
        
        self.track_table = self._create_track_table()
        time_layout, self.manual_time_edit = self._create_time_layout()

        central_layout = QVBoxLayout(self.manual_tab)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.release_id_input)
        input_layout.addWidget(self.fetch_button)
        input_layout.addWidget(self.clear_button)

        central_layout.addLayout(input_layout)
        central_layout.addWidget(self.track_table)
        central_layout.addLayout(time_layout)
        central_layout.addWidget(self.scrobble_button)

        self.artist_name = ""
        self.album_title = ""
        self.fetch_button.clicked.connect(self.fetch_release_data)
        self.scrobble_button.clicked.connect(self.scrobble_tracks)
        self.clear_button.clicked.connect(self.clear_data)

    def setup_files_tab(self):
        layout = QVBoxLayout(self.files_tab)
        
        self.select_files_button = QPushButton("SELECT AUDIO FILES")
        self.select_files_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clear_files_button = QPushButton("CLEAR")
        
        self.files_table = self._create_track_table()
        time_layout, self.files_time_edit = self._create_time_layout()
        self.scrobble_files_button = QPushButton("SCROBBLE")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.select_files_button)
        buttons_layout.addWidget(self.clear_files_button)
        
        layout.addLayout(buttons_layout)
        layout.addWidget(self.files_table)
        layout.addLayout(time_layout)
        layout.addWidget(self.scrobble_files_button)

        self.select_files_button.clicked.connect(self.select_audio_files)
        self.clear_files_button.clicked.connect(self.clear_files_data)
        self.scrobble_files_button.clicked.connect(self.scrobble_files)
        self.audio_files = []

    def clear_data(self):
        self.release_id_input.clear()
        self.track_table.setRowCount(0)
        self.artist_name = ""
        self.album_title = ""
        self.manual_time_edit.setDateTime(QDateTime.currentDateTime())

    def fetch_release_data(self):
        raw_text = self.release_id_input.text().strip()
        release_id = raw_text.replace('r', '').replace('[', '').replace(']', '')

        if not release_id.isdigit():
            QMessageBox.warning(self, "ERROR", "Incorrect release ID format.")
            return

        data = self.api_handler.get_discogs_release(release_id)
        if not data or not all(k in data for k in ('artist', 'album', 'tracks')):
            QMessageBox.critical(self, "ERROR", "Couldn't download metadata or data is invalid.")
            return

        self.artist_name, self.album_title = data['artist'], data['album']
        self.populate_table(data['tracks'])

    def populate_table(self, tracklist):
        self.track_table.setRowCount(len(tracklist))
        for row, track in enumerate(tracklist):
            self._insert_track_row(
                table=self.track_table,
                row=row,
                pos=track['position'],
                artist=self.artist_name,
                album=self.album_title,
                title=track['title'],
                duration=track['duration']
            )

    def scrobble_tracks(self):
        if not self.artist_name:
            QMessageBox.warning(self, "NO DATA", "Please import metadata first.")
            return

        tracks_to_scrobble = []
        for row in range(self.track_table.rowCount()):
            if self.track_table.item(row, 0).checkState() == Qt.Checked:
                title = self.track_table.item(row, 4).text()
                duration_str = self.track_table.item(row, 5).text()
                duration_sec = self.parse_duration(duration_str)
                tracks_to_scrobble.append({'title': title, 'duration': duration_sec})

        if not tracks_to_scrobble:
            QMessageBox.information(self, "INFORMATION", "No tracks selected to scrobble.")
            return

        end_timestamp = self.manual_time_edit.dateTime().toSecsSinceEpoch() if self.manual_time_edit.dateTime().isValid() else None

        try:
            self.api_handler.scrobble_to_lastfm(
                self.artist_name, self.album_title, tracks_to_scrobble, timestamp=end_timestamp
            )
            QMessageBox.information(self, "SUCCESS", "Scrobbling process completed.")
        except Exception as e:
            QMessageBox.critical(self, "ERROR", f"Scrobbling failed: {e}")

    def select_audio_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "", "Audio Files (*.mp3 *.flac *.wav *.ogg *.m4a *.opus)"
        )
        if not files:
            return
            
        self.clear_files_data()
        self.audio_files = files
        self.files_table.setRowCount(len(files))

        for i, fpath in enumerate(files):
            try:
                audio = MutagenFile(fpath, easy=True)
                artist = audio['artist'][0] if audio and 'artist' in audio and audio['artist'] else "Unknown Artist"
                album = audio['album'][0] if audio and 'album' in audio and audio['album'] else "Unknown Album"
                title = audio['title'][0] if audio and 'title' in audio and audio['title'] else os.path.basename(fpath)
                duration_sec = int(audio.info.length) if audio and audio.info else 0
            except Exception:
                artist = "Unknown Artist"
                album = "Unknown Album"
                title = os.path.basename(fpath)
                duration_sec = 0

            duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"

            self._insert_track_row(
                table=self.files_table,
                row=i,
                pos=str(i + 1),
                artist=artist,
                album=album,
                title=title,
                duration=duration_str
            )

    def clear_files_data(self):
        self.files_table.setRowCount(0)
        self.audio_files = []
        self.files_time_edit.setDateTime(QDateTime.currentDateTime())

    def scrobble_files(self):
        if not self.audio_files:
            QMessageBox.warning(self, "NO FILES", "Please select audio files first.")
            return

        grouped_tracks = {}
        for i in range(self.files_table.rowCount()):
            if self.files_table.item(i, 0).checkState() == Qt.Checked:
                artist = self.files_table.item(i, 2).text()
                album = self.files_table.item(i, 3).text()
                title = self.files_table.item(i, 4).text()
                duration_str = self.files_table.item(i, 5).text()
                duration_sec = self.parse_duration(duration_str)
                track_data = {'title': title, 'duration': duration_sec}
                key = (artist, album)
                if key not in grouped_tracks:
                    grouped_tracks[key] = []
                grouped_tracks[key].append(track_data)

        if not grouped_tracks:
            QMessageBox.information(self, "INFORMATION", "No tracks selected to scrobble.")
            return

        end_timestamp = self.files_time_edit.dateTime().toSecsSinceEpoch() if self.files_time_edit.dateTime().isValid() else None

        success_count = 0
        fail_count = 0
        error_msgs = []
        
        for (artist, album), tracks_to_scrobble in grouped_tracks.items():
            if not artist or not album or artist == "Unknown Artist" or album == "Unknown Album":
                fail_count += len(tracks_to_scrobble)
                error_msgs.append(f"Skipped {len(tracks_to_scrobble)} tracks (Unknown Artist/Album)")
                continue

            try:
                self.api_handler.scrobble_to_lastfm(
                    artist, album, tracks_to_scrobble, timestamp=end_timestamp
                )
                success_count += len(tracks_to_scrobble)
            except Exception as e:
                fail_count += len(tracks_to_scrobble)
                error_msgs.append(f"Failed for {artist} - {album}: {e}")

        summary_message = f"Scrobbling process completed.\n\n"
        summary_message += f"Successfully scrobbled: {success_count} tracks\n"
        summary_message += f"Failed/Skipped: {fail_count} tracks\n"
        
        if error_msgs:
            summary_message += "\nErrors:\n" + "\n".join(list(set(error_msgs))) 

        if fail_count > 0:
            QMessageBox.warning(self, "PARTIAL SUCCESS", summary_message)
        else:
            QMessageBox.information(self, "SUCCESS", summary_message)

    def _insert_track_row(self, table: QTableWidget, row: int, pos: str, artist: str, album: str, title: str, duration: str):
        check_item = QTableWidgetItem()
        check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        check_item.setCheckState(Qt.Checked)
        
        pos_item = QTableWidgetItem(pos)
        artist_item = QTableWidgetItem(artist)
        album_item = QTableWidgetItem(album)
        title_item = QTableWidgetItem(title)
        duration_item = QTableWidgetItem(duration)
        
        pos_item.setFlags(pos_item.flags() & ~Qt.ItemIsEditable)
        artist_item.setFlags(artist_item.flags() & ~Qt.ItemIsEditable)
        album_item.setFlags(album_item.flags() & ~Qt.ItemIsEditable)
        duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)

        table.setItem(row, 0, check_item)
        table.setItem(row, 1, pos_item)
        table.setItem(row, 2, artist_item)
        table.setItem(row, 3, album_item)
        table.setItem(row, 4, title_item)
        table.setItem(row, 5, duration_item)

    @staticmethod
    def parse_duration(duration_str):
        duration_sec = 0
        if duration_str and ':' in duration_str:
            try:
                parts = [int(p) for p in duration_str.split(':')]
                if len(parts) == 3:
                    duration_sec = parts[0]*3600 + parts[1]*60 + parts[2]
                elif len(parts) == 2:
                    duration_sec = parts[0]*60 + parts[1]
                else:
                    duration_sec = 180
            except (ValueError, IndexError):
                duration_sec = 180
        if duration_sec == 0:
            duration_sec = 180
        return duration_sec


if __name__ == '__main__':
    app = QApplication(sys.argv)

    try:
        user_credentials, api_keys = config.load_all_config()
        
        api_handler = ApiClients(
            lastfm_username=user_credentials[0], 
            lastfm_password=user_credentials[1],
            discogs_token=api_keys['discogs_token'],
            lastfm_key=api_keys['lastfm_key'],
            lastfm_secret=api_keys['lastfm_secret']
        )
        
        window = ScrobblerApp(api_handler)
        window.show()
        sys.exit(app.exec())
        
    except (FileNotFoundError, KeyError, ValueError) as e:
        QMessageBox.critical(app.activeWindow(), "CONFIG ERROR", f"Error in {config.CONFIG_FILE}:\n\n{e}\n\nPlease manually edit the configuration file.")
        sys.exit()
    except Exception as e:
        QMessageBox.critical(app.activeWindow(), "CRITICAL ERROR", f"An unexpected error occurred: {e}")
        sys.exit()