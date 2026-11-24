"""Put src/ on the import path, so a test imports the hooks package by name."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
