# AAMS X agent v2

SEO-only X (Twitter) agent for Afraz Alam (@afrazdigital): SEO, AEO and GEO for Shopify, WooCommerce and custom stores. A Claude Code cloud routine publishes one post or thread Monday to Friday at 8:30 PM IST, with one first reply that carries the source and a UTM link to afrazalam.com.

- The rules: `inputs/X-STANDARD-v2.md`
- What the routine does: `automation/routine/ROUTINE-PROMPT.md`
- Repo guide for agents: `CLAUDE.md` (same as `AGENTS.md`)
- State: `memory/x-post-log.md`

## Run locally

```
pip install -r requirements.txt
python -m playwright install chromium
python automation/routine/x_today.py                    # today's pillar and format
python automation/routine/site_new.py --days 7          # new afrazalam.com pages
python automation/routine/render_card.py outputs/<folder>/draft.json
python automation/routine/validate_post.py outputs/<folder>/draft.json
python automation/routine/x_flow.py outputs/<folder>/draft.json --dry-run
python -m pytest
```

`x_flow.py` without `--dry-run` publishes to the live account. Only the scheduled routine runs it.

Credentials live in `.env` (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`) and in the cloud environment, never in git.

v1 files are in `archive/legacy_v1/`.
