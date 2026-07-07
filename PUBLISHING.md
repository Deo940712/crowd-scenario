# Publishing to PyPI

`crowd-scenario` is publish-ready: pure stdlib runtime (`dependencies = []`), `py.typed`
ships in the wheel, and `twine check` passes on both the wheel and the sdist.

## One-time

```bash
pip install build twine
```

## Each release

1. Bump the version in **both** `pyproject.toml` (`[project].version`) and
   `src/crowdscenario/__init__.py` (`__version__`), and keep them in sync.
2. Ensure the tree is green:

   ```bash
   pytest -q
   ruff check .
   ```

3. Build a clean wheel + sdist:

   ```bash
   # remove stale artifacts first
   rm -rf dist            # PowerShell: Remove-Item -Recurse -Force dist
   python -m build --outdir dist
   ```

4. Validate metadata + README rendering:

   ```bash
   python -m twine check dist/*
   ```

5. Upload (requires your own PyPI credentials — never commit a token):

   ```bash
   # test first, optional:
   python -m twine upload --repository testpypi dist/*
   # real:
   python -m twine upload dist/*
   ```

`dist/` is git-ignored, so build artifacts never enter the repository.
