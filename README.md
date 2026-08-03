# UofT ASIC — Education

Hub site for UofT ASIC Team education materials.

**Live:** https://edu.uoftasic.com/

## Update the catalog

1. Edit [`data/courses.json`](data/courses.json) — set `status` to `live` or `planned`.
2. Push to `main`. GitHub Actions runs `python3 scripts/build.py` and deploys Pages.

Local preview (optional):

```bash
python3 scripts/build.py
python3 -m http.server -d . 8765
# open http://127.0.0.1:8765/
```

| Field | Notes |
|-------|--------|
| `id` | Course id → link `https://uoftasic.com/<id>/` when `live` |
| `track` | `Core`, `Analog`, or `Digital` |
| `status` | `live` (linked) or `planned` (roadmap only) |
| `summary` | One-line description |

## Deploy

Workflow: [`.github/workflows/deploy-hub.yml`](.github/workflows/deploy-hub.yml)

GitHub repo **Settings → Pages → Build and deployment → Source** must be **GitHub Actions** (not “Deploy from a branch”).

## Related

- Shared student workspace: https://github.com/uoftasic/workspace
- Course / lab template: https://uoftasic.com/course-template/
