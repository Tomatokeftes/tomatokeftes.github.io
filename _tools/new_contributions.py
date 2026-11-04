"""Bring the contributions in _data/software.yml up to date with GitHub.

    python _tools/new_contributions.py

Looks up my pull requests to other people's repositories, then adds the ones the
site does not list yet and corrects the status of those it does. Pull requests
closed without being merged are never added, and are taken off the list if they
were on it. Check the result before committing: reword new titles, and write the
description of a new project if its repository has none. A pull request you do
not want listed goes under contributions_skip in that file, so it is not added
again.

The monthly workflow in .github/workflows/new-contributions.yml runs it.
"""

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "_data" / "software.yml"
QUERY = "author:Tomatokeftes type:pr -user:Tomatokeftes -org:M4i-Imaging-Mass-Spectrometry"


def github(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "tomatokeftes.github.io contributions helper"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    request = urllib.request.Request("https://api.github.com/" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def my_pull_requests():
    """{(repo, number): (title, status)}, oldest first; status is merged, open or closed."""
    items, page = [], 1
    while True:
        found = github(f"search/issues?q={urllib.parse.quote(QUERY)}&per_page=100&page={page}")
        items += found["items"]
        if len(items) >= found["total_count"] or not found["items"]:
            break
        page += 1
    pulls = {}
    for item in sorted(items, key=lambda i: i["created_at"]):
        repo = item["repository_url"].removeprefix("https://api.github.com/repos/")
        status = "merged" if item["pull_request"].get("merged_at") else item["state"]
        pulls[repo, item["number"]] = (" ".join(item["title"].split()), status)
    return pulls


def pull_lines(number, title, status):
    return [
        f"      - number: {number}",
        f"        title: {json.dumps(title, ensure_ascii=False)}",
        f"        status: {status}",
    ]


def contributions_end(lines):
    """The index just past the contributions section."""
    start = lines.index("contributions:")
    for i in range(start + 1, len(lines)):
        if lines[i] and not lines[i].startswith(" "):
            return i
    return len(lines)


def listed_repo_end(lines, repo):
    """The index just past the last pull request of a project, or None if it is not listed."""
    try:
        i = lines.index(f"    repo: {repo}", lines.index("contributions:"))
    except ValueError:
        return None
    while i < len(lines) and lines[i].startswith("    "):
        i += 1
    return i


def update(lines, pulls):
    """Apply what GitHub says to the lines of the file, and print what changed."""
    skip = set(re.findall(r"^  - (\S+#\d+)$", "\n".join(lines[lines.index("contributions_skip:"):]), re.M))
    repo, listed = None, set()
    i = lines.index("contributions:")
    while i < contributions_end(lines):
        line = lines[i]
        if line.startswith("    repo: "):
            repo = line.split(": ", 1)[1]
        elif line.startswith("      - number: "):
            number = int(line.split(": ", 1)[1])
            listed.add((repo, number))
            status = pulls.get((repo, number), (None, None))[1]
            if status == "closed":
                print(f"Removed {repo}#{number}: closed without being merged")
                del lines[i:i + 3]
                continue
            if status and lines[i + 2] != f"        status: {status}":
                print(f"Updated {repo}#{number}: now {status}")
                lines[i + 2] = f"        status: {status}"
        i += 1

    for (repo, number), (title, status) in pulls.items():
        if (repo, number) in listed or status == "closed" or f"{repo}#{number}" in skip:
            continue
        print(f"Added {repo}#{number}: {title}")
        end = listed_repo_end(lines, repo)
        if end is None:
            description = github(f"repos/{repo}").get("description") or ""
            owner, name = repo.split("/")
            end = contributions_end(lines)
            while not lines[end - 1].strip():
                end -= 1
            new = ["", f"  - name: {name}", f"    org: {owner}", f"    repo: {repo}",
                   f"    description: {json.dumps(description, ensure_ascii=False)}", "    pull_requests:"]
            lines[end:end] = new + pull_lines(number, title, status)
        else:
            lines[end:end] = pull_lines(number, title, status)


def main():
    lines = DATA.read_text(encoding="utf-8").splitlines()
    update(lines, my_pull_requests())
    DATA.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
