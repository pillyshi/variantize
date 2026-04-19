from pathlib import Path

import pytest

from variantize.parser import parse_model_file

FIXTURE = Path(__file__).parent / "fixtures" / "_date.py"


def test_parse_class_name():
    info = parse_model_file(FIXTURE)
    assert info.class_name == "DateFull"


def test_parse_base_class():
    info = parse_model_file(FIXTURE)
    assert info.base_class == "BaseModel"


def test_parse_fields():
    info = parse_model_file(FIXTURE)
    names = [f.name for f in info.fields]
    assert names == ["year", "month", "day", "template"]


def test_field_annotations():
    info = parse_model_file(FIXTURE)
    by_name = {f.name: f for f in info.fields}
    assert by_name["year"].annotation == "str"
    assert by_name["month"].annotation == "str"
    assert by_name["day"].annotation == "str"
    assert by_name["template"].annotation == "str"


def test_template_default():
    info = parse_model_file(FIXTURE)
    assert info.template_field is not None
    assert "{year}" in info.template_field.default
    assert "{month}" in info.template_field.default
    assert "{day}" in info.template_field.default


def test_optional_fields():
    info = parse_model_file(FIXTURE)
    assert info.optional_fields == ["year", "month", "day"]


def test_import_lines():
    info = parse_model_file(FIXTURE)
    assert any("pydantic" in line for line in info.import_lines)
