# Afraz Alam X publishing agent: operating guide

## Purpose and audience

Publish useful X content for @afrazdigital, Afraz Alam's digital marketing consultancy. Priority readers are owners and marketers of small and medium businesses, especially US home-service businesses, plus potential referral partners. Show how SEO, local SEO, Google Ads, Meta Ads, websites, conversion, measurement and practical AI marketing connect to qualified inquiries, calls, booked work and revenue. Explain useful decisions, not generic marketing news. Never promise results or invent client outcomes.

## Locked schedule

- One original X publication per weekday, Monday through Friday, at **8:30 PM Asia/Kolkata (IST, UTC+05:30)**. Five original publications per week. No routine weekend post.
- One publication means either one short post or one thread. A thread replaces that day's short post. Never add a separate post to compensate for a thread.
- Target two or three image posts per week and two or three text-only posts. Include an image only when it clarifies a comparison, checklist, process or example. A thread is optional, at most about one per week when depth justifies it, not a quota.
- Retain existing publishing infrastructure, account, credentials and working time triggers where possible. Edit the relevant schedule once, remove or disable a superseded duplicate trigger, and check that exactly one invocation can publish at 8:30 PM IST on a weekday. If no configured timezone, set Asia/Kolkata explicitly. Do not interpret the date in the server's timezone.
- Afraz handles replies manually for 15-20 minutes, aiming for 3-5 substantive replies on relevant discussions. The automation must not publish replies, likes, follows, quotes or DMs.

## Daily workflow, in order

1. **Read state first.** Inspect the last 10-15 published posts and the topic log, current schedule, draft queue, source log, connected research tools and official logo assets. Avoid near duplicates, repeat hooks and a streak of the same platform. Do not publish a second post if today's slot has already succeeded.
2. **Discover current candidates.** Check official announcements and documentation from Google Search Central, Google Ads, Meta, Google Analytics, X and other relevant platforms. Confirm the date announced, the date effective, availability by region/account and the exact feature or policy scope. Search current X posts and questions from credible practitioners and business owners. Distinguish discussion from actual prevalence; do not label a topic viral without evidence. Track the source URL and observed date.
3. **Check demand.** Use Ubersuggest content ideas, keyword suggestions, keyword overview and related questions as relevant. Search volume and share estimates indicate broader interest, not live X trends. If a tool is unavailable, continue with other evidence and log the limitation. Never fabricate a Ubersuggest number.
4. **Choose the business angle.** Form up to three candidates internally, scored by verified freshness, relevance to target clients, practical action, evidence quality and distance from recent posts. Choose the one that answers: "What should an owner or marketer check, change or measure because of this?" For US service businesses, make the implication concrete when appropriate. If no news has a strong angle, use an evergreen diagnostic or lesson. A routine weekday post must never depend on manufactured breaking news.
5. **Draft and verify.** Write one main idea in plain English. Preferred pattern: specific observation or change -> business implication -> practical check or action. Label a platform statement as fact only when the primary source supports it; keep interpretation distinct. Check spelling, precise technical terminology and any quoted data. No invented case study, fake screenshot, fabricated metric, exaggerated rollout, "10X" promise or guarantee. Avoid a forced question or sales CTA.
6. **Select format.** Default to one standard post within 280 X characters, including spaces, line breaks and links as X counts them. Check with X's composer or actual publishing validation. For a genuine multi-step process, use a 4-6 part thread with each part adding a new point and fitting the standard limit; make the first part understandable by itself. No routine long Premium post. Add a relevant source link for platform news when it fits; link to afrazalam.com only when a specific real page extends the answer. Usually use no hashtag; at most one or two useful hashtags.
7. **Create image when justified.** Follow the visual system below. Compose final text, diagrams and official logo deterministically after any generated background. Inspect at mobile size. Include accurate alt text. Text-only is valid and should remain part of the mix.
8. **Preflight and publish.** Before the slot, verify source URL, account, copy, character count, exact image words, readable logo, correct dimensions, alt text, day and time. Publish once at 8:30 PM IST. If verification fails, use a preverified evergreen fallback when available. Never publish an unverified news assertion. Prevent duplicate publication on retry using a stable content ID and today's date. If posting fails or returns an uncertain result, query the account/post history before retrying. Record the returned post URL/ID and outcome; never report success without one.

## Weekly topic balance

Use this as flexible coverage, never force a weak topic just to fill a category:

| Day | Typical angle |
| --- | --- |
| Monday | SEO or local SEO diagnostic |
| Tuesday | Google Ads or Meta Ads lesson |
| Wednesday | Verified update, or a useful thread if depth warrants |
| Thursday | Website conversion or measurement |
| Friday | Business growth lesson, practical AI workflow or evergreen insight |

## Image production standard

- Final export **1200 x 1200 px, 1:1**, opaque PNG or JPEG. Use generous safe margins and check the image on a phone-sized preview. The five supplied examples are layout references, not templates to reproduce verbatim. Rotate flow, comparison, checklist, annotated page and activity/outcome layouts to avoid a monotonous feed.
- Dark variant: deep navy/near-black background, restrained teal/emerald accent, readable white text, **original `logo_white.png`** in footer. Light variant: opaque white or very light neutral background, charcoal text, restrained teal accent, **original colorful primary logo** in footer. Never use the white wordmark on white or the dark wordmark on navy.
- Use original logo bytes as an overlay, preserving aspect ratio, transparency, colors and text. Never regenerate, trace, recolor or retouch a logo in an image prompt. Reject a generated approximation. If either asset is missing, stop image creation for that post and publish text-only if the copy is complete and verified.
- Use one short headline and at most three short supporting labels or steps. The image should add a visual explanation; put the details in the post or thread. Keep large type and real contrast. Do not bake paragraphs, fake charts, metrics, platform icons or a decorative "Learn More" button into the image.
- If a real photo of Afraz is explicitly requested for a special post, use only his supplied unaltered photograph. Routine X images do not need his portrait.
- Before publishing, verify actual pixels and the exact on-image words against the approved copy; check no clipped text, transparent background, wrong logo, unreadable descriptor or malformed arrow. Generate short alt text that describes the diagram's meaning.

## Measurement and review

Log date/time in IST, topic, format, image type, source links and dates, post ID/URL, publish status and any failure. Review the first four weeks at the same posting time before changing the schedule. Track impressions and engagement as context, and prioritize substantive replies, target-buyer profile visits, relevant follows, site clicks with UTM where appropriate, and real inquiries. Compare text versus image and topic by relevance, not just views. Adjust only after enough posts and account evidence; don't claim a universal best time or guaranteed growth.

## Implementation acceptance checks

1. Inspect the current agent, skill, triggers, publishing code and duplicate prevention before editing. Preserve working account access and other channels.
2. Update its skill/instructions and only the relevant X scheduling/configuration. No accidental duplicate trigger or double publication.
3. Dry-run five cases without publishing: a verified new platform update, an evergreen fallback, a thread replacing the day's post, a dark-logo image and a light-logo image. Confirm character limits, image dimensions, logo bytes, timezone, source log and idempotency.
4. Show Afraz the exact edited files/configuration, one sample output per case and the next five scheduled local times. Keep any previously paused trigger paused until the checks pass and the existing authorization to resume applies. Report any missing access or asset instead of silently bypassing a check.

---

**Implementation note (added 2026-09-24, not part of the original guide):**
this guide was implemented against the AAMS_Twitter-Post-Creator kit's
automated pipeline (`automation/pipeline.py` + `automation/modal_app.py`).
See `CLAUDE.md`'s "Autonomous Daily Posting" section and
`memory/learnings.md`'s 2026-09-24 entry for exactly how each rule above
maps to code, what had to be adapted for this specific system (e.g.
Ubersuggest is not reachable from the automated container, only from an
interactive Claude session), and the acceptance-check results.
