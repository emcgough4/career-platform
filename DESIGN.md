---
name: Eleanor McGough
description: A plum-lit screening room where her short-form video brings every other colour.
colors:
  plum-ground: "#2a1336"
  plum-surface: "#3a1f48"
  bone-white: "#f4f3ef"
  plum-mist: "#c9b3d6"
  hairline: "rgb(255 255 255 / 0.14)"
typography:
  display:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(3.25rem, 9.5vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.02em"
    fontVariation: "'wdth' 75"
  headline:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 5vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontVariation: "'wdth' 75"
  title:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.35
  body:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "tnum"
rounded:
  none: "0px"
spacing:
  gutter: "clamp(1.25rem, 4vw, 3rem)"
  section: "clamp(4rem, 10vw, 8rem)"
  container: "80rem"
components:
  button-primary:
    backgroundColor: "{colors.bone-white}"
    textColor: "{colors.plum-ground}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "0 1.5rem"
    height: "48px"
  button-primary-hover:
    backgroundColor: "{colors.plum-ground}"
    textColor: "{colors.bone-white}"
  button-outline:
    backgroundColor: "{colors.plum-ground}"
    textColor: "{colors.bone-white}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "0 1.5rem"
    height: "48px"
  button-outline-hover:
    backgroundColor: "{colors.bone-white}"
    textColor: "{colors.plum-ground}"
  icon-button:
    backgroundColor: "{colors.plum-ground}"
    textColor: "{colors.bone-white}"
    rounded: "{rounded.none}"
    size: "48px"
  nav-link:
    textColor: "{colors.plum-mist}"
    typography: "{typography.body}"
    padding: "0 0.75rem"
    height: "44px"
  nav-link-active:
    textColor: "{colors.bone-white}"
  work-card-media:
    backgroundColor: "{colors.plum-surface}"
    rounded: "{rounded.none}"
  media-slot-preview:
    backgroundColor: "{colors.plum-surface}"
    textColor: "{colors.plum-mist}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
---

# Design System: Eleanor McGough

## Overview

**Creative North Star: "The Screening Room"**

The house lights are dimmed to a deep plum and the screen is the brightest thing in the room. One plum ground, off-white type and no interface accent colour mean that, beyond the plum, every hue on the page comes from her clips and stills. Media sits in tall vertical frames, the way her work plays on a phone, and the page is built to be watched first and read second: a large name, one plain line, two actions, then a horizontal reel of work.

One family carries everything. Archivo at 800 weight and 75% width makes the condensed, poster-like display voice; the same family at normal width carries all reading text. Only four type sizes exist on screen. Structure comes from hairline rules, generous section spacing and square-cornered media, never from boxes, tints or decoration. Density is low on the home page and calm on the resume, where a date column and hairline-ruled entries make a recruiter's skim fast.

Confirmed rejections: the earlier cobalt-and-chartreuse build, judged "messy" by the owner; a near-black ground, judged "too dark" (the owner chose plum from five rendered grounds on 2026-10-07); too many fonts and sizes; repeated content on one page.

**Key Characteristics:**
- Deep plum ground, off-white type, zero UI accent colour; the work supplies every other colour.
- One family (Archivo variable), two widths, four sizes.
- 9:16 media with square corners, shown in place and playing on hover or focus.
- Hairline rules and spacing for structure; no cards, shadows or rounded corners.
- Two button states only: solid bone-white and bone-white outline.

## Colors

A single-hue plum family (ground, surface and a pale tinted secondary) under bone-white type; every other colour is reserved for the media. Bone white on plum ground is 15.2:1; plum mist on plum ground is 8.8:1.

### Primary
- **Plum Ground** (`plum-ground`): the page ground, theme colour, favicon field and the text colour on solid buttons and selections.
- **Plum Surface** (`plum-surface`): the surface behind media frames while they load or when a frame is empty; never used as a card or panel fill around text.
- **Plum Mist** (`plum-mist`): secondary text only: lead paragraphs, meta lines, dates, organisations, inactive nav links, footer.

### Neutral
- **Bone White** (`bone-white`): all primary text, solid button fill, outline button stroke, focus ring, active nav underline, and the heavier rule under resume section headings.
- **Hairline** (`hairline`, white at 14%): dividers between list entries, the footer top rule and the icon-button border.

### Named Rules
**The Work Brings The Colour Rule.** Plum is the ground, not an accent. Links, focus, buttons and highlights are all bone-white on plum ground; there is no second UI hue. A colour on screen that is neither the plum family nor her media is a defect.

## Typography

**Display Font:** Archivo at 800 weight, 75% width (variable `wdth`), with Arial Narrow fallback
**Body Font:** Archivo at normal width, with system-ui fallback

**Character:** One family in two voices: a condensed, heavy poster headline against a plain, open grotesque for reading. The contrast comes from width and weight, never from a second family.

### Hierarchy
- **Display** (800, 75% width, clamp 3.25rem to 6rem, line-height 0.92): the single page title: her name on the home page, and "Work", "Resume", "Say hello." on inner pages. One per page.
- **Headline** (800, 75% width, clamp 2.25rem to 3.5rem, line-height 1): section headings ("Selected work", "About", "Experience"), the project title on a case study, and the two large display-voice data points: a case-study metric and the email address on Contact.
- **Title** (700, body size, line-height 1.35): role names, card titles, case-study subsection labels, button labels. Same size as body; weight alone sets it apart.
- **Body** (400, 1.0625rem, line-height 1.6): all reading text, capped at about 40rem for leads and 65ch for resume bullets and details.
- **Label** (400, 0.875rem, tabular figures): dates, locations, card meta, skill categories, tags, footer, empty-slot captions. Sentence case, no tracking, no uppercase.

### Named Rules
**The Four Sizes Rule.** The screen uses exactly four type sizes: display, section, body and meta (the `--size-*` tokens). Every new element maps onto one of them; emphasis comes from weight (400, 700, 800) or colour (bone-white versus plum mist), never from a fifth size. Print stylesheet sizes (28pt display, 10.5pt body) are a separate medium and do not count.

**The One Family Rule.** Archivo is the only typeface. The condensed 75% width belongs to display and headline roles only; everything else is normal width.

## Layout

A single centred container of up to 80rem with a fluid gutter (clamp 1.25rem to 3rem) on each side. Sections are separated by one generous rhythm token (clamp 4rem to 8rem); page heads get their own top padding of clamp 3rem to 6rem.

- **Home hero:** two columns (about 1.4fr copy, 1fr media), bottom-aligned, with the name top-left in two lines and a tall 9:16 media frame on the right capped at 78vh. Below 760px it stacks and the hero frame becomes 4:5 so the name stays in the first viewport.
- **Reel:** a horizontal scroll-snap row that bleeds to the viewport edge while its first card aligns with the container; cards are clamp 14rem to 19rem wide with 1rem gaps.
- **Portfolio:** an auto-fill grid of the same cards, minimum 14rem.
- **About and resume rows:** a narrow label column (1fr against 2fr on About; a fixed 12rem date column on the resume) that collapses to one column below 760px.
- **Case study:** a sticky 9:16 media column (16rem to 26rem) beside a body capped at 42rem; with no media it becomes a single column.

### Named Rules
**The Say It Once Rule.** Each fact appears once per page: one email, one set of social links, one listing of a role. The header carries no contact button, the footer carries only "Back to top", and the home About block lists current roles and school as one-line facts with a link to the full resume rather than restating it.

## Elevation & Depth

Flat. There are no shadows anywhere. Depth comes only from the media itself and from tone: plum surface behind frames, and a translucent plum-ground header (85% opacity with a 12px backdrop blur) that lets content pass beneath it while sticky. Overlays on media (the play badge on video cards, the hero pause control) use plum ground at 75% so they read against any frame.

### Named Rules
**The Lights-Down Rule.** Nothing is lifted. If an element needs separation, use a hairline or spacing, not a shadow or a lighter panel.

## Shapes

Square everywhere: zero radius on buttons, icon buttons, media frames and slots. Lines are 1px: hairline for dividers and icon-button borders, bone-white for button outlines and resume section rules. Media is framed by its own edge, with no border, mat or decorative frame. Vertical 9:16 is the native silhouette of work, hero and case-study media.

## Components

### Buttons
Blunt, high-contrast and square.
- **Shape:** square corners (0), 48px minimum height, 1.5rem side padding, 700 weight at body size.
- **Primary:** bone-white fill with plum-ground text. Used for the one main action on a page ("Email me", "Copy address", "View the project").
- **Outline:** transparent with a 1px bone-white stroke and bone-white text, for the secondary action.
- **Hover / Focus:** the two variants swap fills on hover (0.2s, expo-out ease); press nudges down 1px; focus is a 2px bone-white outline offset 4px.
- **Icon button:** 48px square, 1px hairline border that turns bone-white on hover, inline SVG chevrons; disabled drops to 35% opacity. Used for reel previous and next.
- **Text link:** 700 weight, underlined, 44px tap height ("Full resume").

### Navigation
Name at left in 700 weight; Work, Resume and Contact at right in plum mist at body size, 44px tall targets. Hover and the current page turn bone-white; the current page also gets a 2px underline offset 0.5em. The header is sticky and translucent. "Work" is hidden when no projects are published. On narrow screens the links tighten their padding rather than collapsing into a menu.

### Work Card (signature)
A 9:16 square-cornered media frame on plum surface, then a 700-weight title and a label-size meta line (metric or year) in plum mist, with no container around the text. Video covers carry a small square play badge bottom-left that fades away on hover. On hover or focus the muted clip plays and the media scales to 1.04 over 0.6s; on touch the first tap previews and the second opens the case study. Reduced motion stops playback.

### Reel (signature)
The work cards in a horizontal scroll-snap row with prev/next icon buttons beside the section heading (shown only once script runs), arrow-key navigation when focused, and mouse drag. Touch and trackpads scroll natively.

### Hero Media
A tall 9:16 frame (4:5 on mobile) holding her photo or a muted looping clip. A clip autoplays unless reduced motion is set, with a 48px pause/play control bottom-right. The name above tightens its tracking and fades to 55% as the page scrolls (scroll-driven, static where unsupported or under reduced motion).

### Fact and Resume Rows
Hairline-ruled rows: content on the left, a plum-mist tabular-figure date on the right (About), or a 12rem plum-mist date column with title, plum-mist organisation, bullets capped at 65ch and a plum-mist label line of skills (Resume). Resume section headings sit on a 1px bone-white rule.

### Empty Media Slot (preview-only)
A 1px dashed white (32%) frame on plum surface with a centred label-size plum-mist caption ("Hero, photo of you or your best clip", "Work 1, vertical clip or still"), with placeholder card title and meta in plum mist. It renders **only** when the `PREVIEW_SLOTS=1` setting is on, so the owner can see where media will go, and is hidden from assistive tech. Production never shows it: with no projects the reel, nav link and hero frame are omitted and the portfolio shows a plain empty-state sentence instead.

## Do's and Don'ts

### Do:
- **Do** let her media be the only source of colour; keep UI in plum ground, bone white, plum mist and hairline.
- **Do** map every text element onto one of the four sizes (display, section, body, meta) and vary weight or colour for emphasis.
- **Do** use Archivo 800 at 75% width only for the page title, section headings and the rare headline-size data point.
- **Do** frame media in 9:16 with square corners on plum surface, playing muted in place.
- **Do** separate content with 1px hairlines and the section spacing token.
- **Do** keep tap targets at 44px or more and the 2px bone-white focus ring offset 4px.
- **Do** omit a section when its data is absent, rather than filling it with placeholders in production.

### Don't:
- **Don't** add an accent colour, gradient, tinted panel or highlight.
- **Don't** introduce a fifth type size or a second typeface.
- **Don't** show the same email, link set or role twice on one page.
- **Don't** add eyebrows or kickers above headings, uppercase tracked labels, or decorative frames around media.
- **Don't** round corners, add shadows, or wrap text in cards.
- **Don't** ship the dashed empty-slot frame outside `PREVIEW_SLOTS` mode.
