---
name: twitter-post
description: Research a real angle, write a tweet or thread in the user's brand voice, generate the image, get approval, and publish to X (Twitter). Use when the user says "make a tweet", "post to X", "tweet this", "make a thread", or invokes /twitter-post.
---

# X (Twitter) Post Creator

Read `CLAUDE.md` at the repo root before running this skill if you haven't
already this session. It has the full operating rules, the X-specific copy
rules, and the list of things this kit deliberately does not do. This file
is the step-by-step execution flow.

## Step 1: Research

Run:
```
python .claude/skills/twitter-post/scripts/scrape.py
```
This pulls fresh content from the user's own site and every URL in
`inputs/competitors/urls.txt` via Firecrawl, and writes the findings to
`outputs/<date>_<slug>/research.json`. If `inputs/competitors/urls.txt` is
empty or missing, tell the user and ask them to add at least their own site
before continuing, don't invent research.

Never invent a trend, a statistic, or a "recent study" that wasn't actually
found in this step. If the research doesn't support a strong angle, say so
and ask the user for a topic instead of manufacturing one.

## Step 2: Angle + format decision

Read the research output. Propose exactly ONE angle, stated in a sentence,
plus a recommendation: single tweet or thread. Default to a single tweet
unless the topic genuinely needs a 5-7 tweet breakdown (a framework, a
step-by-step, a "here's everything that changed" recap). Show the angle to
the user and wait for approval or redirection before writing any copy.

## Step 3: Copy

Read `inputs/brand/` for voice notes. If empty, fall back to the Voice
Defaults and X Copy Rules in `CLAUDE.md`. Read `memory/learnings.md` and
apply anything relevant.

Draft the copy:
- **Single tweet:** one tweet, under ~250 characters where possible, ends
  with a genuine question or an explicit invite to disagree, no external
  link in the body, 0-2 hashtags max.
- **Thread:** tweet 1 is the hook (bold statement + pain point +
  counterintuitive angle + hint of proof), tweets 2-3 set up context and a
  roadmap, tweets 4-7 deliver one idea each, second-to-last summarizes,
  last tweet is the CTA. Every tweet in the thread under ~250 characters.

Rotate templates (contrarian take, hard truth, before/after with a real
number, data-driven insight, stop/start, unpopular opinion, curiosity
question) rather than defaulting to the same shape every run, check
`memory/learnings.md` for which templates the user has liked or rejected
recently.

If the user supplied a topic or draft in `inputs/copy/`, treat their draft
text as final and render it verbatim, only fill in what they explicitly
left open.

## Step 4: Creative

Run:
```
python .claude/skills/twitter-post/scripts/generate_image.py --prompt "<image concept>" --slug "<slug>" --index 1 [--ratio 16:9|1:1|4:5]
```
Default ratio is 16:9 (1200x675), X's standard post image. Use the brand
colors/fonts from `inputs/brand/` and any style reference in
`inputs/references/`. For a thread, one strong image on the hook tweet is
usually enough, don't generate one per tweet unless the user asks.

If image generation fails or produces garbled on-image text, regenerate
just that image, don't restart the whole post.

## Step 5: Approval gate (hard stop, no exceptions)

Show the user:
- The final copy (full thread if applicable, in order)
- The generated image(s)
- Where any link will go (first reply, not the body) if one is needed

Ask explicitly: publish now, or hold as a draft? Do not proceed to Step 6
without an unambiguous yes. If the user asks for changes, go back to Step 3
or Step 4 as needed and show the approval gate again.

## Step 6: Publish

Single tweet:
```
python .claude/skills/twitter-post/scripts/publish_twitter.py --text "<final copy>" --images outputs/<date>_<slug>/image_1.png --slug "<slug>"
```

Thread: write the approved thread to `outputs/<date>_<slug>/thread.json` as
a JSON array of strings (one per tweet, in order), then run:
```
python .claude/skills/twitter-post/scripts/publish_twitter.py --thread-file outputs/<date>_<slug>/thread.json --images outputs/<date>_<slug>/image_1.png --slug "<slug>"
```
The image attaches to the first tweet in the thread only.

Read the script's output. It prints the tweet ID(s) and the live URL(s),
and writes the same to `outputs/<date>_<slug>/publish_log.json`. Report
the live URL back to the user.

If a needed link belongs in the first reply, publish it as a follow-up
call with `--in-reply-to <tweet_id>` after the main post succeeds, only
after telling the user that's what you're about to do.

## Step 7: First-hour nudge

After a successful publish, tell the user: the next 30-60 minutes is when
X decides how far this goes, replying to any early comments personally
during that window is the single highest-leverage thing they can do right
now. This kit does not do that step for them, on purpose, see "What This
Kit Does Not Do" in `CLAUDE.md`.

## After every run

Ask the user for quick feedback (what worked, what to change) and append a
dated entry to `memory/learnings.md`, one or two lines, specific enough to
actually change next run's behavior. Don't ask this as a big survey, one
short question is enough.
