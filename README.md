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
| `track` | `Core`, `Analog` or `Digital`. IC101 is the Core course the hub shows at the top under "Start here". The other Core courses, IC102 and PCB101, get a ladder of their own, headed "For both tracks", below the two tracks. The track blurbs, and that ladder's heading and blurb, are in `scripts/build.py`. |
| `status` | `live` (linked) or `planned` (shown on the roadmap only) |
| `prereqs` | Ids of the courses this one requires. The hub places each course one level below its prerequisites. A `group` id, such as `dd105`, means either version of that course, and `build.py` stops with an error on an id that is neither a course nor a group. |
| `summary` | What a student does in the course, in a sentence or two |

Some courses come in versions that teach the same thing with different tools, and a student takes only one of them, as with DD105-A and DD105-B, or IC102-A and IC102-D. Each version has its own entry, with these four fields as well:

| Field | Notes |
|-------|--------|
| `group` | The id the versions share (`dd105`). The hub shows them as one step in the ladder, split between the versions, with the group id as its code and the name from the first version's `title`. It counts them as one course in its totals of open courses. The versions must have the same `track` and `prereqs`, and `build.py` stops with an error if they don't. |
| `variant` | The version's letter (`A`, `B`; IC102 uses `A` for analog and `D` for digital). The hub shows the versions in letter order. |
| `label` | What the version uses, such as `SystemVerilog and UVM, on Verilator`. |
| `pick` | One sentence on who should take this version. |

## Deploy

The workflow is [`.github/workflows/deploy-hub.yml`](.github/workflows/deploy-hub.yml).

In the GitHub repo, **Settings → Pages → Build and deployment → Source** must be set to **GitHub Actions**, not "Deploy from a branch".

## Related

- Shared student workspace: https://github.com/uoftasic/workspace
- Course and lab template: https://uoftasic.com/course-template/
