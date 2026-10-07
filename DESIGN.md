---
name: Eleanor McGough
description: A plum-lit screening room where her short-form video brings every colour except the cream that titles it.
colors:
  plum-ground: "#2a1336"
  plum-surface: "#3a1f48"
  cream: "#efe1cc"
  bone-white: "#f4f3ef"
  plum-mist: "#c9b3d6"
  hairline: "rgb(255 255 255 / 0.14)"
  phone-bezel: "#140a1a"
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
    backgroundColor: "{colors.cream}"
    textColor: "{colors.plum-ground}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "0 1.5rem"
    height: "48px"
  button-primary-hover:
    backgroundColor: "{colors.plum-ground}"
    textColor: "{colors.cream}"
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
  phone-frame:
    backgroundColor: "{colors.phone-bezel}"
    rounded: "{rounded.phone}"
  note:
    backgroundColor: "{colors.cream}"
    textColor: "{colors.plum-ground}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.45rem 0.75rem"
  topic-card:
    backgroundColor: "{colors.plum-surface}"
    textColor: "{colors.cream}"
    typography: "{typography.headline}"
    rounded: "{rounded.none}"
    padding: "1.25rem"
  topic-card-hover:
    backgroundColor: "{colors.cream}"
    textColor: "{colors.plum-ground}"
  media-slot-preview:
    backgroundColor: "{colors.plum-surface}"
    textColor: "{colors.plum-mist}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
---

# Design System: Eleanor McGough

## Overview

**Creative North Star: "The Screening Room"**

The house lights are dimmed to a deep plum and the screen is the brightest thing in the room. A plum ground, off-white reading text and one warm cream for titles, the main action and the notes beside the work mean that every other hue on the page comes from her clips and stills. Social video plays in phone frames, the way it plays on a phone; web screens and documents sit at their own shape. The page is built to be watched first and read second: a large name, one plain line, two actions, then a horizontal reel of work.

Two families, four sizes. Bodoni Moda at 500 weight sets the name and the lowercase, full-stopped section titles ("video.", "about.", "experience."), giving the polish of a printed programme; Archivo carries everything else, from body text to the cream metric notes. Structure comes from hairline rules, generous section spacing and square-cornered media. The level is the owner's "Polished middle": elegant serif titles, a topic index, phone frames and cream callout notes, and nothing beyond that. Density is low on the home page and calm on the resume, where a date column and hairline-ruled entries make a recruiter's skim fast.

Confirmed rejections: the earlier cobalt-and-chartreuse build, judged "messy" by the owner; a near-black ground, judged "too dark" (plum was chosen from five rendered grounds on 2026-10-07); too many fonts and sizes; repeated content on one page; clip-art stickers and tilted collage from the Canva reference.

**Key Characteristics:**
- Deep plum ground, bone-white text, cream for titles and the one main action; the work supplies every other colour.
- Two families (Bodoni Moda 500 for display and section titles, Archivo for the rest), four sizes.
- Social video in rounded phone frames, the only rounded objects; everything else square.
- Screens at 16:9 and documents at 4:5, shown at their own aspect; vertical 9:16 for clips and stills.
- Cream notes carry real numbers beside the work.
- Hairline rules and spacing for structure; plum-surface fill only on topic cards and empty media.

## Colors

A single-hue plum family under bone-white text, with one warm cream as the only interface accent. Bone white on plum ground is 15.2:1; plum mist on plum ground is 8.8:1; plum ground on cream (button and note text) is about 13:1.

### Primary
- **Plum Ground** (`plum-ground`): the page ground, theme colour and favicon field; the text colour on cream buttons, notes, hovered topic cards and selections.
- **Plum Surface** (`plum-surface`): the fill behind media while it loads or when a frame is empty, and the resting fill of topic cards. Never a panel around reading text.

### Secondary
- **Warm Cream** (`cream`): Bodoni display and section titles, the Contact email address, the primary button, the metric notes and the hovered topic card. Every use is either a title or a call to look at something.

### Neutral
- **Bone White** (`bone-white`): body text, card titles, outline button stroke, focus ring, active nav underline and the 1px rule under resume section titles.
- **Plum Mist** (`plum-mist`): secondary text only: leads, meta lines, dates, organisations, topic counts, inactive nav links, crumb, footer.
- **Hairline** (`hairline`, white at 14%): dividers between list entries, the footer top rule and the icon-button border.
- **Phone Bezel** (`phone-bezel`): the 0.4rem border of the phone frame and nothing else.

### Named Rules
**The Work Brings The Colour Rule.** Plum is the ground and cream is the only accent. Links, focus and secondary controls are bone-white on plum; there is no third UI hue. A colour on screen that is neither the plum family, bone white, cream nor her media is a defect.

## Typography

**Display Font:** Bodoni Moda (self-hosted variable, used at 500), with Didot, Bodoni 72 and Georgia fallbacks
**Body Font:** Archivo (self-hosted variable, normal width), with Arial Narrow and system-ui fallbacks

**Character:** A high-contrast Didone for the few words that name things, set lowercase with a full stop like a programme listing, against a plain, open grotesque for everything that is read or counted.

### Hierarchy
- **Display** (Bodoni Moda 500, clamp 3.25rem to 6rem, line-height 0.95, cream): the one page title: her name on home, "work.", "resume.", "Say hello." on inner pages.
- **Headline / Section** (Bodoni Moda 500, clamp 2.25rem to 3.5rem, line-height 1.05, cream): lowercase full-stopped section titles ("selected work.", "about.", "video.", "experience."), topic card names, the project title on a case study, and the Contact email address.
- **Title** (Archivo 700, body size, line-height 1.35): card titles, role names, case-study subsection labels, button labels. Same size as body; weight alone sets it apart.
- **Body** (Archivo 400, 1.0625rem, line-height 1.6): all reading text, leads capped at 40rem, resume text at 65ch. Inline notes on case studies use this size at 700.
- **Label / Meta** (Archivo 400, 0.875rem, tabular figures): dates, card meta, topic counts, tags, footer, and the cream notes on cards (at 700). Sentence case, no tracking, no uppercase.

### Named Rules
**The Two Families Rule.** Bodoni Moda at 500 is reserved for the display and section roles: the page title, section titles, topic names and the one display-size data point (the Contact email). Archivo carries everything else, including the cream metric notes, buttons and card titles. No third family, and no Bodoni below section size.

**The Four Sizes Rule.** The screen uses exactly four type sizes: display, section, body and meta (the `--size-*` tokens). Every new element maps onto one of them; emphasis comes from family, weight (400, 500, 700) or colour (cream, bone white, plum mist), never from a fifth size. Print stylesheet sizes (28pt display, 10.5pt body) are a separate medium and do not count.

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

Flat by default. Depth comes from the media itself, from tone (plum surface behind frames and on topic cards) and from a translucent plum-ground header (85% opacity, 12px backdrop blur). Two objects are lifted, both physical things placed on the page: the phone frame and the cream note. Both use soft, plum-black, downward-diffused shadows; neither is a hard offset. Overlays on media (play badge, hero pause control) use plum ground at 75%.

### Shadow Vocabulary
- **Phone lift** (`box-shadow: 0 0 0 1px rgb(255 255 255 / 0.12), 0 1.25rem 2.5rem -1.25rem rgb(8 2 12 / 0.7)`; on detail pages `0 1.5rem 3rem -1.5rem`): the phone frame only, with a faint white edge so the bezel reads against plum.
- **Note lift** (`box-shadow: 0 0.5rem 1.25rem -0.5rem rgb(8 2 12 / 0.6)`): the cream note overlapping a card's media. The inline note on a case study has no shadow.

### Named Rules
**The Lights-Down Rule.** Only phones and notes are lifted. Any other element that needs separation gets a hairline or spacing, not a shadow or a lighter panel.

## Shapes

Square everywhere except the phone: zero radius on buttons, icon buttons, notes, topic cards, media frames and slots. The phone frame (0.4rem phone-bezel border, 1.6rem radius) is the one rounded object and holds only social video, on cards and on case-study pages. Lines are 1px: hairline for dividers and icon-button borders, bone white for button outlines and resume section rules. Native silhouettes: 9:16 for clips, stills and the hero; 16:9 for web screens, fitted with bands of the screen's own edge colour; 4:5 for documents. Screens and documents are shown at their own aspect, never cropped to 9:16.

## Components

### Buttons
Blunt, high-contrast and square.
- **Shape:** square corners, 48px minimum height, 1.5rem side padding, Archivo 700 at body size.
- **Primary:** cream fill and border with plum-ground text, for the one main action on a page ("Email me", "Copy address", "View the project").
- **Outline:** transparent with a 1px bone-white stroke and bone-white text, for secondary actions.
- **Hover / Focus:** primary empties to a cream outline with cream text; outline fills bone white with plum text (0.2s, expo-out). Press nudges down 1px; focus is a 2px bone-white outline offset 4px.
- **Icon button:** 48px square, 1px hairline border that turns bone white on hover, inline SVG chevrons; disabled at 35% opacity. Used for reel previous and next.
- **Text link:** 700 weight, underlined, 44px tap height ("Full resume").

### Navigation
Name at left in Archivo 700; Work, Resume and Contact at right in plum mist at body size, 44px targets. Hover and the current page turn bone white; the current page also gets a 2px underline offset 0.5em. The header is sticky and translucent. On narrow screens the links drop to meta size and tighten their padding rather than collapsing into a menu.

### Work Card (signature)
Media, then an Archivo 700 title and a meta-size plum-mist description, with no container around the text. Social video sits in a phone frame; clips and stills in a square 9:16 frame on plum surface; screens and documents at their own aspect. Video covers carry a small square play badge bottom-left that fades on hover. A cream note, when the project has a metric, overlaps the media's right edge near the bottom (Archivo 700, meta size, tabular figures, one line with ellipsis). On hover or focus the muted clip plays and the media scales to 1.04 over 0.6s; on touch the first tap previews and the second opens the case study. Reduced motion stops playback.

### Note
A square cream tag with plum-ground text carrying a real number ("17.6K views · 550 likes"). On cards it is absolutely placed and lifted; on a case study it sits inline under the lead at body size with no shadow. Only recorded metrics appear; a project without one gets no note.

### Topic Card
A tall square plum-surface card holding the topic name in cream Bodoni at section size with a full stop, and a plum-mist piece count at the bottom. On hover or focus the card turns cream and its text plum ground (0.25s, expo-out). It links to the topic section on the same page.

### Reel
Work cards in a horizontal scroll-snap row with prev/next icon buttons beside the section title (shown only once script runs and only when the row overflows), arrow-key navigation when focused, and mouse drag. Touch and trackpads scroll natively.

### Hero Media
A tall 9:16 frame (4:5 on mobile) holding her photo or a muted looping clip, autoplaying unless reduced motion is set, with a 48px pause/play control bottom-right. The name above tightens its tracking and fades to 55% as the page scrolls (scroll-driven, static where unsupported or under reduced motion).

### Fact and Resume Rows
Hairline-ruled rows: content left, plum-mist tabular date right (About), or a 12rem plum-mist date column with title, plum-mist organisation, bullets capped at 65ch and a skills line (Resume). Resume section titles sit on a 1px bone-white rule.

### Empty Media Slot (preview-only)
A 1px dashed white (32%) frame on plum surface with a centred meta-size plum-mist caption. It renders only when `PREVIEW_SLOTS=1` is on and is hidden from assistive tech. Production never shows it: with no projects the reel, nav link and hero frame are omitted and the portfolio shows a plain empty-state sentence.

## Do's and Don'ts

### Do:
- **Do** let her media be the only source of colour beyond plum, bone white and cream.
- **Do** set page and section titles in cream Bodoni Moda 500, lowercase with a full stop where they name a section.
- **Do** map every text element onto one of the four sizes (display, section, body, meta) and vary family, weight or colour for emphasis.
- **Do** put social video in the phone frame and show screens (16:9) and documents (4:5) at their own aspect.
- **Do** give a topic of more than four items a reel and a smaller topic a full-width grid with one column per item.
- **Do** put only recorded numbers in cream notes.
- **Do** separate content with 1px hairlines and the section spacing token.
- **Do** keep tap targets at 44px or more and the 2px bone-white focus ring offset 4px.
- **Do** omit a section when its data is absent, rather than filling it with placeholders in production.

### Don't:
- **Don't** add a second accent colour, gradient, or tinted panel around reading text.
- **Don't** introduce a fifth type size or a third typeface, or use Bodoni Moda for body, buttons or notes.
- **Don't** show the same email, link set or role twice on one page.
- **Don't** add eyebrows or kickers above titles, uppercase tracked labels, clip-art stickers or tilted collage.
- **Don't** round anything but the phone frame, or lift anything but phones and notes.
- **Don't** crop a web screen or document into a 9:16 frame.
- **Don't** ship the dashed empty-slot frame outside `PREVIEW_SLOTS` mode.
