# variantize

A CLI tool that automatically generates all field-omission variants of a Pydantic model.

## Motivation

Suppose you have a model representing a date:

```python
class DateFull(BaseModel):
    year: str
    month: str
    day: str
    template: str = "{year}/{month}/{day}"
```

Real-world data is often partial — you might know only the year, or only the month and day. Handling these cases requires multiple models with omitted fields. Writing them by hand is tedious and error-prone. variantize generates them automatically.

## Installation

```bash
pip install variantize
# or
poetry add variantize
```

## Usage

Prepare your source model in a file with a `_` prefix:

```
_date.py   # define your base model here
```

Run the following command to generate `date.py`:

```bash
variantize _date.py
```

### Generated output

`date.py` will contain:

- The original `DateFull` class (copied as-is)
- All partial variants with omitted fields set to `Literal[None]`
- A Union type alias combining all classes

```python
class DateFull(BaseModel):
    year: str
    month: str
    day: str
    template: str = "{year}/{month}/{day}"

class DateWithoutYear(BaseModel):
    year: Literal[None] = None
    month: str
    day: str
    template: str = "{year}/{month}/{day}"

# ... all variants

Date = (
    DateFull
    | DateWithoutYear
    | DateWithoutMonth
    | DateWithoutDay
    | DateWithoutYearMonth
    | DateWithoutMonthDay
    | DateWithoutDayYear
)
```

> **Note**: The `template` field is copied as-is from the base model. Edit each variant's template manually to match its omitted fields.

## Specification

- Only the first class in the input file is processed.
- The `template` field is excluded from optional-ization.
- Fields eligible for optional-ization are auto-detected from `{...}` placeholders in `template`.
- The all-None variant (no fields present) is not generated.
- The all-present variant is not generated (it is already `DateFull`).
- Imports from the source file are copied as-is; `Literal` is added automatically if not present.
- The output file is overwritten on every run (idempotent).

## File naming convention

| Input | Output |
|-------|--------|
| `_date.py` | `date.py` |
| `_address.py` | `address.py` |

## Class naming convention

Base class name + `Without` + omitted field names in definition order (PascalCase):

```
DateFull → DateWithoutYear, DateWithoutMonth, DateWithoutYearMonth, ...
```

## Development

```bash
git clone https://github.com/yourname/variantize
cd variantize
poetry install
poetry run variantize --help
```

## License

MIT
