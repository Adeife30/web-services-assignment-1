from __future__ import annotations

import json
import sys
from pathlib import Path


def main(openapi_path: str, output_path: str) -> None:
    openapi = json.loads(Path(openapi_path).read_text(encoding="utf-8"))
    lines = []
    lines.append("Inventory Management API")
    lines.append("=" * 26)
    lines.append("")
    lines.append("Generated from FastAPI OpenAPI documentation.")
    lines.append("Reference docs: http://localhost:8000/docs")
    lines.append("")

    for path, methods in openapi.get("paths", {}).items():
        lines.append(path)
        lines.append("-" * len(path))
        for method, details in methods.items():
            lines.append(f"Method: {method.upper()}")
            lines.append(f"Summary: {details.get('summary', 'N/A')}")
            parameters = details.get("parameters", [])
            if parameters:
                lines.append("Parameters:")
                for parameter in parameters:
                    required = parameter.get("required", False)
                    schema = parameter.get("schema", {})
                    param_type = schema.get("type", "unknown")
                    lines.append(
                        f"  - {parameter['name']} ({parameter['in']}, type={param_type}, required={required})"
                    )
            else:
                lines.append("Parameters: body-only or none")
            lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python scripts/generate_readme.py <openapi.json> <README.txt>")
    main(sys.argv[1], sys.argv[2])
