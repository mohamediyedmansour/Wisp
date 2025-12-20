#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pyperclip

from wisp.uploader import CatboxUploader
from wisp.exceptions import CatboxError
from wisp.utils import is_url

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="catbox-upload",
        description="Upload files or URLs to Catbox"
    )
    parser.add_argument("target", help="File path or URL")
    parser.add_argument("--copy", action="store_true", help="Copy URL to clipboard")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()
    uploader = CatboxUploader()

    try:
        if is_url(args.target):
            url = uploader.upload_url(args.target)
        else:
            url = uploader.upload_file(Path(args.target))

        if args.copy:
            pyperclip.copy(url)

        if args.json:
            print(json.dumps({
                "success": True,
                "url": url
            }))
        else:
            uploader.print_result(url, copied=args.copy)

    except CatboxError as e:
        if args.json:
            print(json.dumps({
                "success": False,
                "error": str(e)
            }))
        else:
            logging.error(f"❌ {e}")
        raise SystemExit(2)
