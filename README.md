# UofT ASIC — Education

The hub site for the UofT ASIC Team's education materials, live at https://edu.uoftasic.com/.

## Update the catalog

1. Edit [`data/courses.json`](data/courses.json). Set a course's `status` to `live` or `planned`.
2. Push to `main`. GitHub Actions runs `python3 scripts/build.py` and deploys to Pages.

To preview locally (optional):

```bash
python3 scripts/build.py
python3 -m http.server -d . 8765
# open http://127.0.0.1:8765/
```

| Field | Notes |
|-------|--------|
| `id` | Course id. A `live` course links to `https://uoftasic.com/<id>/`. |
| `title` | Course code, an em dash, then the name (`AD101 — Signals`). The hub shows the part after the dash as the name. |
| `track` | `Core`, `Analog` or `Digital` |
| `status` | `live` (linked) or `planned` (shown on the roadmap only) |
| `prereqs` | Ids of the courses this one requires. The hub places each course one level below its prerequisites. |
| `summary` | One-line description |

## Deploy

The workflow is [`.github/workflows/deploy-hub.yml`](.github/workflows/deploy-hub.yml).

In the GitHub repo, **Settings → Pages → Build and deployment → Source** must be set to **GitHub Actions**, not "Deploy from a branch".

## Related

- Shared student workspace: https://github.com/uoftasic/workspace
- Course and lab template: https://uoftasic.com/course-template/
