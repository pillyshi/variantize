from pathlib import Path

from variantize.generator import _variant_class_name, generate_variants
from variantize.parser import parse_model_file

FIXTURE = Path(__file__).parent / "fixtures" / "_date.py"


def test_variant_count():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    # N=3: 2^3 - 2 = 6
    assert len(variants) == 6


def test_no_all_present_variant():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    full_names = {"year", "month", "day"}
    for v in variants:
        omitted = {f.name for f in v.fields if f.annotation == "Literal[None]"}
        assert omitted != set(), "all-present variant should not be generated"
        assert omitted != full_names, "all-none variant should not be generated"


def test_no_all_none_variant():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    optional_set = set(model.optional_fields)
    for v in variants:
        omitted = {f.name for f in v.fields if f.annotation == "Literal[None]"}
        assert omitted != optional_set


def test_variant_class_names():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    names = [v.class_name for v in variants]
    assert "DateWithoutYear" in names
    assert "DateWithoutMonth" in names
    assert "DateWithoutDay" in names
    assert "DateWithoutYearMonth" in names
    assert "DateWithoutYearDay" in names
    assert "DateWithoutMonthDay" in names


def test_template_field_never_omitted():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    for v in variants:
        template = next((f for f in v.fields if f.name == "template"), None)
        assert template is not None
        assert template.annotation == "str"


def test_omitted_field_becomes_literal_none():
    model = parse_model_file(FIXTURE)
    variants = generate_variants(model)
    without_year = next(v for v in variants if v.class_name == "DateWithoutYear")
    year_field = next(f for f in without_year.fields if f.name == "year")
    assert year_field.annotation == "Literal[None]"
    assert year_field.default == "None"


def test_variant_class_name_helper():
    assert _variant_class_name("DateFull", ("year",)) == "DateWithoutYear"
    assert _variant_class_name("DateFull", ("year", "month")) == "DateWithoutYearMonth"
    assert _variant_class_name("AddressFull", ("city",)) == "AddressWithoutCity"


FIXTURE_NO_TEMPLATE = Path(__file__).parent / "fixtures" / "_point.py"


def test_no_template_variant_count():
    model = parse_model_file(FIXTURE_NO_TEMPLATE)
    variants = generate_variants(model)
    # N=2: 2^2 - 2 = 2
    assert len(variants) == 2


def test_no_template_variant_class_names():
    model = parse_model_file(FIXTURE_NO_TEMPLATE)
    variants = generate_variants(model)
    names = [v.class_name for v in variants]
    assert "PointWithoutX" in names
    assert "PointWithoutY" in names


def test_no_template_omitted_field_becomes_literal_none():
    model = parse_model_file(FIXTURE_NO_TEMPLATE)
    variants = generate_variants(model)
    without_x = next(v for v in variants if v.class_name == "PointWithoutX")
    x_field = next(f for f in without_x.fields if f.name == "x")
    assert x_field.annotation == "Literal[None]"
    assert x_field.default == "None"
