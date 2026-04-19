from __future__ import annotations

import sys
from pathlib import Path

from variantize.generator import VariantModel
from variantize.parser import FieldInfo, ModelInfo


def write_output(output_path: Path, model: ModelInfo, variants: list[VariantModel]) -> None:
    output_path.write_text(_render(model, variants))


def _render(model: ModelInfo, variants: list[VariantModel]) -> str:
    import_block = _render_imports(model.import_lines)
    stem = model.class_name.removesuffix("Full")
    all_class_names = [model.class_name] + [v.class_name for v in variants]

    parts = [import_block]
    parts.append(_render_class(model.class_name, model.base_class, model.fields, model.properties))
    for v in variants:
        parts.append(_render_class(v.class_name, v.base_class, v.fields, v.properties))
    parts.append(_render_union(stem, all_class_names))

    return "\n\n\n".join(parts) + "\n"


def _render_imports(import_lines: list[str]) -> str:
    lines = list(import_lines)
    if not any("Literal" in line for line in lines):
        lines.append("from typing import Literal")

    stdlib, third_party = [], []
    for line in lines:
        module = _top_level_module(line)
        if module in sys.stdlib_module_names:
            stdlib.append(line)
        else:
            third_party.append(line)

    groups = [g for g in ["\n".join(stdlib), "\n".join(third_party)] if g]
    return "\n\n".join(groups)


def _top_level_module(import_line: str) -> str:
    # "from foo.bar import X" → "foo", "import foo.bar" → "foo"
    parts = import_line.split()
    if parts[0] == "from":
        return parts[1].split(".")[0]
    if parts[0] == "import":
        return parts[1].split(".")[0]
    return ""


def _render_class(name: str, base: str, fields: list[FieldInfo], properties: list[str] = []) -> str:
    lines = [f"class {name}({base}):"]
    for f in fields:
        if f.default is not None:
            lines.append(f"    {f.name}: {f.annotation} = {f.default}")
        else:
            lines.append(f"    {f.name}: {f.annotation}")
    result = "\n".join(lines)
    for prop in properties:
        result += "\n\n" + prop
    return result


def _render_union(stem: str, all_class_names: list[str]) -> str:
    parts = "\n    | ".join(all_class_names)
    return f"{stem} = (\n    {parts}\n)"
