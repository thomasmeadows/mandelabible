#!/usr/bin/env python3

import argparse
import base64
import mimetypes
from pathlib import Path

from openai import OpenAI

SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
}

client = OpenAI()


def image_to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def extract_text(image_path: Path) -> str:
    data_url = image_to_data_url(image_path)

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract ALL visible text from this image. "
                            "Do not summarize. Preserve paragraphs, line "
                            "breaks, headings, tables, and formatting as "
                            "closely as possible. Return only the extracted text."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url,
                    },
                ],
            }
        ],
    )

    return response.output_text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="OCR every image in a folder using OpenAI."
    )
    parser.add_argument(
        "folder",
        help="Folder containing images",
    )

    args = parser.parse_args()

    folder = Path(args.folder)

    if not folder.exists():
        raise SystemExit(f"Folder not found: {folder}")

    images = sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not images:
        print("No images found.")
        return

    output = Path("residuals.md")

    with output.open("w", encoding="utf-8") as md:

        md.write("# OCR Residuals\n\n")

        for image in images:
            print(f"Scanning {image.name}...")

            try:
                text = extract_text(image)
            except Exception as e:
                text = f"**ERROR:** {e}"

            md.write(f"## {image.name}\n\n")

            if text:
                md.write(text)
            else:
                md.write("*No text detected.*")

            md.write("\n\n---\n\n")

    print(f"\nFinished.\nOutput written to {output.resolve()}")


if __name__ == "__main__":
    main()