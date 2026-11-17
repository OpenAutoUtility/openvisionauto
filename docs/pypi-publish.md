# PyPI Publish Guide

Releases are published by GitHub Actions through
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no API
token is stored in the repository.

The package is owned by the PyPI **organization** `OpenAutoUtility`, not by any
individual account, so maintainers can come and go without changing ownership.

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

The upload job waits for approval because it targets the `pypi` environment.
Approve it on the run page; until then the run stays in *Waiting*.

## Rehearse on TestPyPI first

Bump `pyproject.toml` to a pre-release version such as `0.1.1rc1`, commit and
push to `main`, then run the `Publish` workflow manually
(Actions → Publish → Run workflow). A manual run publishes to TestPyPI only;
PyPI itself is reachable exclusively by pushing a `v*` tag. Verify with:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ openvisionauto
```

TestPyPI consumes the version number, so the rehearsal version can never be
reused on real PyPI — that is why it must carry a `rc` suffix.

## One-time setup

### 1. Create the PyPI organization

A GitHub organization and a PyPI organization are separate things. Apply at
<https://pypi.org/manage/organizations/>, choosing *community project* (free) or
*corporate* ($5 per member per month). PyPI admins review every application and
there is no published turnaround time, so apply early.

TestPyPI is a separate index with its own organizations; for TestPyPI rehearsal
a personal pending publisher is enough.

### 2. Add a pending publisher under the organization

Use the **organization's** *Publishing* page, not your account's. Published this
way, the project belongs to the organization from the first upload; a pending
publisher created under a personal account would make you the individual owner.

| Field | Value |
| --- | --- |
| PyPI project name | `openvisionauto` |
| Owner | `OpenAutoUtility` |
| Repository | `openvisionauto` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

A pending publisher reserves nothing: if someone else uploads `openvisionauto`
first, it is invalidated and the project must be transferred manually.

### 3. Configure GitHub environments

Create `pypi` and `testpypi` under *Settings → Environments*. The name must
match the pending publisher exactly.

Both environments restrict who may deploy to them, and the rules differ because
the two publish jobs are triggered differently:

| Environment | Allowed refs | Required reviewers |
| --- | --- | --- |
| `pypi` | `v*` tag | yes |
| `testpypi` | `v*` tag **and** `main` | optional |

`testpypi` needs `main` as well: the rehearsal is started by hand from `main`,
so a tag-only rule would block it.

Reviewers must have at least read access to the repository. Type the full
username and pick it from the dropdown — partial input shows no matches. Nothing
is stored until **Save protection rules** is clicked.

Leave *Prevent self-review* off while you are the only reviewer; otherwise you
cannot approve your own release and the job waits forever. Repository admins can
still bypass these rules by default.

### 4. Add maintainers

- **GitHub** — add colleagues to the organization with write access.
- **PyPI** — add them to the PyPI organization (Owner, Manager, or Member) so
  they can trigger releases and manage the project without owning it personally.

## Manual upload (fallback)

If Actions is unavailable, build and upload locally:

```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Use `__token__` as username and a PyPI API token as password. Uploads made with
a personal token do not change project ownership once the organization owns it.
