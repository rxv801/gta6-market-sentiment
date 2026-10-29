"""Create the GitHub Projects board and add every story issue with its Epic, Priority, Size and Status.

Idempotent: reuses the project, fields and items if they already exist.

Usage:
    python3 scripts/setup_project.py
"""

import json
import re
import subprocess

OWNER = "rxv801"
REPO = "gta6-market-sentiment"
TITLE = "GTA VI Study"

STATUSES = [
    ("Backlog", "GRAY", "Not planned for the current week"),
    ("Ready", "BLUE", "Planned for the current week"),
    ("In progress", "YELLOW", "Being worked on"),
    ("Review", "PURPLE", "PR open, waiting for review"),
    ("Done", "GREEN", "Merged and meets the definition of done"),
]
FIELDS = {
    "Epic": ["DOC", "GOV", "OPS", "ING", "RES", "WH", "AN", "ML", "BI"],
    "Priority": ["P0", "P1", "P2"],
    "Size": ["S", "M", "L"],
}
# Stories already started; everything else in the current milestone starts as Ready.
CURRENT_MILESTONE = "M0 – Kickoff"
IN_PROGRESS = {"DOC-1", "OPS-4"}


def run(*args):
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out.strip().startswith(("{", "[")) else out


def graphql(query, **variables):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    return run(*args)["data"]


def main():
    projects = run("gh", "project", "list", "--owner", OWNER, "--format", "json")["projects"]
    project = next((p for p in projects if p["title"] == TITLE), None)
    if project is None:
        project = run("gh", "project", "create", "--owner", OWNER, "--title", TITLE, "--format", "json")
        run("gh", "project", "link", str(project["number"]), "--owner", OWNER, "--repo", f"{OWNER}/{REPO}")
        print("Created project", project["url"])
    num, pid = str(project["number"]), project["id"]

    fields = {
        f["name"]: f for f in run("gh", "project", "field-list", num, "--owner", OWNER, "--format", "json")["fields"]
    }

    # Status: replace the default Todo / In Progress / Done options with our workflow.
    status = fields["Status"]
    if [o["name"] for o in status["options"]] != [s[0] for s in STATUSES]:
        options = ", ".join(f'{{name: "{n}", color: {c}, description: "{d}"}}' for n, c, d in STATUSES)
        graphql(
            f"mutation($id: ID!) {{ updateProjectV2Field(input: {{fieldId: $id, singleSelectOptions: [{options}]}}) "
            "{ projectV2Field { ... on ProjectV2SingleSelectField { id } } } }",
            id=status["id"],
        )
        print("Updated Status options")

    for name, options in FIELDS.items():
        if name not in fields:
            run(
                "gh",
                "project",
                "field-create",
                num,
                "--owner",
                OWNER,
                "--name",
                name,
                "--data-type",
                "SINGLE_SELECT",
                "--single-select-options",
                ",".join(options),
            )
            print("Created field", name)

    fields = {
        f["name"]: f for f in run("gh", "project", "field-list", num, "--owner", OWNER, "--format", "json")["fields"]
    }
    option_id = {name: {o["name"]: o["id"] for o in fields[name]["options"]} for name in ["Status", *FIELDS]}

    existing = {
        i["content"]["url"]: i["id"]
        for i in run("gh", "project", "item-list", num, "--owner", OWNER, "--limit", "500", "--format", "json")["items"]
        if i.get("content", {}).get("url")
    }

    issues = run(
        "gh",
        "issue",
        "list",
        "--repo",
        f"{OWNER}/{REPO}",
        "--label",
        "type:story",
        "--state",
        "all",
        "--limit",
        "500",
        "--json",
        "url,title,labels,milestone",
    )
    for issue in issues:
        if issue["url"] in existing:
            continue
        sid = re.match(r"\[([A-Z]+-\d+)\]", issue["title"]).group(1)
        labels = dict(label["name"].split(":", 1) for label in issue["labels"])
        if sid in IN_PROGRESS:
            status_name = "In progress"
        elif issue["milestone"] and issue["milestone"]["title"] == CURRENT_MILESTONE:
            status_name = "Ready"
        else:
            status_name = "Backlog"

        item_id = run("gh", "project", "item-add", num, "--owner", OWNER, "--url", issue["url"], "--format", "json")[
            "id"
        ]
        values = {
            "Status": status_name,
            "Epic": labels["epic"],
            "Priority": labels["priority"],
            "Size": labels["size"],
        }
        for field, value in values.items():
            run(
                "gh",
                "project",
                "item-edit",
                "--id",
                item_id,
                "--project-id",
                pid,
                "--field-id",
                fields[field]["id"],
                "--single-select-option-id",
                option_id[field][value],
            )
        print(f"Added {sid:7} {status_name}")

    print("Board:", project["url"])


if __name__ == "__main__":
    main()
