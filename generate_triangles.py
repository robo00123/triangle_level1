#!/usr/bin/env python3
"""Generate triangle SVG images from CSV data and templates."""

from __future__ import annotations

import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NAMESPACE)


def _normalize_header(name: str) -> str:
    return name.strip().lower().replace(" ", "")


def _header_indices(header_row: list[str]) -> tuple[int, int, int, int]:
    header_map = {_normalize_header(name): idx for idx, name in enumerate(header_row)}

    def _index(key: str, fallback: int) -> int:
        return header_map.get(key, fallback)

    return (
        _index("filename", 0),
        _index("svg_template", 1),
        _index("b", 2),
        _index("h", 3),
    )


def _ensure_svg_extension(name: str) -> str:
    base, ext = os.path.splitext(name)
    if ext:
        return name
    return f"{base}.svg"


def _replace_dimensions(
    root: ET.Element, base_value: str, height_value: str
) -> tuple[int, int]:
    replaced_base = 0
    replaced_height = 0
    for element in root.iter():
        if element.text is None:
            continue
        text = element.text.strip()
        if text == "b":
            element.text = base_value
            replaced_base += 1
        elif text == "h":
            element.text = height_value
            replaced_height += 1
    return replaced_base, replaced_height


def generate_images(csv_path: str, template_dir: str, output_dir: str) -> int:
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    os.makedirs(output_dir, exist_ok=True)

    template_cache: dict[str, str] = {}
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        try:
            header_row = next(reader)
        except StopIteration as exc:
            raise ValueError("CSV file is empty") from exc

        filename_idx, template_idx, base_idx, height_idx = _header_indices(header_row)

        for row_number, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                continue
            try:
                filename = row[filename_idx].strip()
                template_name = row[template_idx].strip()
                base_value = row[base_idx].strip()
                height_value = row[height_idx].strip()
            except IndexError as exc:
                raise ValueError(
                    f"Row {row_number} does not have enough columns"
                ) from exc

            if not filename:
                raise ValueError(f"Row {row_number} missing filename")
            if not template_name:
                raise ValueError(f"Row {row_number} missing svg template")

            template_path = os.path.join(template_dir, template_name)
            if template_path not in template_cache:
                with open(template_path, encoding="utf-8") as template_file:
                    template_cache[template_path] = template_file.read()

            try:
                root = ET.fromstring(template_cache[template_path])
            except ET.ParseError as exc:
                raise ValueError(
                    f"Template '{template_name}' is not valid SVG"
                ) from exc

            replaced_base, replaced_height = _replace_dimensions(
                root, base_value, height_value
            )
            if replaced_base == 0 or replaced_height == 0:
                raise ValueError(
                    f"Template '{template_name}' missing b/h placeholders"
                )

            output_name = _ensure_svg_extension(filename)
            output_path = os.path.join(output_dir, output_name)
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            count += 1

    return count


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate triangle SVG images by replacing b/h placeholders with CSV values."
        )
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default="triangleslevel1.csv",
        help="Path to the CSV file with triangle data.",
    )
    parser.add_argument(
        "--templates-dir",
        dest="template_dir",
        default=".",
        help="Directory containing SVG template files.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="generated",
        help="Directory to write generated SVG files.",
    )
    args = parser.parse_args()

    try:
        count = generate_images(args.csv_path, args.template_dir, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Generated {count} SVG files in {os.path.abspath(args.output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
