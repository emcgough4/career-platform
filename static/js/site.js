// Progressive enhancements: every page works without this file.
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

// Reel: prev/next buttons, arrow keys and drag-to-scroll on the horizontal work row.
document.querySelectorAll("[data-reel]").forEach((reel) => {
  const controls = reel.parentElement.querySelector("[data-reel-controls]");
  const step = () => (reel.querySelector(".card")?.getBoundingClientRect().width || 280) + 16;
  const scrollByCards = (direction) =>
    reel.scrollBy({ left: direction * step(), behavior: reducedMotion.matches ? "auto" : "smooth" });

  const updateControls = () => {
    if (!controls) return;
    const overflow = reel.scrollWidth - reel.clientWidth > 4;
    controls.hidden = !overflow;
    controls.querySelector("[data-reel-prev]").disabled = reel.scrollLeft <= 4;
    controls.querySelector("[data-reel-next]").disabled = reel.scrollLeft >= reel.scrollWidth - reel.clientWidth - 4;
  };

  controls?.querySelector("[data-reel-prev]").addEventListener("click", () => scrollByCards(-1));
  controls?.querySelector("[data-reel-next]").addEventListener("click", () => scrollByCards(1));
  reel.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") { event.preventDefault(); scrollByCards(1); }
    if (event.key === "ArrowLeft") { event.preventDefault(); scrollByCards(-1); }
  });
  reel.addEventListener("scroll", updateControls, { passive: true });
  window.addEventListener("resize", updateControls);
  updateControls();

  // Drag with a mouse; touch and trackpads already scroll natively.
  let start = null;
  reel.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "mouse") return;
    start = { x: event.clientX, left: reel.scrollLeft, moved: false };
  });
  reel.addEventListener("pointermove", (event) => {
    if (!start) return;
    const distance = event.clientX - start.x;
    if (Math.abs(distance) > 4) {
      start.moved = true;
      reel.classList.add("is-dragging");
      reel.scrollLeft = start.left - distance;
    }
  });
  const endDrag = () => { reel.classList.remove("is-dragging"); setTimeout(() => { start = null; }, 0); };
  reel.addEventListener("pointerup", endDrag);
  reel.addEventListener("pointerleave", endDrag);
  // A drag should not count as a click on the card underneath.
  reel.addEventListener("click", (event) => { if (start?.moved) event.preventDefault(); }, true);
});

// Cards: muted clips play while hovered or focused. On touch, the first tap previews and the second opens.
document.querySelectorAll(".card-link").forEach((card) => {
  const video = card.querySelector("video[data-preview]");
  if (!video) return;
  let lastPointer = "mouse";
  const play = () => { if (!reducedMotion.matches) video.play().catch(() => {}); };
  const stop = () => { video.pause(); };
  card.addEventListener("pointerdown", (event) => { lastPointer = event.pointerType; });
  card.addEventListener("pointerenter", (event) => { if (event.pointerType === "mouse") play(); });
  card.addEventListener("pointerleave", (event) => { if (event.pointerType === "mouse") stop(); });
  // Taps also focus the link on Android; let the click handler own touch previews.
  card.addEventListener("focus", () => { if (lastPointer !== "touch") play(); });
  card.addEventListener("blur", stop);
  card.addEventListener("click", (event) => {
    if (lastPointer !== "touch" || reducedMotion.matches || !video.paused) return;
    event.preventDefault();
    document.querySelectorAll("video[data-preview]").forEach((other) => { if (other !== video) other.pause(); });
    play();
  });
});

// Hero clip: autoplay muted unless the visitor prefers reduced motion, with a pause/play control.
document.querySelectorAll(".hero-media video[data-preview]").forEach((video) => {
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "icon-button media-toggle";
  const icons = {
    pause: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/></svg>',
    play: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/></svg>',
  };
  const render = () => {
    toggle.innerHTML = video.paused ? icons.play : icons.pause;
    toggle.setAttribute("aria-label", video.paused ? "Play clip" : "Pause clip");
  };
  toggle.addEventListener("click", () => { if (video.paused) video.play().catch(() => {}); else video.pause(); });
  video.addEventListener("play", render);
  video.addEventListener("pause", render);
  video.after(toggle);
  if (!reducedMotion.matches) video.play().catch(() => {});
  render();
});

// Resume: print-to-PDF button.
document.querySelectorAll("[data-print]").forEach((button) => {
  button.hidden = false;
  button.addEventListener("click", () => window.print());
});

// Contact: copy the email address.
document.querySelectorAll("[data-copy]").forEach((button) => {
  if (!navigator.clipboard) return;
  const status = document.querySelector(".copy-status");
  button.hidden = false;
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      status.textContent = "Copied to clipboard";
    } catch {
      status.textContent = "Couldn’t copy. Select the address above instead.";
    }
    setTimeout(() => { status.textContent = ""; }, 4000);
  });
});
