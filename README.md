# Building 20 Ventures

Zola billboard website for Building 20 Ventures, LLC, using the Seagull theme.

| Branch | Published URL |
| --- | --- |
| `production` | https://building20.vc/ |
| `main` | https://building20.vc/staging/ |

## Local development

Install **Zola 0.22.1**, Make, and Python 3.10 or newer. No Python packages are
required. All build, preview, and test commands go through the Makefile:

```sh
make build      # production output in public/
make staging    # staging output in .tmp/staging/
make test       # Zola checks, both builds, link/asset checks, deployment tests
make preview    # http://127.0.0.1:1111/ and /staging/ on the same local server
make serve      # Zola live reload for site editing
```

Edit `content/about.md` and `content/contact.md` for the placeholder text.
The homepage headline is in `templates/home.html`; layout overrides and colors
are in `templates/` and `sass/`. The login page redirects to
`https://mail.google.com/a/building20.vc`; change `extra.workspace_login` in
`config.toml` if another Workspace application is preferred.

Original images remain in `art/`. `make` copies them unchanged into generated
`static/art/` before building. `art/3.png` has background RGB **252, 249, 242**
(`#FCF9F2`), measured at all four corners and as its dominant pixel color;
the site uses that exact color. The banner credits the MIT Museum.

## Deployment

`.github/workflows/pages.yml` runs on every push to `main` or `production`, or
on a manual dispatch. Both branches must exist. It checks out the current
`production` branch for the root site and current `main` for `/staging/`, builds
both with their own URLs, and publishes **one combined Pages artifact**. A
staging push never promotes its content into the root site. Deleted files are
removed on the next deployment. The workflow fails if either build is missing
instead of substituting staging for production.

One shared concurrency group covers the full build and deployment, without
cancelling active deployments. Checkouts occur after acquiring that lock so
queued runs read current branch heads. GitHub can coalesce pending runs; the
eventual deployment includes the latest content from both branches. Deployment
tooling comes from `main`, while production templates and content come from
`production`. Each branch must retain a compatible `make build` interface.

To release reviewed changes, open a PR **from `main` into `production`** and
merge it. Main remains the staging branch. For rollback, revert the relevant
commit on `production`; its push deploys the rollback. PRs run `make test`
without deploying. Initial setup creates both branches with the same site.

Staging is public, labeled as a preview, and has `noindex, nofollow` metadata.
Production `robots.txt` disallows `/staging/`. This discourages indexing; it is
not access control. GitHub Pages serves the root `404.html` for missing paths,
including paths below `/staging/`.

## GitHub Pages setup

1. The repository must be public on GitHub Free. Private organization Pages
   requires GitHub Team or an eligible Enterprise plan.
2. In **Settings → Pages**, select **GitHub Actions** as the publishing source.
3. In **Settings → Environments → github-pages**, permit deployments from both
   `main` and `production` (use selected branches if protection is desired).
4. Set the custom domain to **building20.vc** before pointing DNS at GitHub.
5. Run **Publish production and staging** if the initial pushes predate setup.
6. Once DNS and certificate issuance complete, enable **Enforce HTTPS**.

For a custom Actions deployment, GitHub uses the Pages custom-domain setting;
a repository `CNAME` file is not required. No deploy key or personal access
token is needed by the workflow; it uses the repository `GITHUB_TOKEN` and OIDC.

## DNS

At the DNS provider for `building20.vc`, add these records (TTL 3600 is fine):

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `building-20-ventures.github.io` |

Optional IPv6: add four `AAAA` records at `@`, with values
`2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, and
`2606:50c0:8003::153`. Replace conflicting website A/AAAA records, but preserve
Google Workspace MX and TXT records (SPF, DKIM, verification, and DMARC).
Do not put a CNAME at the apex alongside Workspace MX records.

There is **no staging DNS record**: `/staging/` is a path on the same host.
The `www` CNAME points to the organization host, without `/website` or a URL
scheme. GitHub redirects `www` to the configured apex domain. If the DNS
provider offers a proxy/CDN, use DNS-only during GitHub certificate setup.

In the organization’s **Settings → Pages**, verify domain ownership using
the TXT record GitHub provides. Its value is unique; copy it from GitHub.
DNS propagation and HTTPS availability can take up to 24 hours.

Reference: [GitHub custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## Theme and credits

`themes/seagull/` vendors the runtime directories and metadata from
[Seagull](https://git.lacontrevoie.fr/HugoTrentesaux/seagull), by Hugo Trentesaux,
at commit `e87e14d59d1097a15331ee2a48d290688809340c`, the version listed in
Zola’s theme catalog when this site was created. It is declared **AGPL** by
upstream. Theme files are unchanged; custom templates and Sass live at the
site root. Keep upstream attribution and licensing when updating the theme.
This version works with the pinned Zola 0.22.1 toolchain; newer Seagull
versions use different template syntax and require a coordinated upgrade.

Banner: `Serendipity_turning-points-serendipity.webp`, credited to the MIT Museum.
Company logo: `3.png`. Image rights remain with their respective owners.
Copyright © 2026 Building 20 Ventures, LLC.
