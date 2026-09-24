# tomatokeftes.github.io

Personal site of Theodoros Visvikis, published at https://tomatokeftes.github.io/ by GitHub Pages from the `main` branch.

## Editing

- **Publications:** one file per paper in `_publications/`. To add a paper from its DOI:

  ```
  python _tools/new_publication.py 10.1021/jasms.6c00169
  ```

  Then check the new file: set `venue_short` (the small label above the title), and add `preprint`, `code` or `data` links if there are any. Text below the front matter is shown as the abstract.
- **News:** one file per item in `_news/`, with a `date` and a sentence or two of Markdown. If the item announces a paper, give it the paper's `doi` too, so the home page lists the paper only once.
- **Software:** `_data/software.yml`.
- **Name, menu and profile links:** `_config.yml`.
- **Look:** `assets/css/style.css`.
- **Mountains in the footer:** the ink of two Song paintings from The Met (public domain): *Summer Mountains*, attributed to Qu Ding (`assets/img/mountains-summer.webp`), and *Cloudy Mountains* by Mi Youren (`assets/img/mountains-cloudy.webp`). A page picks one with `mountains: summer` or `mountains: cloudy` in its front matter; the defaults are in `_config.yml` and the credits in `_data/mountains.yml`. `python _tools/ink_mountains.py` makes the images again, for example with a different crop.

## Preview

Build with GitHub's own Pages image (needs Docker), then serve the result. From PowerShell in this folder:

```
docker run --rm -v "${PWD}:/github/workspace" -e GITHUB_WORKSPACE=/github/workspace -e GITHUB_REPOSITORY=Tomatokeftes/tomatokeftes.github.io -e INPUT_SOURCE=. -e INPUT_DESTINATION=_site ghcr.io/actions/jekyll-build-pages:v1.0.13
python -m http.server 4000 --directory _site
```

and open http://localhost:4000.
