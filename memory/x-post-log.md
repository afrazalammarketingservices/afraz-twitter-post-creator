# X post log (AAMS X Post routine)

Source of truth for idempotency, the 30-day topic check, CTA rotation and
weekly mix. Replaces the Modal Dict state. One row per publish attempt.
Status is one of PUBLISHED, NEEDS_AFRAZ, SKIPPED, DRY_RUN. Notes holds
non-blocking flags such as ALT_TEXT_FAILED (the post is live, the alt text
call failed) and "manual test" (a run Afraz started by hand; it counts for
the once-a-day check on its own date only). Never put a key or token in
this file.

| IST date | Day | Reader | Format | Image layout | Topic | Topic key | Sources (with dates) | Post ID | Permalink | CTA variant | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-03 | Sat | home-service | single | comparison | Judge Google pay-per-lead ads by cost per booked job, not cost per lead, by marking each lead Booked | cost-per-booked-job-lead-status | Google Ads Help, About goals and leads for pay-per-lead goals, https://support.google.com/google-ads/answer/17325352, undated page, accessed 2026-10-03 | none | none | none (not posted) | NEEDS_AFRAZ | manual test; Thursday row used per run message; draft and image passed validation, publish call blocked by the session permission classifier before it ran, nothing posted |
