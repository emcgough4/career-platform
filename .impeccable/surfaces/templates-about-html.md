---
version: 1
slug: "templates-about-html"
primary_target: "templates/about.html"
related_targets: ["templates/resume.html","templates/portfolio.html","templates/contact.html","templates/project_detail.html","templates/base.html"]
---

# Surface brief: career site (all public pages)

Scope: Home (/about), Work (/portfolio), project detail, Resume, Contact, 404. Visitor mode: **Persuade/Experience**. The work is the argument.
Audience/job: a recruiter for a creative marketing role decides in seconds whether she can make content people stop for.
Proof: her own clips and stills, supplied by the owner. Until they arrive, media slots render only with PREVIEW_SLOTS=1. In production without media, those sections collapse and nothing placeholder ships.
Constraints: data-driven. Project media uses existing columns: `cover_image_url` (image or .mp4/.webm/.mov) and `project_url` (a TikTok, YouTube or Instagram link is embedded on the detail page). Fallback comment kept for ops. Owner complaints: too many fonts/sizes, repeated content.
Supersedes the 2026-10-06 cobalt/lower-third world, which the owner rejected as messy.

## Direction contract

THESIS: A reel, not a résumé. Her clips play in the page the way they play on a phone, in place of the category's text hero with a contact button.
OWN-WORLD: Deep plum ground (#2a1336; surfaces #3a1f48; secondary text tinted plum #c9b3d6). The owner chose it on 2026-10-07 over near-black ("black seems too dark to me, is there a more fun color"). Off-white type and no UI accent colour, so beyond the plum, colour comes only from her media. One family, Archivo: display 800 at 75% width, everything else normal width. Four sizes in total. Media in 9:16 with square corners. White pill-free buttons. No eyebrows, no decorative frames, no highlights.
STORY: She makes short-form video and social → watch it → email her.
FIRST VIEWPORT: Name in two lines at ~6rem, top-left. Headline as one plain line beneath. Two actions: Email me (white) and See the work (outline). Right: a tall 9:16 hero media slot (her photo or clip). Below the fold, a horizontal reel starts.
SIGNATURE INTERACTION: The reel is a horizontal scroll-snap row of 9:16 cards. Muted clips play on hover or focus; on touch the first tap previews and the second opens; it can be dragged, has prev/next buttons and arrow-key navigation, and each card opens its case study. Motion: the hero name tightens as you scroll (scroll-driven, with a static fallback); cards play and their media scales slightly on hover; the autoplaying hero clip has a pause/play control; reduced motion stops autoplay.
FORM: Pinned by the owner, not rolled (no seed key). On 2026-10-07 the owner was offered three directions: "Clean editorial", "Bold creative" and "Simple one-pager". They chose "Bold creative" with the note: "I want it to be engaging and interactive and really stand out for a creative marketing role." In an earlier answer the same day they had named the problems with the rejected build: "Too many fonts/sizes, Repeated content". PRODUCT.md Brand Commitments records both. Code-led, no image generation.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
