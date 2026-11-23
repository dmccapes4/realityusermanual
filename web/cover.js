(() => {
  "use strict";
  const button = document.getElementById("open-book");
  const invitation = document.getElementById("invitation");
  if (!button) return;

  let opening = false;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function openBook() {
    if (opening) return;
    opening = true;
    button.disabled = true;
    document.body.classList.add("opening");
    invitation.textContent = "Opening";
    const delay = reduced ? 120 : 1120;
    window.setTimeout(() => {
      document.body.classList.add("departing");
      window.setTimeout(() => location.assign("/book/"), reduced ? 20 : 260);
    }, delay);
  }

  button.addEventListener("click", openBook);
  window.addEventListener("pageshow", () => {
    opening = false;
    button.disabled = false;
    document.body.classList.remove("opening", "departing");
    invitation.textContent = "Click the cover to begin";
  });
})();
