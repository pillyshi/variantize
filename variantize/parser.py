from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FieldInfo:
    name: str
    annotation: str
    default: str | None


@dataclass
class ModelInfo:
    class_name: str
    base_class: str
    fields: list[FieldInfo]
    template_field: FieldInfo | None
    optional_fields: list[str]
    import_lines: list[str]


def parse_model_file(path: Path) -> ModelInfo:
    source = path.read_text()
    tree = ast.parse(source)
    source_lines = source.splitlines()

    import_lines = _collect_imports(tree, source_lines)
    class_node = _find_first_class(tree)
    fields = _extract_fields(class_node)
    template_field = next((f for f in fields if f.name == "template"), None)
    optional_fields = _extract_optional_fields(template_field, fields)
    base_class = class_node.bases[0].id if class_node.bases else "BaseModel"

    return ModelInfo(
        class_name=class_node.name,
        base_class=base_class,
        fields=fields,
        template_field=template_field,
        optional_fields=optional_fields,
        import_lines=import_lines,
    )


def _collect_imports(tree: ast.Module, source_lines: list[str]) -> list[str]:
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            start = node.lineno - 1
            end = node.end_lineno
            lines.append("\n".join(source_lines[start:end]))
    return lines


def _find_first_class(tree: ast.Module) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return node
    raise ValueError("No class definition found in the input file")


def _extract_fields(class_node: ast.ClassDef) -> list[FieldInfo]:
    fields = []
    for node in class_node.body:
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name):
            continue
        name = node.target.id
        annotation = ast.unparse(node.annotation)
        default = ast.unparse(node.value) if node.value is not None else None
        fields.append(FieldInfo(name=name, annotation=annotation, default=default))
    return fields


def _extract_optional_fields(
    template_field: FieldInfo | None, fields: list[FieldInfo]
) -> list[str]:
    if template_field is None or template_field.default is None:
        return []
    placeholders = set(re.findall(r"\{(\w+)\}", template_field.default))
    return [f.name for f in fields if f.name in placeholders]
