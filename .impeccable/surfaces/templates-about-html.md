---
version: 1
slug: "templates-about-html"
primary_target: "templates/about.html"
related_targets: ["templates/resume.html","templates/portfolio.html","templates/contact.html","templates/project_detail.html","templates/base.html"]
---

# Surface brief: career site (all public pages)

Scope: About, Resume, Portfolio, project detail, Contact, 404. Visitor mode: **Persuade** (recruiter decides whether to reach out).
Audience/job: recruiter skimming on laptop or phone; needs name, school, grad date, current roles, contact. Proof: real roles and degrees from the DB; no work samples yet.
Constraints: data-driven templates; fallback string kept as an HTML comment for ops greps; tests unchanged.
Unresolved: media (headshot, video stills), metrics, availability line — owner to supply.

## Direction contract

THESIS: The site is set like her own video work — broadcast lower-thirds and a 9:16 frame — instead of the category's cream page with an eyebrow over a big name.
OWN-WORLD: Cobalt field (#1d3fd8) owns the hero and closing bands; chartreuse (#d8f45a) is the lower-third strap with near-black ink; cool white page; Archivo variable — condensed 900 for headlines, set in mixed case (all-caps flattens “McGough” and the strap-on-cobalt contrast already carries the broadcast voice), normal width for text. No pills, no cards, no eyebrows. Rules: a 2px ink rule opens each section, light grey hairlines separate items within it (two weights so section starts read at a skim).
STORY: Visitor sees who she is and what she's doing now, believes she makes content with an eye, then emails or opens the resume.
FIRST VIEWPORT: Full-bleed cobalt band. Left: name in condensed 900 at ~6rem, chartreuse strap with headline beneath, the one-sentence summary, two actions (Email / Resume). Right: a 9:16 viewfinder (thirds grid, action-safe brackets, centre cross) holding her photo, or her current roles as lower-thirds set in the lower third, inside the action-safe brackets; without a photo the frame drops below 760px because “Right now” follows directly.
FORM: Pinned by the owner, not rolled (no concept-seed run, so no seed key). Owner’s words: “What do you think is best for me? I want to focus on creativity but also be aesthetic.” They then accepted the editorial-creator recommendation with “ok, let me know when it’s done”. Code-led, no image generation.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
