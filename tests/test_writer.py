from pathlib import Path

import pytest

from variantize.generator import generate_variants
from variantize.parser import FieldInfo, ModelInfo, parse_model_file
from variantize.writer import _render, _render_imports, _render_union, write_output

FIXTURE = Path(__file__).parent / "fixtures" / "_date.py"


def test_literal_added_when_missing():
    result = _render_imports(["from pydantic import BaseModel"])
    assert "Literal" in result


def test_literal_not_duplicated():
    result = _render_imports(["from typing import Literal", "from pydantic import BaseModel"])
    assert result.count("Literal") == 1


def test_union_alias_name():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    output = _render(model, variants)
    assert "Date = (" in output


def test_union_alias_contains_all_classes():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    output = _render(model, variants)
    assert "DateFull" in output
    for v in variants:
        assert v.class_name in output


def test_output_path_derivation(tmp_path):
    import shutil
    src = tmp_path / "_date.py"
    shutil.copy(FIXTURE, src)
    model = parse_model_file(src)
    variants = generate_variants(model)
    output_path = src.parent / src.name.lstrip("_")
    write_output(output_path, model, variants)
    assert output_path.exists()
    assert output_path.name == "date.py"


def test_full_output_is_valid_python(tmp_path):
    import shutil
    src = tmp_path / "_date.py"
    shutil.copy(FIXTURE, src)
    model = parse_model_file(src)
    variants = generate_variants(model)
    output_path = src.parent / src.name.lstrip("_")
    write_output(output_path, model, variants)
    import ast
    ast.parse(output_path.read_text())  # raises SyntaxError if invalid


def test_render_union():
    result = _render_union("Date", ["DateFull", "DateWithoutYear", "DateWithoutMonth"])
    assert result.startswith("Date = (")
    assert "DateFull" in result
    assert "DateWithoutYear" in result
