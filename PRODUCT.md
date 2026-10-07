# Product

<!-- impeccable:product-schema 1 -->

> Written 2026-10-06 without an interview round: the owner asked for the critique fixes to run end to end. Facts marked *(inferred)* come from the repository, the database content and the critique answers, and should be confirmed.

## Platform

web

## Users

- **Recruiters and hiring managers** for marketing, social media, video and content roles *(inferred)*. They arrive from LinkedIn, an application or an email signature, often on a phone, and decide in under a minute whether the candidate is worth a conversation.
- **The owner, Eleanor McGough**, who maintains content through SQL against SQLite rather than an admin UI.

## Product Purpose

A personal career site for Eleanor McGough, a Marketing and Information Systems & Business Analytics student at Loyola Marymount University (graduating May 2027). Success is a recruiter understanding who she is and what she makes, then reaching out by email or LinkedIn.

## Positioning

She already produces the medium recruiters are hiring for: short-form vertical video, social accounts for The Loyolan, and SEO content for XDR Radiology. The site should be evidence of that eye, not only a description of it.

## Operating Context

- FastAPI + Jinja templates, SQLAlchemy models, SQLite as the source of truth (`data/career_platform.db`, never committed).
- Deployed on an Azure VM; `DATABASE_URL` comes from `.env`. Ops checks grep the rendered HTML for the fallback string "Showing the latest saved profile snapshot" and expect a count of 0.
- When the database is unavailable, pages render `data/public_profile_snapshot.json`, a deliberately placeholder snapshot that tests depend on.
- Pages: About (`/`, `/about`), Resume, Portfolio + project detail, Contact.

## Capabilities and Constraints

- No contact form or server-side mail; contact is mailto and LinkedIn.
- Content is data-driven; templates must not hard-code biography facts.
- Project records support cover images, tags and case-study sections, but none are published yet.
- Undecided: whether to publish a downloadable PDF resume; whether to add a headshot (`photo_url`).

## Brand Commitments

- Tone requested by the owner: creative first, but aesthetic and polished. Not chaotic.
- 2026-10-07, after the first redesign was judged "not a clean work and is messy": the owner chose the **Bold creative** direction, where her work leads (large photo and video stills, big confident type, colour from her content rather than UI decoration), and asked that it be "engaging and interactive and really stand out for a creative marketing role".
- 2026-10-07: the owner found near-black "too dark" and chose a deep **plum** ground from five rendered options (plum, teal, oxblood, forest, indigo).
- Specific complaints to never repeat: too many fonts and sizes; repeated content (the same email, links or roles shown twice on one page).

## Evidence on Hand

- Real profile, 2 experiences, 2 LMU degrees (GPA 3.84, Dean's List, Ignatius Grant, Xavier Award), 12 skills in 3 categories.
- **Absent, must not be fabricated:** work samples, video stills, metrics (views, follower growth), testimonials, availability dates, response-time promises.

## Product Principles

1. Show the work before describing it; when work is missing, say so plainly rather than promise it.
2. A recruiter's 30-second skim must surface name, school, graduation date, current roles and how to reach her.
3. Every fact on the page comes from the database; the design adapts to what exists.
4. Polished enough to read as professional, specific enough to read as her.

## Accessibility & Inclusion

WCAG 2.2 AA: contrast, visible focus, keyboard navigation, 44px touch targets, reduced-motion support *(inferred standard)*.
