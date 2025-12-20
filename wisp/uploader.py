from __future__ import annotations

import mimetypes
import requests
import qrcode
from pathlib import Path
from typing import Final
from tqdm import tqdm
from rich.console import Console
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor

from wisp.exceptions import CatboxError

CATBOX_API: Final[str] = "https://catbox.moe/user/api.php"
MAX_SIZE_MB: Final[int] = 199
MAX_SIZE_BYTES: Final[int] = MAX_SIZE_MB * 1024 * 1024

console = Console()


class CatboxUploader:
    def __init__(self) -> None:
        self.session = requests.Session()

    def upload_file(self, path: Path) -> str:
        if not path.exists():
            raise CatboxError("File does not exist")

        size = path.stat().st_size
        if size <= 0:
            raise CatboxError("File size is zero")
        if size > MAX_SIZE_BYTES:
            raise CatboxError(f"File exceeds {MAX_SIZE_MB} MB limit")

        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

        encoder = MultipartEncoder(fields={
            "reqtype": "fileupload",
            "userhash": "",
            "fileToUpload": (path.name, open(path, "rb"), mime),
        })

        bar = tqdm(total=encoder.len, unit="B", unit_scale=True, desc="Uploading")

        def callback(monitor: MultipartEncoderMonitor) -> None:
            bar.n = monitor.bytes_read
            bar.refresh()

        monitor = MultipartEncoderMonitor(encoder, callback)

        response = self.session.post(
            CATBOX_API,
            data=monitor,
            headers={"Content-Type": monitor.content_type},
            timeout=120
        )

        bar.close()

        return self._handle_response(response)

    def upload_url(self, url: str) -> str:
        response = self.session.post(
            CATBOX_API,
            data={"reqtype": "urlupload", "userhash": "", "url": url},
            timeout=60
        )
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> str:
        if response.status_code != 200:
            raise CatboxError(f"HTTP {response.status_code}")

        text = response.text.strip()
        if not text.startswith("https://files.catbox.moe/"):
            raise CatboxError(text)

        return text

    def print_result(self, url: str, copied: bool = False) -> None:
        console.print("\n✅ Upload successful!", style="bold green")
        console.print(f"[bold cyan]{url}[/bold cyan]")
        if copied:
            console.print("📋 Copied to clipboard")

        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)

        console.print("\n📱 QR Code:\n")
        qr.print_ascii(invert=True)
