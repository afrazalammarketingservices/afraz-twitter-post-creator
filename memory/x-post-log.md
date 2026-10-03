# X post log (AAMS X Post routine)

Source of truth for idempotency, the 30-day topic check, CTA rotation and
weekly mix. Replaces the Modal Dict state. One row per publish attempt.
Status is one of PUBLISHED, NEEDS_AFRAZ, SKIPPED, DRY_RUN. Never put a key
or token in this file.

| IST date | Day | Reader | Format | Image layout | Topic | Topic key | Sources (with dates) | Post ID | Permalink | CTA variant | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
