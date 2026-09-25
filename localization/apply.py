"""Apply the reviewed Simplified Chinese copy without changing protocol identifiers."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent


def apply(source: str, glossary: str) -> None:
    path = ROOT / source
    mapping_path = ROOT / "localization" / glossary
    contents = path.read_text(encoding="utf-8")
    missing = []
    seen = set()
    for number, line in enumerate(mapping_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        old, sep, new = line.partition("\t")
        if not sep or not old or not new or old in seen:
            raise ValueError(f"Invalid mapping at {mapping_path}:{number}")
        seen.add(old)
        quoted_old = f'"{old}"'
        quoted_new = f'"{new}"'
        if quoted_old in contents:
            contents = contents.replace(quoted_old, quoted_new)
        elif quoted_new not in contents:
            missing.append(f"{number}: {old}")
    if missing:
        raise ValueError("Mappings not found:\n" + "\n".join(missing))
    path.write_text(contents, encoding="utf-8")
    print(f"{source}: {len(seen)} reviewed phrases applied")


if __name__ == "__main__":
    for source, glossary in [
        ("AirCardApp.swift", "SwiftUI.tsv"),
        ("aircard_backend.py", "Backend.tsv"),
        ("aircard.py", "CLI.tsv"),
        ("apply_card_skin.py", "CardTool.tsv"),
        ("Sources/device_helper.m", "DeviceHelper.tsv"),
        ("Sources/airtraffic_host.m", "AirTraffic.tsv"),
    ]:
        if (ROOT / "localization" / glossary).exists():
            apply(source, glossary)
