import asyncio
import hashlib
import json
import re
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

import edge_tts
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class PronunciationService(QObject):
    """Edge TTS with dictionary audio fallback and disk cache.

    All network I/O takes place on a background thread. The Qt player is
    operated only by UI-thread slots through signals.
    """

    started = Signal(str)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        cache_dir: str | Path,
        voice: str = "en-US-AriaNeural",
        parent=None,
    ):
        super().__init__(parent)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voice = voice

        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(1.0)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)

        self._lock = threading.Lock()
        self._active_requests: set[str] = set()
        self._edge_blocked_until = 0.0

        # Force queued delivery: completed downloads play in Qt's UI thread.
        self.finished.connect(self.play_downloaded_file)

    def speak(self, text: str) -> None:
        value = " ".join(text.strip().split())
        if not value:
            self.failed.emit("Không có nội dung để phát âm.")
            return

        audio_path = self._cache_path(value)
        if audio_path.exists() and audio_path.stat().st_size > 0:
            self._play(audio_path)
            return

        request_key = str(audio_path)
        with self._lock:
            if request_key in self._active_requests:
                return
            self._active_requests.add(request_key)

        self.started.emit(value)
        threading.Thread(
            target=self._download_worker,
            args=(value, audio_path, request_key),
            daemon=True,
        ).start()

    def _cache_path(self, text: str) -> Path:
        # Keep the existing key format so users retain old cached recordings.
        digest = hashlib.sha256(
            f"{self.voice}\0{text}".encode("utf-8")
        ).hexdigest()
        return self.cache_dir / f"{digest}.mp3"

    @staticmethod
    def _dictionary_audio(text: str, destination: Path) -> bool:
        """Retrieve real recordings for *single words*, not whole phrases."""
        if not re.fullmatch(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text):
            return False

        api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + quote(text)
        request = Request(api_url, headers={"User-Agent": "QuizLearn/1.0"})
        try:
            with urlopen(request, timeout=8) as response:
                entries = json.load(response)
            if not isinstance(entries, list):
                return False

            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                # Reject unrelated suggestions; never pronounce another word.
                if entry.get("word", "").casefold() != text.casefold():
                    continue
                for phonetic in entry.get("phonetics", []):
                    if not isinstance(phonetic, dict):
                        continue
                    audio_url = phonetic.get("audio") or ""
                    parsed = urlparse(audio_url)
                    if parsed.scheme != "https" or parsed.hostname not in {
                        "api.dictionaryapi.dev",
                        "ssl.gstatic.com",
                    }:
                        continue
                    audio_req = Request(
                        audio_url, headers={"User-Agent": "QuizLearn/1.0"}
                    )
                    try:
                        with urlopen(audio_req, timeout=10) as response:
                            content_type = response.headers.get(
                                "Content-Type", ""
                            ).lower()
                            data = response.read(2_000_001)
                    except (HTTPError, URLError, TimeoutError, OSError):
                        continue

                    if not data or len(data) > 2_000_000:
                        continue
                    if not (
                        "audio/mpeg" in content_type
                        or "audio/mp3" in content_type
                        or data.startswith(b"ID3")
                        or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
                    ):
                        continue
                    destination.write_bytes(data)
                    return True
        except (
            HTTPError, URLError, TimeoutError, ValueError,
            OSError, KeyError, TypeError,
        ):
            return False
        return False

    def _download_worker(
        self, text: str, audio_path: Path, request_key: str
    ) -> None:
        temp_path = audio_path.with_suffix(".tmp.mp3")
        edge_error = None
        try:
            with self._lock:
                skip_edge = time.monotonic() < self._edge_blocked_until

            if not skip_edge:
                try:
                    asyncio.run(
                        edge_tts.Communicate(
                            text=text, voice=self.voice
                        ).save(str(temp_path))
                    )
                    if not temp_path.exists() or temp_path.stat().st_size == 0:
                        raise RuntimeError("Empty TTS audio")
                    temp_path.replace(audio_path)
                    self.finished.emit(str(audio_path))
                    return
                except Exception as error:
                    edge_error = str(error)
                    temp_path.unlink(missing_ok=True)
                    if "403" in edge_error or "401" in edge_error:
                        with self._lock:
                            self._edge_blocked_until = time.monotonic() + 300

            if self._dictionary_audio(text, temp_path):
                temp_path.replace(audio_path)
                self.finished.emit(str(audio_path))
                return

            if edge_error and ("403" in edge_error or "401" in edge_error):
                message = (
                    "Edge TTS từ chối truy cập (HTTP 403/401); "
                    "từ điển dự phòng không có âm thanh cho mục này."
                )
            else:
                message = (
                    "Không tải được âm thanh từ Edge TTS và từ điển dự phòng. "
                    "Các từ đã lưu vẫn phát được ngoại tuyến."
                )
            self.failed.emit(message)
        except Exception:
            self.failed.emit("Không thể tải âm thanh. Vui lòng thử lại sau.")
        finally:
            temp_path.unlink(missing_ok=True)
            with self._lock:
                self._active_requests.discard(request_key)

    def _play(self, audio_path: Path) -> None:
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(str(audio_path.resolve())))
        self.player.play()

    def play_downloaded_file(self, audio_path: str) -> None:
        self._play(Path(audio_path))
