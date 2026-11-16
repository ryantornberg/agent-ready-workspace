"""Put each service's folder on the import path, so a test imports its modules by name."""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
for service in ("orders-api", "orders-web", "orders-service-v1"):
    sys.path.insert(0, str(SRC / service))
