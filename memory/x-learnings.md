# X agent v2 learnings

One dated line per real lesson, newest last. Only what changes how the next post is planned, written or checked. No keys, no em or en dashes.

Format: `- YYYY-MM-DD (pillar): what happened -> what to do next time`

## Lessons

- 2026-11-05 (myth_or_mistake): step 1 "pip install" went to Python 3.13 while "python" is 3.11, so validate_post.py failed with No module named twitter_text -> run "python -m pip install -q -r automation/routine/requirements.txt" instead
- 2026-11-06 (website_thread): render_card.py failed with "cannot import name _imaging" because Python 3.11 loaded the system Python 3.13 Pillow -> after setup run python -c "from PIL import Image"; if it fails, python -m pip install --ignore-installed --target /usr/local/lib/python3.11/dist-packages pillow
- 2026-11-06 (website_thread): a thread_cover headline of 6 words wrapped to 3 lines and pushed the button below y 1230 -> keep the cover headline to about 3 or 4 words and use only words that appear in the post
- 2026-11-09 (seo_fix): a single post failed the gate at 288 weighted chars and two small trims (to 283, then 282) used up both rewrite rounds, so nothing was published -> before the first gate run, aim for 240 to 265 weighted chars, and when a rewrite is needed for length cut at least 20 characters in one round
- 2026-11-12 (myth_or_mistake): a draft I estimated at about 250 chars measured 328, and round 1 landed at 281 -> measure each candidate with python -c "from twitter_text import parse_tweet" before every gate run, and keep a direct page quote short since it eats length
- 2026-11-13: In the cloud env, plain pip installs into python 3.13 while python is 3.11, so step 1 silently leaves playwright and twitter_text missing. Use python -m pip install -r automation/routine/requirements.txt and python -m playwright install --with-deps chromium; if PIL fails with _imaging, run python -m pip install --force-reinstall --no-deps pillow.
- 2026-11-18 (what_changed): the gate failed because draft.json keyword was not a phrase in the post copy -> pick the keyword as an exact phrase from the post before the first gate run
- 2026-11-19 (myth_or_mistake): publish and the read-only recent_posts.py both got 403 because api.twitter.com served a Cloudflare challenge (cf-mitigated: challenge) to the cloud IP; api.x.com answered normally with 401 unauthenticated -> before drafting, run recent_posts.py --recent 1 as an early API check, and if it is blocked log NEEDS_AFRAZ early so Afraz can publish before 9:30 PM
- 2026-11-20 (website_thread): the Cloudflare challenge on api.twitter.com blocked publishing a second day in a row while api.x.com still answers normally, and outputs/ is gitignored so a ready draft dies with the container -> on a blocked run push the ready outputs folder to the session branch with git add -f so Afraz can post it by hand; the client host needs a fix by Afraz
- 2026-11-23 (seo_fix): after the client moved to api.x.com and upload.x.com, the early read-only check and publishing both worked from the cloud IP -> keep the early recent_posts.py --recent 1 check; the Cloudflare block on api.twitter.com no longer applies
