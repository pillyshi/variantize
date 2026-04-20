from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from variantize.parser import FieldInfo, ModelInfo


@dataclass
class VariantModel:
    class_name: str
    base_class: str
    fields: list[FieldInfo]
    properties: list[str]


def generate_variants(model: ModelInfo) -> list[VariantModel]:
    subsets = _generate_omission_subsets(model.optional_fields)
    return [_build_variant(model, omitted) for omitted in subsets]


def _generate_omission_subsets(fields: list[str]) -> list[tuple[str, ...]]:
    result = []
    for size in range(1, len(fields)):
        for combo in combinations(fields, size):
            result.append(combo)
    return result


def _build_variant(model: ModelInfo, omitted: tuple[str, ...]) -> VariantModel:
    omitted_set = set(omitted)
    new_fields = []
    for f in model.fields:
        if f.name == "template":
            new_fields.append(f)
        elif f.name in omitted_set:
            new_fields.append(FieldInfo(name=f.name, annotation="Literal[None]", default="None"))
        else:
            new_fields.append(f)
    return VariantModel(
        class_name=_variant_class_name(model.class_name, omitted),
        base_class=model.base_class,
        fields=new_fields,
        properties=model.properties,
    )


def _variant_class_name(base_name: str, omitted: tuple[str, ...]) -> str:
    stem = base_name.removesuffix("Full")
    suffix = "".join(_snake_to_pascal(f) for f in omitted)
    return f"{stem}Without{suffix}"


def _snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))
