"""Combine independent branch builds into one GitHub Pages artifact."""

import shutil
import sys
from pathlib import Path


def assemble(production: Path, staging: Path, output: Path) -> None:
    production, staging, output = (p.resolve() for p in (production, staging, output))
    for source in (production, staging):
        if not (source / "index.html").is_file():
            raise ValueError(f"Missing site build: {source}")
        if output == source or output in source.parents or source in output.parents:
            raise ValueError("Output must be separate from both source builds")
    if (production / "staging").exists():
        raise ValueError("Production must not contain a staging directory")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(production, output)
    shutil.copytree(staging, output / "staging")
    # Add this at the artifact root even when production is an older revision.
    alias = output / "stage"
    alias.mkdir(exist_ok=True)
    (alias / "index.html").write_text(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
        '<title>Staging preview</title>\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        '<meta http-equiv="refresh" content="0; url=/staging/">\n'
        '<link rel="canonical" href="/staging/">\n'
        '</head><body><p><a href="/staging/">Continue to staging</a></p></body></html>\n',
        encoding="utf-8",
    )
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    assemble(*(Path(argument) for argument in sys.argv[1:]))
