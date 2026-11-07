"""Create GitHub labels, milestones and story issues from docs/backlog.md.

Epics are not issues: they are the epic:* labels and the Epic field on the Projects board.

Idempotent: anything that already exists (matched by name or title) is skipped.

Usage:
    python3 scripts/setup_github.py            # dry run, prints what it would do
    python3 scripts/setup_github.py --apply    # creates everything
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "rxv801/gta6-market-sentiment"
BACKLOG = Path(__file__).resolve().parent.parent / "docs" / "backlog.md"
APPLY = "--apply" in sys.argv

EPIC_COLOR = "5319e7"
LABELS = {
    "type:story": ("0e8a16", "Deliverable piece of work"),
    "size:S": ("c2e0c6", "About 1 hour"),
    "size:M": ("fef2c0", "About 2-4 hours"),
    "size:L": ("f9d0c4", "A full session"),
    "priority:P0": ("b60205", "Blocks a deadline"),
    "priority:P1": ("d93f0b", "Needed for v1.0"),
    "priority:P2": ("fbca04", "Nice to have"),
}


def gh(*args, input_json=None):
    cmd = ["gh", "api", *args]
    if input_json is not None:
        cmd += ["--input", "-"]
    out = subprocess.run(
        cmd,
        input=json.dumps(input_json) if input_json is not None else None,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out) if out.strip() else None


def gh_list(path):
    return gh("--paginate", "--slurp", path)


def parse_backlog():
    text = BACKLOG.read_text()

    epics = dict(re.findall(r"^\| ([A-Z]+) \| ([^|]+?) \|$", text.split("## Epics")[1].split("##")[0], re.M))

    milestones, stories = [], []
    stories_text = text.split("## Stories")[1].split("## Board setup")[0]
    for block in re.split(r"^### ", stories_text, flags=re.M)[1:]:
        header = block.splitlines()[0]
        name, due = re.match(r"(.+) \(due (\d{4}-\d{2}-\d{2})\)", header).groups()
        note = block.splitlines()[2].strip()
        milestones.append({"title": name, "due": due, "description": note})
        for sid, title, size, pri, ac in re.findall(
            r"^\| ([A-Z]+-\d+) \| (.+?) \| ([SML]) \| (P\d) \| (.+?) \|$", block, re.M
        ):
            stories.append(
                {
                    "id": sid,
                    "epic": sid.split("-")[0],
                    "title": title,
                    "size": size,
                    "priority": pri,
                    "ac": ac,
                    "milestone": name,
                }
            )
    return epics, milestones, stories


def story_body(s, epics):
    criteria = "\n".join(f"- [ ] {c.strip()}" for c in s["ac"].split(";"))
    return (
        f"**Epic:** {s['epic']} ({epics[s['epic']]})  \n"
        f"**Size:** {s['size']} · **Priority:** {s['priority']}\n\n"
        f"## Acceptance criteria\n{criteria}\n\n"
        f"## Notes\n_Add implementation notes, links and decisions here._\n"
    )


def main():
    epics, milestones, stories = parse_backlog()
    print(f"Parsed {len(epics)} epics, {len(milestones)} milestones, {len(stories)} stories")
    print("Mode:", "APPLY" if APPLY else "DRY RUN (pass --apply to create)")

    # Labels
    existing_labels = {label["name"] for page in gh_list(f"repos/{REPO}/labels") for label in page}
    all_labels = dict(LABELS)
    for key, name in epics.items():
        all_labels[f"epic:{key}"] = (EPIC_COLOR, name)
    for name, (color, desc) in all_labels.items():
        if name in existing_labels:
            continue
        print("label    +", name)
        if APPLY:
            gh(f"repos/{REPO}/labels", input_json={"name": name, "color": color, "description": desc})

    # Milestones
    existing_ms = {m["title"]: m["number"] for page in gh_list(f"repos/{REPO}/milestones?state=all") for m in page}
    for m in milestones:
        if m["title"] in existing_ms:
            continue
        print("milestone+", m["title"], m["due"])
        if APPLY:
            created = gh(
                f"repos/{REPO}/milestones",
                input_json={
                    "title": m["title"],
                    "description": m["description"],
                    "due_on": f"{m['due']}T12:00:00Z",
                },
            )
            existing_ms[m["title"]] = created["number"]

    # Story issues
    existing_issues = {
        i["title"] for page in gh_list(f"repos/{REPO}/issues?state=all") for i in page if "pull_request" not in i
    }

    for s in stories:
        title = f"[{s['id']}] {s['title']}"
        if title in existing_issues:
            continue
        print("story    +", title, "→", s["milestone"])
        if APPLY:
            gh(
                f"repos/{REPO}/issues",
                input_json={
                    "title": title,
                    "body": story_body(s, epics),
                    "labels": ["type:story", f"epic:{s['epic']}", f"size:{s['size']}", f"priority:{s['priority']}"],
                    "milestone": existing_ms[s["milestone"]],
                },
            )

    print("Done.")


if __name__ == "__main__":
    main()
