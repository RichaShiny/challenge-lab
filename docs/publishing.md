# Publish the interactive demo

The **Demo site** workflow builds the standalone report on every pull request. After a merge to main, it rebuilds the synthetic experiment and deploys only `_site/index.html` through GitHub Pages. Pull requests never deploy. The publishing job alone receives Pages-write and OIDC permissions.

## One-time repository setup

Before merging this change, open **Settings → Pages → Build and deployment → Source** and select **GitHub Actions**. If the repository uses environment protection, allow main to deploy to the `github-pages` environment. No personal access token or third-party hosting account is needed.

After merging, open **Actions → Demo site** and check the deployment. Its environment link is the authoritative live URL. With the repository's default Pages domain, the expected URL is:

https://richashiny.github.io/challenge-lab/

The URL is not a claim that deployment has already completed. If Pages was enabled after the merge, run **Demo site → Run workflow** against main.

## Local build

```sh
python3 pipeline.py
python3 scripts/build_site.py
```

Open `_site/index.html` locally. It contains the report and working demo-mission buttons without external libraries. The publishing folder is disposable and recreated each build. It contains no SQLite database, runtime validation logs or repository source.

All reported data remains synthetic. The mission widget simulates progress; it does not collect user data or issue rewards.

Reference: [GitHub's custom Pages workflow guide](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
