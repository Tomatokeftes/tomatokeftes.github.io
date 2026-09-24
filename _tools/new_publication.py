"""Add a paper to the site's publication list, from its DOI.

    python _tools/new_publication.py 10.1038/s41592-026-03155-1

Looks the DOI up on Crossref and writes _publications/<date>-<words>.md with
the title, authors, venue, citation and a BibTeX entry. Check the new file
before committing: set a short venue name for the badge, and add links to a
preprint, code or data where there are any. Text below the front matter is
shown as the abstract. Pass --stdout to print the entry instead of writing it.
"""

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
ME = "Visvikis"  # family name kept when a long author list is shortened
MAX_AUTHORS = 10  # author lists longer than this are shortened for display
STOP_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from",
    "in", "into", "is", "of", "on", "the", "to", "with",
}


def crossref(doi):
    request = urllib.request.Request(
        f"https://api.crossref.org/works/{doi}",
        headers={"User-Agent": "tomatokeftes.github.io publication helper"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["message"]


def first_date(message, *keys):
    """The first of the given Crossref dates that is set, as [year, month, day]."""
    for key in keys:
        parts = (message.get(key) or {}).get("date-parts", [[None]])[0]
        if parts and parts[0]:
            return parts + [1] * (3 - len(parts))
    return None


def words(text):
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", ascii_text.lower())


def initials(given):
    # "Ron M.A." -> "R. M. A.", "Wouter-Michiel" -> "W.-M."
    return " ".join(
        "-".join(part[0] + "." for part in word.split("-") if part)
        for word in given.replace(".", " ").split()
    )


def people(message):
    """(given, family) for each author; group authors have no given name."""
    authors = []
    for author in message.get("author", []):
        if "family" in author:
            given = re.sub(r"\.(?=\S)", ". ", author.get("given", ""))  # "M.A." -> "M. A."
            authors.append((given, author["family"]))
        elif author.get("name") and not author["name"].lower().startswith("on behalf of"):
            authors.append((None, author["name"]))
    return authors


def author_line(authors):
    """The authors as shown on the site, shortened when the list is long."""
    names = [f"{initials(g)} {f}" if g else f for g, f in authors]
    if len(names) <= MAX_AUTHORS:
        return ", ".join(names), None
    mine = [i for i, (_, family) in enumerate(authors) if family == ME]
    parts, last = [], -1
    for i in sorted({0, 1, 2, len(names) - 1, *mine}):
        if i > last + 1:
            parts.append("…")
        parts.append(names[i])
        last = i
    return ", ".join(parts), len(names)


def entry(doi):
    """The file name and text of the publication entry for a DOI."""
    m = crossref(doi)
    title = " ".join(m["title"][0].split())
    authors = people(m)
    shown, count = author_line(authors)
    preprint = m.get("type") == "posted-content"
    if preprint:
        venue = (m.get("institution") or [{}])[0].get("name", "Preprint")
        short = venue
    else:
        venue = m["container-title"][0]
        short = (m.get("short-container-title") or [venue])[0]

    online = first_date(m, "published-online", "issued", "published")
    printed = first_date(m, "published-print")
    year = (printed or online)[0]
    volume, issue = m.get("volume"), m.get("issue")
    pages, number = m.get("page"), m.get("article-number")
    citation = ""
    if volume:
        citation = volume + (f"({issue})" if issue else "")
        if pages or number:
            citation += ", " + (pages.replace("-", "–") if pages else number)

    key_word = next((w for w in words(title) if w not in STOP_WORDS), "paper")
    key = "".join(words(authors[0][1])) + str(year) + key_word
    bib_authors = " and ".join(
        f"{family}, {given}" if given else "{" + family + "}" for given, family in authors
    )
    fields = [("title", title), ("author", bib_authors)]
    fields.append(("publisher" if preprint else "journal", venue))
    fields.append(("year", str(year)))
    if volume:
        fields.append(("volume", volume))
    if issue:
        fields.append(("number", issue))
    if pages or number:
        fields.append(("pages", pages.replace("-", "--") if pages else number))
    fields.append(("doi", doi))
    width = max(len(name) for name, _ in fields)
    bibtex = "@%s{%s,\n%s\n}" % (
        "misc" if preprint else "article",
        key,
        ",\n".join(f"  {name.ljust(width)} = {{{value}}}" for name, value in fields),
    )

    front = [("title", title), ("authors", shown)]
    if count:
        front.append(("author_count", count))
    front += [("venue", venue), ("venue_short", short)]
    if citation:
        front.append(("citation", citation))
    if preprint:
        front.append(("type", "preprint"))
    has_preprint = (m.get("relation") or {}).get("has-preprint") or []
    front += [("year", year), ("date", "%04d-%02d-%02d" % tuple(online[:3])), ("doi", doi)]
    if has_preprint:
        front.append(("preprint", "https://doi.org/" + has_preprint[0]["id"]))

    lines = ["---"]
    for name, value in front:
        shown_value = value if isinstance(value, int) or name == "date" else json.dumps(value, ensure_ascii=False)
        lines.append(f"{name}: {shown_value}")
    lines.append("bibtex: |")
    lines += ["  " + line for line in bibtex.splitlines()]
    lines.append("---")
    slug = "-".join([w for w in words(title) if w not in STOP_WORDS][:4])
    name = "%04d-%02d-%02d-%s.md" % (*online[:3], slug)
    return name, "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("doi", help="the paper's DOI, with or without https://doi.org/")
    parser.add_argument("--stdout", action="store_true", help="print the entry instead of writing it")
    args = parser.parse_args()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", args.doi.strip(), flags=re.I)

    name, text = entry(doi)
    if args.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(text)
        return

    folder = SITE / "_publications"
    for existing in folder.glob("*.md"):
        if doi.lower() in existing.read_text(encoding="utf-8").lower():
            sys.exit(f"{doi} is already listed in {existing.relative_to(SITE)}")
    path = folder / name
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path.relative_to(SITE)}")


if __name__ == "__main__":
    main()
