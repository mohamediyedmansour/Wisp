#!/usr/bin/env python3
from __future__ import annotations

import sys
import logging
from pathlib import Path

from uploader import CatboxUploader
from exceptions import CatboxError
from utils import is_url

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: ./main.py <file_path | url>")
        sys.exit(1)

    target = sys.argv[1]
    uploader = CatboxUploader()

    try:
        if is_url(target):
            url = uploader.upload_url(target)
        else:
            url = uploader.upload_file(Path(target))

        uploader.print_result(url)

    except CatboxError as e:
        logging.error(f"❌ {e}")
        sys.exit(2)

    except KeyboardInterrupt:
        logging.warning("\nUpload cancelled by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
