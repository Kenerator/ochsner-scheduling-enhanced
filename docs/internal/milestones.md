# Milestones and optional UX refinement

Updated: not yet populated. No checkpoint tags created by bootstrap.

| Tag | Source commit | Purpose / timing | Relevant docs or demo |
| --- | --- | --- | --- |
| Pending | Pending | Scaffold only | Pending |

Create **annotated, immutable tags** for useful reviewed milestones—not each tool call. Suggested names: `poc/scaffold`, `poc/planned`, `poc/mvp`, `poc/ux-01-before`, `poc/ux-01-after`, `poc/submitted`. Use `poc/budget-baseline` only when the Operator directs capture of an actual agreed work-window baseline. Names are suggestions, not mandatory gates; tags do not confer release/publication authority.[^tagging]

After committing the intended source and verifying the tag is unused:

```sh
git tag -a poc/mvp -m "Working MVP checkpoint"
git rev-parse 'poc/mvp^{commit}'
# Only with push authority to the confirmed remote:
git push origin refs/tags/poc/mvp
```

Record the tag, resolved commit and purpose here in the next documentation commit; do not move a tag to include its own record. Use a new numbered tag for a later checkpoint. Never force-update tags or push all unrelated tags. See [Git setup](git-setup.md) for remote/commit cadence.

## Optional refinement

During Spec-Kit Tasks, consider an **optional post-MVP** task for a bounded UI/UX flow/polish pass. It cannot delay a working required slice, weaken acceptance, or substitute for core correctness. Follow the Operator's scope and timing decisions; agents must not silently stop or shrink work based on estimated elapsed time.

If selected, retain the working baseline with a pre-refinement tag, make the focused changes, test affected behavior, and tag the post-refinement result. Document the user benefit/trade-off in the existing decisions/next-steps files. Comparable synthetic-data screenshots or short clips may help the review; use the same scenario/view and disclose any separately permitted later work. If not selected, put a brief deferred item in next steps—no unfinished mandatory gate.

Link relevant tags from as-built docs and video notes instead of duplicating this table. Budget compliance and permission for supplemental work remain Operator decisions; never imply all versions were built within an agreed time window.

## Optional adversarial review

Consider one near-final or explicitly deferred task to populate the [review report](reviews/adversarial-review.md). Reuse a sufficient existing independent review. Preserve the source commit reviewed; commit sanitized findings and useful synthetic regressions. A suggested immutable tag is `poc/review-01`; record its source here and push that named tag only under existing destination/privacy authority. No raw consultation transcript, new mandatory gate or extra publication grant.

[^tagging]: [Git: tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging). Reviewed 2026-10-07. Use annotated tags for meaningful source checkpoints and explicitly push selected tags. Limit: A checkpoint is not release/publication authority or a budget-compliance claim.

## Recorded Enhanced checkpoints

- `poc/reference-baseline` →688039e: approved unchanged reference assets and credential guard.
- `poc/enhanced-guarded-ui-01` →7738727a9f2ca97fe999527df20515a016a7332f: reviewed implementation,91 tests, genuine model multi-turn synthetic booking and actual IAB confirmation. Private remote branch and peeled annotated tag verified at this SHA; fresh-clone qualification subsequently passed on both platforms. Tags are immutable.

Operator-dispatched +2h/+3h checkpoints use distinct immutable tags at actual capture time. +3h remains pending dispatch; no exact historical-time claim is made.

- `poc/checkpoint-2h-20261009` →acdd0b6152b9f73862ec835d9bba0fa441c293af: progress snapshot captured2026-10-09 00:42:11.471751 CDT,70.472s late relative to00:41:01. All subagents completed/no native writer, tree clean at capture and after push; remote main and peeled tag matched exactSHA then. Later resumed product changes do not move this tag.
- Post-checkpoint product delta 256a1b4: model redirect boundary fixed and92 tests/live application/both incrementally updated qualification clones passed.
