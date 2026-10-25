# 2D Tower Defense Maker

English guides, public API reference and support resources for **2D Tower Defense Maker**.

- Manual: https://hyunter777.github.io/2d-tower-defense-maker/
- API: https://hyunter777.github.io/2d-tower-defense-maker/api/
- FAQ: https://hyunter777.github.io/2d-tower-defense-maker/faq/
- Bug reports and questions: https://github.com/hyunter777/2d-tower-defense-maker/issues

## Build

Use Python 3.12, .NET 8 and DocFX 2.81.0:

```sh
python -m pip install -r requirements.txt
dotnet tool install --global docfx --version 2.81.0
python scripts/build.py --output site
```

The validated static build is published from the `gh-pages` branch with GitHub Pages. A GitHub Actions workflow template is kept in `deployment/pages-workflow.yml` for maintainers who have workflow-write permission. The committed API metadata is generated from the package; the site repository does not include implementation code or assemblies. See `scripts/generate_api.py --help` to refresh metadata from a local package checkout and installed Unity reference assemblies.

## Preview

After building, run `python -m http.server 8788 --directory site` and open the printed local address. To edit guides with automatic reload, run `python -m mkdocs serve`; the generated API is available in the combined static build.

Copyright © FlyCat. Documentation and screenshots belong to the publisher. Inter is distributed under SIL OFL 1.1; its license accompanies the font files in `docs/en/assets/fonts/`. Example snippets are intended for use with the purchased product in your own projects.

## Publish an update

After reviewing and committing documentation changes in this dedicated repository, build and publish the static artifact:

```sh
python scripts/build.py --output site
ghp-import -n -p site
```

The repository's Pages source is `gh-pages` at `/`. The `-n` option adds `.nojekyll` so GitHub serves the generated MkDocs and DocFX files directly. The source repository contains public guides and API metadata; product implementation files and assembly binaries stay in the product project.
