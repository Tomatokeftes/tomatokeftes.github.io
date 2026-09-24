// Opens the abstract and BibTeX panels under a publication, and copies code to the clipboard.
document.addEventListener("click", function (event) {
  var toggle = event.target.closest(".toggle");
  if (toggle) {
    var panel = document.getElementById(toggle.getAttribute("aria-controls"));
    var open = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(open));
    if (panel) panel.classList.toggle("is-open", open);
    return;
  }

  var copy = event.target.closest("[data-copy]");
  var code = copy && copy.parentElement.querySelector("code");
  if (!code || !navigator.clipboard) return;
  navigator.clipboard.writeText(code.textContent.trim()).then(function () {
    copy.textContent = "Copied";
    copy.classList.add("is-done");
    setTimeout(function () {
      copy.textContent = "Copy";
      copy.classList.remove("is-done");
    }, 1600);
  });
});
