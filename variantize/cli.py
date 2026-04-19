from __future__ import annotations

from pathlib import Path

import typer

from variantize.generator import generate_variants
from variantize.parser import parse_model_file
from variantize.writer import write_output

app = typer.Typer()


@app.command()
def main(input_file: Path = typer.Argument(..., help="Input file with _ prefix")) -> None:
    if not input_file.exists():
        typer.echo(f"Error: {input_file} does not exist", err=True)
        raise typer.Exit(1)
    if not input_file.name.startswith("_"):
        typer.echo(f"Error: input file must start with '_', got: {input_file.name}", err=True)
        raise typer.Exit(1)

    model_info = parse_model_file(input_file)
    variants = generate_variants(model_info)
    output_path = input_file.parent / input_file.name.lstrip("_")
    write_output(output_path, model_info, variants)
    typer.echo(f"Generated {output_path}")
