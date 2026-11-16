# PyPI Publish Guide

Releases are published by GitHub Actions through
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no API
token is stored in the repository.

## Release a version

1. Bump `version` in `pyproject.toml`.
2. Commit and push to `main`.
3. Tag and push:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The `Publish` workflow builds the sdist and wheel, validates metadata with
`twine check`, then uploads to PyPI. The job fails early if the tag does not
match the version in `pyproject.toml`.

## Rehearse on TestPyPI first

Run the `Publish` workflow manually (Actions → Publish → Run workflow) with
`target: testpypi`. Verify the result with:

```bash
pip install -i https://test.pypi.org/simple/ openvisionauto
```

Publishing to TestPyPI consumes a version number, so use a pre-release version
such as `0.1.1rc1` for rehearsal.

## One-time setup

These steps happen in the web UI, not in the repository.

**PyPI / TestPyPI** — add a pending publisher under *Publishing*:

| Field | Value |
| --- | --- |
| Owner | `OpenAutoUtility` |
| Repository | `openvisionauto` |
| Workflow | `publish.yml` |
| Environment | `pypi` (or `testpypi` for the rehearsal target) |

**GitHub** — create the `pypi` and `testpypi` environments under
*Settings → Environments*. Add required reviewers to `pypi` so every release
needs an approval before upload.

## Manual upload (fallback)

If Actions is unavailable, build and upload locally:

```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Use `__token__` as username and a PyPI API token as password.
