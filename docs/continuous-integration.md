# Automated validation

The **Tests** GitHub Actions workflow runs on pull requests, pushes to main, and manual dispatch. It tests Python 3.10 (the documented minimum) and 3.13 on Ubuntu with read-only repository permissions. No third-party Python packages or API keys are required.

Each job runs the experiment unit tests, regenerates the full 80,000-user synthetic dataset, and validates the outputs against SQLite. Validation checks database integrity, foreign keys, assigned and mature population counts, raw-event contribution reconciliation, finite statistical results, confidence interval ordering, and rendered report fields.

Run the same checks locally:

```sh
python3 -m unittest discover -s tests -v
python3 pipeline.py
python3 scripts/validate_outputs.py
```

A green check validates code and data consistency, not the business hypothesis or visual layout. Generated data stays out of Git. The workflows do not modify repository files remotely or automatically merge pull requests.

After the workflow has run, maintainers can optionally require its Python checks in branch protection. This change does not configure branch protection.
