---
name: Eleanor McGough
description: A career site set like her own video work, with broadcast lower-thirds on a cobalt field and a 9:16 viewfinder.
colors:
  field: "#1d3fd8"
  field-deep: "#142d9f"
  strap: "#d8f45a"
  ink: "#0f1220"
  ink-soft: "#454c5e"
  paper: "#fbfbfd"
  line: "#dcdfe8"
  on-field: "#ffffff"
  on-field-soft: "#dbe2ff"
typography:
  display:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(3.25rem, 9vw, 6rem)"
    fontWeight: 900
    lineHeight: 0.92
    letterSpacing: "-0.015em"
    fontVariation: "'wdth' 62"
  headline:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 3.2vw, 2.4rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontVariation: "'wdth' 70"
  title:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(1.3rem, 2.2vw, 1.6rem)"
    fontWeight: 800
    lineHeight: 1.15
    fontVariation: "'wdth' 80"
  strap:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(1.05rem, 1.8vw, 1.3rem)"
    fontWeight: 700
    lineHeight: 1.55
    fontVariation: "'wdth' 85"
  body:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    fontVariation: "'wdth' 100"
  label:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.6
    fontFeature: "'tnum' 1"
    fontVariation: "'wdth' 85"
rounded:
  none: "0"
spacing:
  gutter: "clamp(1rem, 4vw, 2.5rem)"
  band: "clamp(3.5rem, 9vw, 7rem)"
  container: "72rem"
components:
  button-strap:
    backgroundColor: "{colors.strap}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0 1.35rem"
    height: "48px"
  button-strap-hover:
    backgroundColor: "{colors.on-field}"
    textColor: "{colors.ink}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.on-field}"
    rounded: "{rounded.none}"
    padding: "0 1.35rem"
    height: "48px"
  button-ghost-hover:
    backgroundColor: "{colors.on-field}"
    textColor: "{colors.field}"
  button-solid:
    backgroundColor: "{colors.field}"
    textColor: "{colors.on-field}"
    rounded: "{rounded.none}"
    padding: "0 1.35rem"
    height: "48px"
  button-solid-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-field}"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.field}"
    rounded: "{rounded.none}"
    padding: "0 1.35rem"
    height: "48px"
  button-outline-hover:
    backgroundColor: "{colors.field}"
    textColor: "{colors.on-field}"
  strap:
    backgroundColor: "{colors.strap}"
    textColor: "{colors.ink}"
    typography: "{typography.strap}"
    rounded: "{rounded.none}"
    padding: "0.2em 0.55em"
  frame-strap-name:
    backgroundColor: "{colors.strap}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.3rem 0.75rem"
  frame-strap-org:
    backgroundColor: "{colors.on-field}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.3rem 0.75rem"
  nav-link:
    textColor: "{colors.ink}"
    padding: "0 0.7rem"
    height: "44px"
---

# Design System: Eleanor McGough

## Overview

**Creative North Star: "The Lower Third"**

The site is set the way her own short-form video is set: a saturated cobalt field, chartreuse lower-third straps carrying near-black ink, and a 9:16 viewfinder with a rule-of-thirds grid, action-safe corner brackets and a centre cross. Identity moments (hero, page heads, the closing contact band, 404) sit on the cobalt field; reading moments (Right now, Resume, case studies) sit on a cool near-white page with ruled lists. The page alternates between "on air" and "the rundown".

Type does the broadcast work. Archivo is one variable family used across its width axis: headlines are condensed and heavy, set in mixed case; running text sits at normal width. Every corner is square. Depth is flat colour, with a single soft shadow reserved for the viewfinder so the frame reads as a device held in front of the band.

The world rejects the category default it was written against: cream page, an eyebrow over a big name, rounded cards and pills.

**Key Characteristics:**
- Cobalt field bands for identity, cool white page for reading.
- Chartreuse lower-third straps with ink text are the signature device.
- One variable family, Archivo; width (62% to 100%) carries hierarchy as much as size.
- Zero radius everywhere on the page.
- Two rule weights: a 2px ink rule opens a section, 1px grey hairlines divide items within it.

## Colors

A two-colour broadcast palette (cobalt and chartreuse) over cool, blue-tinted neutrals.

### Primary
- **Broadcast Cobalt** (field): the full-bleed band behind the hero, page heads, contact page and closing band; also link colour on the page, active nav underline, list bullets, project tags and the solid/outline buttons. It is the default focus-ring colour on the page.
- **Deep Cobalt** (field-deep): the inside of the 9:16 viewfinder and the empty project frame; one step darker so the frame reads as a screen set into the band. Never a band colour.

### Secondary
- **Lower-Third Chartreuse** (strap): straps, the primary action on cobalt, text selection, the skip link, and the focus ring inside cobalt bands. Always carries ink text, never white.

### Neutral
- **Studio Ink** (ink): all text on the page, the 2px section-opening rules, and the solid button's hover fill.
- **Slate** (ink-soft): secondary text: dates, details, tools, footer, empty states.
- **Cool Paper** (paper): the page background and header.
- **Hairline** (line): 1px dividers between list items, under the header and above the footer.
- **On-Air White** (on-field): headlines and ghost-button borders on cobalt; the secondary (organisation) bar of a frame strap.
- **Haze** (on-field-soft): long-form summary text on cobalt, one step softer than white.

### Named Rules
**The Strap Carries Ink Rule.** Chartreuse is always a filled bar with Studio Ink text. It is never a text colour on paper, and white never sits on it. The one exception is the copy-status message on cobalt, which is chartreuse text.

**The Two Grounds Rule.** A section is either cobalt (identity, calls to action) or paper (content). There is no third surface, no tinted panel and no card background.

## Typography

**Display Font:** Archivo variable (with Arial Narrow, system-ui, sans-serif), self-hosted, wght 100 to 900, wdth 62% to 125%
**Body Font:** Archivo at normal width
**Label Font:** Archivo at 85% width with tabular numerals

**Character:** One family stretched across its width axis: compressed and heavy for the broadcast voice, open and regular for reading. Width is a hierarchy tool alongside size and weight.

### Hierarchy
- **Display** (900, wdth 62%, clamp(3.25rem, 9vw, 6rem), line-height 0.92, -0.015em): the name in the hero and the contact page title. Two smaller steps exist: large (clamp(3rem, 8vw, 5.5rem)) for page-head titles and 404, medium (clamp(2.5rem, 6vw, 4.25rem)) for the closing band's "Let's talk."
- **Headline** (800, wdth 70%, clamp(1.75rem, 3.2vw, 2.4rem), line-height 1): section titles (Right now, Experience, Education, Skills); 1.4rem inside case studies.
- **Title** (800, wdth 80%, clamp(1.3rem, 2.2vw, 1.6rem), line-height 1.15): role, degree and entry titles in ruled lists. Skill-group terms use the same face at 1.1rem.
- **Strap** (700, wdth 85%, clamp(1.05rem, 1.8vw, 1.3rem), line-height 1.55): text inside chartreuse lower-thirds under a display title. Frame straps are tighter: 800 wdth 80% 1.05rem for the name bar, 500 0.85rem for the organisation bar.
- **Body** (400, normal width, 1rem, line-height 1.6): running text, held to 60 to 68ch. Hero summary runs larger, clamp(1.05rem, 1.6vw, 1.2rem).
- **Label** (600, wdth 85%, tabular numerals, Slate): dates in the left column of ruled lists ("Since Jan 2026", "Graduating May 2027") and project tags.

### Named Rules
**The Mixed-Case Headline Rule.** Display and headline type is set in mixed case, never uppercase. Caps flatten "McGough", and the strap-on-cobalt contrast already carries the broadcast voice.

**The Width Ladder Rule.** The heavier and larger the role, the narrower the width: display 62%, headline 70%, title 80%, strap and label 85%, body 100%. A new role picks a step on this ladder rather than a new family.

## Layout

A single centred container, min(100% - 2 × gutter, 72rem), with a fluid gutter (clamp(1rem, 4vw, 2.5rem)). Full-bleed bands stack vertically with fluid band padding (clamp(3.5rem, 9vw, 7rem)); page heads use a shorter top/bottom (clamp(3rem, 7vw, 5rem) / clamp(2rem, 4vw, 3rem)).

The hero is a two-column grid: copy on the left, the viewfinder on the right at minmax(15rem, 19rem). Ruled lists (Right now, resume entries, skill groups) use an 11rem date/term column beside a fluid content column with a 2rem gap. The portfolio is an auto-fill grid of 9:16 frames at a 15rem minimum.

At 760px and below, every two-column grid collapses to one column; the viewfinder is hidden when it has no photo (Right now follows directly with the same content) and becomes a 4:5 image up to 22rem when it has one; the closing band stacks. At 480px and below, buttons in an action row grow to fill the line. Every interactive target is at least 44px tall; buttons are 48px.

## Elevation & Depth

Flat by default. Depth comes from the two grounds (cobalt against paper) and from Deep Cobalt set inside cobalt for the viewfinder. Rules and hairlines do the structural work that shadows or cards would do elsewhere.

### Shadow Vocabulary
- **Viewfinder lift** (`box-shadow: 0 1.5rem 3rem -1rem rgb(5 12 60 / 0.55)`): only on the 9:16 frame in a cobalt band, a soft cobalt-tinted drop that holds the device in front of the field.

### Named Rules
**The One Lifted Object Rule.** The viewfinder is the only element with a shadow. Buttons, straps, lists and project frames stay flat.

## Shapes

Square corners throughout (0 radius): buttons, straps, frames, focus outlines. Straps are wrapped bars (box-decoration-break: clone) so each line of a multi-line strap is its own block, like stacked lower-thirds. The recurring silhouette is the 9:16 portrait frame with thirds-grid hairlines at 14% white, 2px corner brackets inset 6% at 75% white, and a 1px centre cross at 60% white. List bullets are small filled cobalt squares (0.45rem). Lines come in exactly two weights: 2px ink to open a section, 1px Hairline between items.

## Components

### Buttons
Blunt, square, broadcast-graphic buttons.
- **Shape:** square (0 radius), 48px tall, 2px border, 700 weight at 85% width, 1.05rem, 0.01em tracking.
- **Strap (primary on cobalt):** chartreuse with ink text; hover turns white. The main action in every cobalt band.
- **Ghost (secondary on cobalt):** transparent with a 2px white border and white text; hover fills white with cobalt text.
- **Solid (primary on paper):** cobalt with white text; hover turns ink.
- **Outline (secondary on paper):** 2px cobalt border, cobalt text; hover fills cobalt.
- **Hover / Focus / Active:** colour transitions at 0.2s on the out-expo curve; press nudges down 1px; focus is a 3px outline offset 3px, cobalt on paper and chartreuse inside cobalt bands.

### Lower-Third Strap
The signature component. A chartreuse bar of ink text, 700 at 85% width, wrapping as stacked bars, placed directly under a display title (hero headline, page-head subtitle, 404 message, availability on Contact). On load the lead strap wipes in from the left with a clip-path reveal (0.8s, out-expo), only when motion is allowed.

### Frame Strap (lower-third pair)
A two-bar lower-third inside a 9:16 frame: a chartreuse name bar (800, 80% width) above a white organisation bar (500, 0.85rem), both ink. Set in the frame's lower third inside the action-safe brackets; staggered wipe-in (0.9s, 0.18s apart) under no-preference motion. The same pair labels portfolio project frames (title and year).

### Viewfinder Frame
A 9:16 Deep Cobalt figure with the thirds grid, action-safe brackets and centre cross, holding either a cover photo or the current roles as frame straps. The only lifted object (see Elevation).

### Ruled List
The content pattern for Right now, Experience, Education and Skills: a headline, a 2px ink rule, then items divided by 1px Hairline, each with an 11rem Slate label column (dates, skill group) and a content column of title, organisation (600) and Slate detail text. Resume bullet points use cobalt squares.

### Navigation
Brand name at left (800, 75% width, 1.35rem, ink). Links at right (500, ink, 44px tall). Hover and the current page draw a 3px cobalt underline bar that grows from the centre (0.3s, out-expo); the current page is also set at 700. On mobile the nav wraps beneath the name and keeps the same treatment.

### Links
Cobalt with a 1px underline offset 0.2em, thickening to 2px on hover; white inside cobalt bands. The contact email is a display-scale link (800, 70% width, up to 4rem) with a thick chartreuse underline that thickens on hover.

## Do's and Don'ts

### Do:
- **Do** put identity moments and calls to action on a full-bleed cobalt band, and content on Cool Paper.
- **Do** set any subtitle or status line under a display title as a chartreuse lower-third strap with ink text.
- **Do** keep every corner square (0 radius) and every action at least 44px tall (buttons 48px).
- **Do** open each content section with a 2px ink rule and divide its items with 1px Hairline.
- **Do** pick headline widths from the Archivo width ladder (62%, 70%, 80%, 85%) and keep body text at normal width.
- **Do** switch the focus ring to chartreuse inside cobalt bands so it stays visible.
- **Do** gate strap wipe-ins behind prefers-reduced-motion: no-preference.

### Don't:
- **Don't** set display or headline type in all caps.
- **Don't** use rounded corners, pills or tag chips; tags are plain 600-weight cobalt text joined with middots.
- **Don't** wrap content in cards or tinted panels; use ruled lists and the two grounds.
- **Don't** put a small label or eyebrow above a headline; supporting lines go below as straps.
- **Don't** put white text on chartreuse or use chartreuse as text colour on paper.
- **Don't** add shadows beyond the viewfinder's.
- **Don't** introduce a second typeface; Archivo's width axis covers the display, label and body roles.
