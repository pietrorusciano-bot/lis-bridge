import os
import shutil
import subprocess
import time

import requests

ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLYAI_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"


def _find_ffmpeg():
    path = shutil.which("ffmpeg")
    if path:
        return path
    candidates = [
        os.path.expandvars(
            r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
        ),
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "ffmpeg"


class Transcriber:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "ASSEMBLYAI_API_KEY mancante. Imposta la variabile d'ambiente "
                "ASSEMBLYAI_API_KEY oppure passala a Transcriber(api_key=...)."
            )

    def _convert(self, audio_path):
        wav_path = os.path.splitext(audio_path)[0] + ".wav"
        subprocess.run(
            [
                _find_ffmpeg(), "-y", "-i", audio_path,
                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return wav_path

    def _upload(self, audio_path):
        wav_path = self._convert(audio_path)
        with open(wav_path, "rb") as f:
            raw = f.read()
        response = requests.post(
            ASSEMBLYAI_UPLOAD_URL,
            headers={
                "Authorization": self.api_key,
                "Content-Type": "application/octet-stream",
            },
            data=raw,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["upload_url"]

    def _poll(self, transcript_id):
        while True:
            response = requests.get(
                f"{ASSEMBLYAI_TRANSCRIPT_URL}/{transcript_id}",
                headers={"Authorization": self.api_key},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            if data["status"] == "completed":
                return data
            if data["status"] == "error":
                raise RuntimeError(f"Trascrizione fallita: {data.get('error')}")
            time.sleep(1)

    def transcribe(self, audio_path):
        upload_url = self._upload(audio_path)
        response = requests.post(
            ASSEMBLYAI_TRANSCRIPT_URL,
            headers={"Authorization": self.api_key},
            json={
                "audio_url": upload_url,
                "speaker_labels": True,
                "language_code": "it",
            },
            timeout=60,
        )
        response.raise_for_status()
        result = self._poll(response.json()["id"])

        utterances = []
        for u in result.get("utterances", []):
            utterances.append({
                "speaker": u.get("speaker", "A"),
                "text": u.get("text", "").strip(),
                "start": u.get("start", 0),
                "end": u.get("end", 0),
            })
        return utterances

    def full_text(self, audio_path):
        utterances = self.transcribe(audio_path)
        return " ".join(u["text"] for u in utterances).strip()
