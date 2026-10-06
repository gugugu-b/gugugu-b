# Profile animations

Install Pillow 12.3.0 and run:

```sh
python3 scripts/build_banner.py
python3 scripts/build_activity.py
```

The activity animation uses the saved GitHub calendar in `data/contributions.json`.
To fetch a fresh calendar, provide a GitHub API token via the `GITHUB_TOKEN`
environment variable and run `python3 scripts/build_activity.py --fetch`.
Never save the token in this repository.

`profile-activity.workflow.yml` is an inactive daily-refresh template. To enable
it, place it at `.github/workflows/profile-activity.yml` using credentials with
workflow-editing permission. It fetches the calendar and commits generated
assets as `github-actions[bot]`.

The operator animation displays fixed measurements from the BW1100 baseline
decode trace. Its scan and stage lights are decorative. No benchmark values
are interpolated or simulated.
