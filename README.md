# X (Twitter) Post Creator

Research a real angle, write the post (single tweet or thread), generate the
image, and publish it straight to your X profile, all from one Claude Code
/ Antigravity workspace. Built to sit next to your Facebook Post Creator,
Instagram Carousel Creator, and LinkedIn Post Creator kits.

You bring the **brand kit**, the **competitor/niche URLs**, and optionally a
**topic or draft**. The kit handles research, copy, image, and publishing.

---

## What makes this different

- **Grounded, not generic.** It scrapes your own site and real competitor
  or niche pages before writing anything, so the angle is based on
  something current, not an AI guess or an invented statistic.
- **Built around how X actually ranks content**, not generic social media
  advice: no links in the post body, replies over likes, image on every
  post, threads for anything that earns the length. See "X Copy Rules" in
  `CLAUDE.md` for the full list.
- **One approval gate.** Nothing goes live on your profile without you
  seeing the final copy and image first and saying yes.
- **Self-learning.** Every time you give feedback, the skill remembers and
  applies it next time.
- **Stays inside a human-approved workflow on purpose.** It does not
  auto-reply, auto-follow, or run unattended. See "What This Kit Does Not
  Do" in `CLAUDE.md` for why, it's a deliberate choice to stay compliant
  with X's automation policy and to protect your named, personal profile.

---

## Setup (20-30 minutes, mostly one-time)

### 1. Drop this folder into your workspace

Move the unzipped `twitter-post-creator/` into your Antigravity (or Claude
Code) workspace and open it as a project.

### 2. Install Python deps

```bash
pip install -r requirements.txt
```

### 3. Get your Gemini key

Free at https://aistudio.google.com/apikey, generous free tier. Same key
type your Facebook and Instagram kits use, you can reuse the same key here.

### 4. Get your Firecrawl key

https://firecrawl.dev, needed to scrape your site and competitor/niche
sites for angles. Reuse your existing key if you already have one.

### 5. Get your X API credentials (the part that's specific to this kit)

X changed its API access model. As of 2026 there is no longer a free
posting tier for new developer accounts. **Verify current pricing at
https://developer.x.com/en/portal/products before you sign up, it changes
without much notice.** The general shape at the time this kit was built:

- **Pay-per-use** is the default for new developer accounts: roughly
  $0.015 per post created (higher if the post contains a link, which this
  kit avoids anyway per the copy rules), billed as credits. For your
  posting volume (a handful of posts a day), this runs to a few dollars a
  month, not a subscription-sized cost.
- Legacy fixed tiers (Basic at $200/month, Pro at $5,000/month) still exist
  for accounts that subscribed before the pay-per-use switch, but are not
  what a new signup gets. Do not assume you need one of these, check your
  actual account first.

**Steps:**

1. Go to **developer.x.com** and apply for a developer account if you don't
   have one (this is separate from your regular X login, it's a developer
   portal account tied to your X account).
2. Create a new **Project**, then an **App** inside it. Name it something
   like "Afraz Alam X Publisher."
3. In the App's settings, set **User authentication settings** to Read and
   Write (this is required, the default is often read-only).
4. Under **Keys and tokens**, generate:
   - **API Key and Secret** (this is your app's consumer key/secret)
   - **Access Token and Secret** (generate these *with Read and Write
     permission selected*, they're tied to your own X account since you're
     both the developer and the account owner)
5. Confirm your billing/payment method is set up in the developer portal if
   your account is on the pay-per-use model, posting will fail without it.

That's four values total: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`,
`X_ACCESS_TOKEN_SECRET`. All four are OAuth 1.0a credentials, used for both
the image upload step and the tweet creation step.

### 6. Configure `.env`

```bash
cp .env.example .env
```

Open `.env` and paste in your values. Save. Never commit this file, never
upload it anywhere, never paste its contents in chat.

### 7. Add your competitor/niche URLs

Open `inputs/competitors/urls.txt` and list your own site plus 1-3
competitor or niche sites (marketing blogs, tools you reference, accounts
you respect), one per line.

### 8. Point it at your existing brand kit (optional but recommended)

If `inputs/brand/` already exists for your Facebook or Instagram kit, copy
those same voice/color notes into this kit's `inputs/brand/` folder so your
voice stays consistent across every channel. X can run a slightly more
casual, opinionated register than LinkedIn or Facebook, decide if you want
that distinction and note it in `inputs/brand/voice.md`.

### 9. Run it

In Claude Code or Antigravity, type:

```
/twitter-post
```

or just say:

> "Make me a tweet." / "Make me a thread about X." / "Post to X."

The skill takes over: research, angle, copy, image, approval, publish.

---

## How a typical run looks

**1. Research** — the agent scrapes your site and the URLs in
`inputs/competitors/urls.txt` via Firecrawl.

**2. Angle + format** — it proposes one sharp, specific angle and whether
it's a single tweet or a thread. You approve or redirect.

**3. Copy** — it drafts the post in your brand voice, following X's actual
ranking rules (no link in the body, ends with a real question, specific
numbers not platitudes).

**4. Creative** — Gemini image generation renders a 1200x675 image by
default (X's standard post ratio).

**5. Approval** — you see the final copy and image together, and the full
thread if applicable. You say publish or hold.

**6. Publish** — only after your yes, it posts directly to your X profile
via the X API and logs the live post ID(s) and URL.

**7. Feedback** — same as your other kits, whatever you say gets saved to
`memory/learnings.md` and applied automatically next time.

---

## Folder structure

```
twitter-post-creator/
├── CLAUDE.md              # Instructions Claude reads on startup
├── README.md              # You're reading this
├── .env                   # Your keys and tokens (you create from .env.example)
├── .env.example
├── requirements.txt
├── inputs/
│   ├── brand/             # Brand kit + voice notes
│   ├── competitors/       # urls.txt — sites to scan for angles
│   ├── references/        # Post styles to match
│   ├── photos/            # Optional founder/team photos
│   └── copy/              # Optional topic or draft copy
├── outputs/                # Finished posts (dated, includes publish_log.json)
├── memory/
│   └── learnings.md       # The skill's memory
└── .claude/skills/twitter-post/    # The skill that does everything
    ├── SKILL.md
    └── scripts/
        ├── scrape.py
        ├── generate_image.py
        └── publish_twitter.py
```

---

## Costs

- Gemini image generation: roughly $0.05-$0.08 per image, same as your
  other kits.
- Firecrawl: free tier covers light research use, check firecrawl.dev for
  current limits.
- X API posting: pay-per-use credits, roughly $0.015 per post at the time
  this kit was built. Confirm current pricing in your developer portal
  before relying on this number, X has changed its pricing model more than
  once.

---

## Security rules (read this before you use it)

- Keys and tokens live in `.env` only, never in chat, never in a committed
  file, never uploaded anywhere as an attachment.
- If a key or token is ever exposed, rotate it immediately in that
  provider's dashboard (developer.x.com, aistudio.google.com, firecrawl.dev)
  before running this kit again.
- Nothing publishes to your profile without you approving the copy and
  image first, every single run, until you explicitly decide otherwise.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Missing API key" | Check `.env` has all values filled in, no quotes |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Publish fails with `403 Forbidden` | Your App's user authentication settings are still Read-only, go back and set Read and Write, then regenerate the Access Token and Secret (old tokens keep the old permission level) |
| Publish fails with `401 Unauthorized` | One of the four X credentials is wrong or was regenerated since you copied it into `.env` |
| Publish fails with a billing/payment error | Your developer account is on pay-per-use and needs a payment method on file in the developer portal |
| Image has garbled on-image text | Regenerate just that image, don't re-run the whole post |
| Thread posts out of order or as separate unlinked tweets | Check `publish_log.json` for the `in_reply_to_tweet_id` chain, this usually means one tweet in the middle failed and the chain broke, republish from that point manually |
