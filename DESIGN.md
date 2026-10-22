---
name: Eleanor McGough
description: A warm espresso page in dark brown ink, where her short-form video brings every colour except the espresso that titles it.
colors:
  espresso-ground: "#f3eadb"
  espresso-surface: "#e9dcc7"
  espresso: "#2b1d14"
  ink: "#2b1d14"
  umber: "#6b5444"
  hairline: "rgb(43 29 20 / 0.16)"
  phone-bezel: "#1e140d"
typography:
  display:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, Georgia, serif"
    fontSize: "clamp(3.25rem, 9.5vw, 6rem)"
    fontWeight: 500
    lineHeight: 0.95
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, Georgia, serif"
    fontSize: "clamp(2.25rem, 5vw, 3.5rem)"
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: "-0.015em"
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
  phone: "1.6rem"
spacing:
  gutter: "clamp(1.25rem, 4vw, 3rem)"
  section: "clamp(4rem, 10vw, 8rem)"
  container: "80rem"
components:
  button-primary:
    backgroundColor: "{colors.espresso}"
    textColor: "{colors.cream-ground}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "0 1.5rem"
    height: "48px"
  button-primary-hover:
    backgroundColor: "{colors.cream-ground}"
    textColor: "{colors.espresso}"
  button-outline:
    backgroundColor: "{colors.cream-ground}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "0 1.5rem"
    height: "48px"
  button-outline-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.cream-ground}"
  icon-button:
    backgroundColor: "{colors.cream-ground}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    size: "48px"
  nav-link:
    textColor: "{colors.umber}"
    typography: "{typography.body}"
    padding: "0 0.75rem"
    height: "44px"
  nav-link-active:
    textColor: "{colors.ink}"
  work-card-media:
    backgroundColor: "{colors.cream-surface}"
    rounded: "{rounded.none}"
  phone-frame:
    backgroundColor: "{colors.phone-bezel}"
    rounded: "{rounded.phone}"
  note:
    backgroundColor: "{colors.espresso}"
    textColor: "{colors.cream-ground}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.45rem 0.75rem"
  topic-card:
    backgroundColor: "{colors.cream-surface}"
    textColor: "{colors.espresso}"
    typography: "{typography.headline}"
    rounded: "{rounded.none}"
    padding: "1.25rem"
  topic-card-hover:
    backgroundColor: "{colors.espresso}"
    textColor: "{colors.cream-ground}"
  media-slot-preview:
    backgroundColor: "{colors.cream-surface}"
    textColor: "{colors.umber}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
---

# Design System: Eleanor McGough

## Overview

**Creative North Star: "The Printed Programme"**

A warm cream page printed in dark brown ink, like a programme handed out before a screening: the paper stays quiet so her clips are the brightest things on it. A cream ground, dark brown reading text and the same espresso for titles, the main action and the notes beside the work mean that every other hue on the page comes from her clips and stills. Social video plays in phone frames, the way it plays on a phone; web screens and documents sit at their own shape. The page is built to be watched first and read second: a large name, one plain line, two actions, then a horizontal reel of work.

Two families, four sizes. Bodoni Moda at 500 weight sets the name and the lowercase, full-stopped section titles ("video.", "about.", "experience."), giving the polish of a printed programme; Archivo carries everything else, from body text to the espresso metric notes. Structure comes from hairline rules, generous section spacing and square-cornered media. The level is the owner's "Polished middle": elegant serif titles, a topic index, phone frames and espresso callout notes, and nothing beyond that. Density is low on the home page and calm on the resume, where a date column and hairline-ruled entries make a recruiter's skim fast.

Confirmed rejections: the earlier cobalt-and-chartreuse build, judged "messy" by the owner; a near-black ground, judged "too dark" (plum was chosen from five rendered grounds on 2026-10-07); the deep plum ground itself, judged "too much" on 2026-10-22 and replaced by cream with dark brown text at the owner's request; too many fonts and sizes; repeated content on one page; clip-art stickers and tilted collage from the Canva reference.

**Key Characteristics:**
- Deep cream ground, ink text, espresso for titles and the one main action; the work supplies every other colour.
- Two families (Bodoni Moda 500 for display and section titles, Archivo for the rest), four sizes.
- Social video in rounded phone frames, the only rounded objects; everything else square.
- Screens at 16:9 and documents at 4:5, shown at their own aspect; vertical 9:16 for clips and stills.
- Espresso notes carry real numbers beside the work.
- Hairline rules and spacing for structure; cream-surface fill only on topic cards and empty media.

## Colors

A warm cream paper family under dark brown ink. Espresso, the ink at full strength, is the only interface accent: it fills the primary button, the notes and hovered topic cards. Ink and espresso on cream ground are 13.7:1; umber on cream ground is 5.9:1 and on cream surface 5.2:1; cream ground on espresso (button and note text) is 13.7:1.

### Primary
- **Cream Ground** (`cream-ground`): the page ground, theme colour and favicon field; the text colour on espresso buttons, notes, hovered topic cards and selections.
- **Cream Surface** (`cream-surface`): the fill behind media while it loads or when a frame is empty, and the resting fill of topic cards. Never a panel around reading text.

### Secondary
- **Espresso** (`espresso`): Bodoni display and section titles, the Contact email address, the primary button, the metric notes and the hovered topic card. Every use is either a title or a call to look at something.

### Neutral
- **Ink** (`ink`): body text, card titles, outline button stroke, focus ring, active nav underline and the 1px rule under resume section titles.
- **Umber** (`umber`): secondary text only: leads, meta lines, dates, organisations, topic counts, inactive nav links, crumb, footer.
- **Hairline** (`hairline`, dark brown at 16%): dividers between list entries, the footer top rule and the icon-button border.
- **Phone Bezel** (`phone-bezel`): the 0.4rem border of the phone frame and nothing else.

### Named Rules
**The Work Brings The Colour Rule.** Cream is the ground and espresso is the only accent. Links, focus and secondary controls are ink on cream; there is no third UI hue. A colour on screen that is neither the cream family, the browns, nor her media is a defect.

## Typography

**Display Font:** Bodoni Moda (self-hosted variable, used at 500), with Didot, Bodoni 72 and Georgia fallbacks
**Body Font:** Archivo (self-hosted variable, normal width), with Arial Narrow and system-ui fallbacks

**Character:** A high-contrast Didone for the few words that name things, set lowercase with a full stop like a programme listing, against a plain, open grotesque for everything that is read or counted.

### Hierarchy
- **Display** (Bodoni Moda 500, clamp 3.25rem to 6rem, line-height 0.95, espresso): the one page title: her name on home, "work.", "resume.", "Say hello." on inner pages.
- **Headline / Section** (Bodoni Moda 500, clamp 2.25rem to 3.5rem, line-height 1.05, espresso): lowercase full-stopped section titles ("selected work.", "about.", "video.", "experience."), topic card names, the project title on a case study, and the Contact email address.
- **Title** (Archivo 700, body size, line-height 1.35): card titles, role names, case-study subsection labels, button labels. Same size as body; weight alone sets it apart.
- **Body** (Archivo 400, 1.0625rem, line-height 1.6): all reading text, leads capped at 40rem, resume text at 65ch. Inline notes on case studies use this size at 700.
- **Label / Meta** (Archivo 400, 0.875rem, tabular figures): dates, card meta, topic counts, tags, footer, and the espresso notes on cards (at 700). Sentence case, no tracking, no uppercase.

### Named Rules
**The Two Families Rule.** Bodoni Moda at 500 is reserved for the display and section roles: the page title, section titles, topic names and the one display-size data point (the Contact email). Archivo carries everything else, including the espresso metric notes, buttons and card titles. No third family, and no Bodoni below section size.

**The Four Sizes Rule.** The screen uses exactly four type sizes: display, section, body and meta (the `--size-*` tokens). Every new element maps onto one of them; emphasis comes from family, weight (400, 500, 700) or colour (espresso, ink, umber), never from a fifth size. Print stylesheet sizes (28pt display, 10.5pt body) are a separate medium and do not count.

## Layout

A single centred container of up to 80rem with a fluid gutter (clamp 1.25rem to 3rem). Sections are separated by one rhythm token (clamp 4rem to 8rem); page heads get top padding of clamp 3rem to 6rem.

- **Home hero:** two columns (1.4fr copy, 1fr media), bottom-aligned, the name top-left in two lines and a tall 9:16 media frame on the right capped at 78vh. Below 760px it stacks and the frame becomes 4:5 so the name stays in the first viewport.
- **Reel:** a horizontal scroll-snap row that bleeds to the viewport edge while its first card aligns with the container; cards are clamp 14rem to 19rem wide with 1rem gaps.
- **Topic index (Work page):** an auto-fit grid of tall cards (minimum 11rem wide, clamp 7rem to 10rem tall) that jump to topic sections; below 480px each becomes a single row with the count beside the name.
- **Topic sections:** a topic with more than four items renders as a reel with prev/next controls; four or fewer render as a full-width grid with one column per item (`--cols` set to the item count), so no row is left ragged. Below 480px the grid is one column.
- **About and resume rows:** a narrow label column (1fr against 2fr on About; a fixed 12rem date column on the resume) that collapses to one column below 760px.
- **Case study:** a sticky 9:16 media column (16rem to 26rem) beside a body capped at 42rem. Image covers (screens and documents) widen to a 1.2fr/1fr grid above 760px and are not sticky. With no media it becomes a single column.

### Named Rules
**The Say It Once Rule.** Each fact appears once per page: one email, one set of social links, one listing of a role. The header carries no contact button, the footer carries only "Back to top", and the home About block lists current roles and school as one-line facts with a link to the full resume rather than restating it.

## Elevation & Depth

Flat by default. Depth comes from the media itself, from tone (cream surface behind frames and on topic cards) and from a translucent cream-ground header (85% opacity, 12px backdrop blur). Two objects are lifted, both physical things placed on the page: the phone frame and the espresso note. Both use soft, brown, downward-diffused shadows; neither is a hard offset. Overlays on media (play badge, hero pause control) use espresso at 75% with cream icons.

### Shadow Vocabulary
- **Phone lift** (`box-shadow: 0 1.25rem 2.5rem -1.25rem rgb(43 29 20 / 0.4)`; on detail pages `0 1.5rem 3rem -1.5rem`): the phone frame only. The dark bezel reads against cream without an edge line.
- **Note lift** (`box-shadow: 0 0.5rem 1.25rem -0.5rem rgb(43 29 20 / 0.35)`): the espresso note overlapping a card's media. The inline note on a case study has no shadow.

### Named Rules
**The Flat Paper Rule.** Only phones and notes are lifted. Any other element that needs separation gets a hairline or spacing, not a shadow or a lighter panel.

## Shapes

Square everywhere except the phone: zero radius on buttons, icon buttons, notes, topic cards, media frames and slots. The phone frame (0.4rem phone-bezel border, 1.6rem radius) is the one rounded object and holds only social video, on cards and on case-study pages. Lines are 1px: hairline for dividers and icon-button borders, ink for button outlines and resume section rules. Native silhouettes: 9:16 for clips, stills and the hero; 16:9 for web screens, fitted with bands of the screen's own edge colour; 4:5 for documents. Screens and documents are shown at their own aspect, never cropped to 9:16.

## Components

### Buttons
Blunt, high-contrast and square.
- **Shape:** square corners, 48px minimum height, 1.5rem side padding, Archivo 700 at body size.
- **Primary:** espresso fill and border with cream-ground text, for the one main action on a page ("Email me", "Copy address", "View the project").
- **Outline:** transparent with a 1px ink stroke and ink text, for secondary actions.
- **Hover / Focus:** primary empties to an espresso outline with espresso text; outline fills ink with cream text (0.2s, expo-out). Press nudges down 1px; focus is a 2px ink outline offset 4px.
- **Icon button:** 48px square, 1px hairline border that turns ink on hover, inline SVG chevrons; disabled at 35% opacity. Used for reel previous and next.
- **Text link:** 700 weight, underlined, 44px tap height ("Full resume").

### Navigation
Name at left in Archivo 700; Work, Resume and Contact at right in umber at body size, 44px targets. Hover and the current page turn ink; the current page also gets a 2px underline offset 0.5em. The header is sticky and translucent. On narrow screens the links drop to meta size and tighten their padding rather than collapsing into a menu.

### Work Card (signature)
Media, then an Archivo 700 title and a meta-size umber description, with no container around the text. Social video sits in a phone frame; clips and stills in a square 9:16 frame on cream surface; screens and documents at their own aspect. Video covers carry a small square play badge bottom-left that fades on hover. A espresso note, when the project has a metric, overlaps the media's right edge near the bottom (Archivo 700, meta size, tabular figures, one line with ellipsis). On hover or focus the muted clip plays and the media scales to 1.04 over 0.6s; on touch the first tap previews and the second opens the case study. Reduced motion stops playback.

### Note
A square espresso tag with cream-ground text carrying a real number ("17.6K views · 550 likes"). On cards it is absolutely placed and lifted; on a case study it sits inline under the lead at body size with no shadow. Only recorded metrics appear; a project without one gets no note.

### Topic Card
A tall square cream-surface card holding the topic name in espresso Bodoni at section size with a full stop, and a umber piece count at the bottom. On hover or focus the card turns espresso and its text cream ground (0.25s, expo-out). It links to the topic section on the same page.

### Reel
Work cards in a horizontal scroll-snap row with prev/next icon buttons beside the section title (shown only once script runs and only when the row overflows), arrow-key navigation when focused, and mouse drag. Touch and trackpads scroll natively.

### Hero Media
A tall 9:16 frame (4:5 on mobile) holding her photo or a muted looping clip, autoplaying unless reduced motion is set, with a 48px pause/play control bottom-right. The name above tightens its tracking and fades to 55% as the page scrolls (scroll-driven, static where unsupported or under reduced motion).

### Fact and Resume Rows
Hairline-ruled rows: content left, umber tabular date right (About), or a 12rem umber date column with title, umber organisation, bullets capped at 65ch and a skills line (Resume). Resume section titles sit on a 1px ink rule.

### Empty Media Slot (preview-only)
A 1px dashed dark brown (30%) frame on cream surface with a centred meta-size umber caption. It renders only when `PREVIEW_SLOTS=1` is on and is hidden from assistive tech. Production never shows it: with no projects the reel, nav link and hero frame are omitted and the portfolio shows a plain empty-state sentence.

## Do's and Don'ts

### Do:
- **Do** let her media be the only source of colour beyond cream, ink and espresso.
- **Do** set page and section titles in espresso Bodoni Moda 500, lowercase with a full stop where they name a section.
- **Do** map every text element onto one of the four sizes (display, section, body, meta) and vary family, weight or colour for emphasis.
- **Do** put social video in the phone frame and show screens (16:9) and documents (4:5) at their own aspect.
- **Do** give a topic of more than four items a reel and a smaller topic a full-width grid with one column per item.
- **Do** put only recorded numbers in espresso notes.
- **Do** separate content with 1px hairlines and the section spacing token.
- **Do** keep tap targets at 44px or more and the 2px ink focus ring offset 4px.
- **Do** omit a section when its data is absent, rather than filling it with placeholders in production.

### Don't:
- **Don't** add a second accent colour, gradient, or tinted panel around reading text.
- **Don't** introduce a fifth type size or a third typeface, or use Bodoni Moda for body, buttons or notes.
- **Don't** show the same email, link set or role twice on one page.
- **Don't** add eyebrows or kickers above titles, uppercase tracked labels, clip-art stickers or tilted collage.
- **Don't** round anything but the phone frame, or lift anything but phones and notes.
- **Don't** crop a web screen or document into a 9:16 frame.
- **Don't** ship the dashed empty-slot frame outside `PREVIEW_SLOTS` mode.
