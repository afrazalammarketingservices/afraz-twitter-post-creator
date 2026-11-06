# X agent v2 learnings

One dated line per real lesson, newest last. Only what changes how the next post is planned, written or checked. No keys, no em or en dashes.

Format: `- YYYY-MM-DD (pillar): what happened -> what to do next time`

## Lessons

- 2026-11-05 (myth_or_mistake): step 1 "pip install" went to Python 3.13 while "python" is 3.11, so validate_post.py failed with No module named twitter_text -> run "python -m pip install -q -r automation/routine/requirements.txt" instead
- 2026-11-06 (website_thread): render_card.py failed with "cannot import name _imaging" because Python 3.11 loaded the system Python 3.13 Pillow -> after setup run python -c "from PIL import Image"; if it fails, python -m pip install --ignore-installed --target /usr/local/lib/python3.11/dist-packages pillow
- 2026-11-06 (website_thread): a thread_cover headline of 6 words wrapped to 3 lines and pushed the button below y 1230 -> keep the cover headline to about 3 or 4 words and use only words that appear in the post
