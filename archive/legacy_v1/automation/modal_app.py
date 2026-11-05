"""
Modal deployment for the automated X (Twitter) posting pipeline.

Deploy:    modal deploy automation/modal_app.py
Live test: modal run automation/modal_app.py::pipeline_entrypoint
Dry-run acceptance check (5 cases, no publish):
           modal run automation/modal_app.py::dry_run_acceptance

See automation/README.md for one-time setup (the twitter-post-secrets
bundle) and CLAUDE.md's "Autonomous Daily Posting" section for the full
decision history behind this rebuild, 2026-09-24, against
AAMS-X-Agent-Operating-Guide.md.
"""
import json
from pathlib import Path

import modal

PROJECT_ROOT = Path(__file__).resolve().parent.parent

app = modal.App("twitter-post-automation")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "anthropic",
        "google-genai>=0.3.0",
        "firecrawl-py==4.38.0",
        "requests>=2.31.0",
        "tweepy>=4.14.0",
        "pillow>=10.0.0",
    )
    .add_local_dir(str(PROJECT_ROOT / "inputs" / "brand"), remote_path="/bundled/brand")
    .add_local_file(
        str(PROJECT_ROOT / "inputs" / "competitors" / "urls.txt"),
        remote_path="/bundled/urls.txt",
    )
    .add_local_file(
        str(PROJECT_ROOT / ".claude" / "skills" / "twitter-post" / "SKILL.md"),
        remote_path="/bundled/SKILL.md",
    )
    .add_local_file(
        str(PROJECT_ROOT / "CLAUDE.md"),
        remote_path="/bundled/CLAUDE.md",
    )
    .add_local_file(
        str(PROJECT_ROOT / "memory" / "learnings.md"),
        remote_path="/bundled/learnings.md",
    )
    .add_local_python_source("pipeline")
)

secrets = [modal.Secret.from_name("twitter-post-secrets")]
dryrun_volume = modal.Volume.from_name("twitter-post-dryrun", create_if_missing=True)
DRYRUN_PATH = "/dryrun"


@app.function(image=image, secrets=secrets, timeout=600)
def run_pipeline():
    import pipeline
    return pipeline.run()


# --- Scheduled trigger: Mon-Fri, 8:30 PM IST (15:00 UTC) ---
#
# Changed 2026-09-24 from 7:30 PM to 8:30 PM IST per
# AAMS-X-Agent-Operating-Guide.md's locked schedule. This is the app's
# ONLY scheduled function (Modal's workspace-wide 5-scheduled-function cap
# is otherwise fully used by LinkedIn/Instagram/Facebook's automations -
# see CLAUDE.md's "Deploy dependency" note).

@app.function(image=image, secrets=secrets, timeout=600,
               schedule=modal.Cron("0 15 * * 1-5"))
def scheduled_run():
    run_pipeline.remote()


# --- Manual live test: `modal run automation/modal_app.py::pipeline_entrypoint` ---
# Publishes for real - same as the scheduled path, just triggered by hand.

@app.local_entrypoint()
def pipeline_entrypoint():
    run_pipeline.remote()


# --- Dry-run acceptance check: the 5 cases from AAMS-X-Agent-Operating-Guide.md ---
# `modal run automation/modal_app.py::dry_run_acceptance`
# Calls the real Anthropic + Gemini APIs (so it costs the same as a normal
# run) but never calls the X publish endpoints. Saves each case's copy +
# image to the twitter-post-dryrun Volume so they can be pulled back with
# `modal volume get twitter-post-dryrun` and inspected before trusting the
# schedule.

DRY_RUN_CASES = {
    "1_verified_update": {},  # real live research, no forcing - exercises the "found a genuine dated update" path
    "2_evergreen_fallback": {
        "skip_research": True,
        "research_override": {
            "query": "(dry-run: forced empty research)",
            "weekday_hint": "evergreen test",
            "trend_hits": [], "scraped_sites": [],
            "limitations": ["dry-run case 2: research intentionally empty to force the evergreen-fallback path"],
        },
    },
    "3_thread": {"format": "thread"},
    "4_dark_logo_image": {"wants_image": True, "variant": "dark"},
    "5_light_logo_image": {"wants_image": True, "variant": "light"},
}


@app.function(image=image, secrets=secrets, timeout=900, volumes={DRYRUN_PATH: dryrun_volume})
def run_dry_case(case_name: str, force_case: dict):
    import pipeline
    out = pipeline.run(dry_run=True, force_case=force_case)

    case_dir = Path(DRYRUN_PATH) / case_name
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "post.json").write_text(
        json.dumps({"post": out["post"], "log_entry": out["log_entry"]}, indent=2, default=str),
        encoding="utf-8",
    )
    if out.get("_image_bytes"):
        (case_dir / "image.png").write_bytes(out["_image_bytes"])
    dryrun_volume.commit()
    return {"case": case_name, "status": out["status"], "has_image": bool(out.get("_image_bytes"))}


@app.local_entrypoint()
def dry_run_acceptance():
    results = []
    for case_name, force_case in DRY_RUN_CASES.items():
        print(f"--- running dry-run case: {case_name} ---")
        try:
            r = run_dry_case.remote(case_name, force_case)
            print(r)
            results.append(r)
        except Exception as e:  # noqa: BLE001
            print(f"CASE {case_name} FAILED: {e}")
            results.append({"case": case_name, "status": "error", "error": str(e)})
    print("\n=== summary ===")
    for r in results:
        print(r)
    print("\nPull results with: modal volume get twitter-post-dryrun / ./dryrun_output")
