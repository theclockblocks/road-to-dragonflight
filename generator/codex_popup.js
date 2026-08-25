/* Codex popup — open codex entries in an overlay instead of navigating away.
 *
 * Progressive enhancement: every link keeps its real href="codex.html#id", so
 * without JS (or if the fetch fails, or <dialog> is unsupported) the browser
 * just follows the link to the Codex page exactly as before. Nothing here is
 * load-bearing for the content.
 */
(function () {
  "use strict";

  var CODEX = "codex.html";
  var HREF = /(?:^|\/)codex\.html#([A-Za-z0-9_-]+)$/;

  // Bail out entirely on browsers without the APIs we need.
  if (!window.fetch || !window.DOMParser || !document.createElement("dialog").showModal) return;

  var codexDoc = null;   // parsed codex.html, fetched once
  var pending = null;    // in-flight fetch promise
  var dlg, bodyEl, backBtn, fullLink;
  var stack = [];        // entry ids visited within this popup session
  var pushedState = false;

  function fetchCodex() {
    if (codexDoc) return Promise.resolve(codexDoc);
    if (pending) return pending;
    pending = fetch(CODEX, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("codex " + r.status);
        return r.text();
      })
      .then(function (html) {
        codexDoc = new DOMParser().parseFromString(html, "text/html");
        return codexDoc;
      });
    return pending;
  }

  function build() {
    if (dlg) return;
    dlg = document.createElement("dialog");
    dlg.className = "cxpop";
    dlg.setAttribute("aria-label", "Codex entry");
    dlg.innerHTML =
      '<div class="cxpop-inner">' +
        '<div class="cxpop-bar">' +
          '<button class="cxpop-back" type="button" hidden>&larr; Back</button>' +
          '<button class="cxpop-close" type="button" aria-label="Close">&times;</button>' +
        '</div>' +
        '<div class="cxpop-body" tabindex="-1"></div>' +
        '<p class="cxpop-foot"><a class="cxpop-full" href="' + CODEX + '">Open the full Codex &rarr;</a></p>' +
      '</div>';
    document.body.appendChild(dlg);

    bodyEl = dlg.querySelector(".cxpop-body");
    backBtn = dlg.querySelector(".cxpop-back");
    fullLink = dlg.querySelector(".cxpop-full");

    dlg.querySelector(".cxpop-close").addEventListener("click", function () { dismiss(); });
    backBtn.addEventListener("click", function () {
      stack.pop();                       // drop current
      var prev = stack.pop();            // step back to the previous one
      if (prev) render(prev);
    });

    // Click on the backdrop (the dialog element itself) closes.
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg) dismiss();
    });

    // Escape key fires 'cancel'; keep history in sync.
    dlg.addEventListener("cancel", function (e) {
      e.preventDefault();
      dismiss();
    });
  }

  function render(id) {
    var entry = codexDoc.getElementById(id);
    if (!entry) { window.location.href = CODEX + "#" + id; return; }

    var clone = entry.cloneNode(true);
    clone.removeAttribute("id");        // never duplicate a page id

    bodyEl.innerHTML = "";
    bodyEl.appendChild(clone);
    fullLink.setAttribute("href", CODEX + "#" + id);

    stack.push(id);
    backBtn.hidden = stack.length < 2;

    bodyEl.scrollTop = 0;
    bodyEl.focus();
  }

  function open(id) {
    build();
    if (!dlg.open) {
      bodyEl.innerHTML = '<p class="cxpop-wait">Looking that up&hellip;</p>';
      dlg.showModal();
      // A history entry so the phone's back gesture closes the popup
      // instead of leaving the chapter.
      try {
        history.pushState({ cxpop: true }, "");
        pushedState = true;
      } catch (err) { pushedState = false; }
      stack = [];
    }
    fetchCodex().then(function () {
      if (dlg.open) render(id);
    }).catch(function () {
      window.location.href = CODEX + "#" + id;
    });
  }

  function close() {
    if (dlg && dlg.open) dlg.close();
    stack = [];
  }

  // Close and unwind the history entry we added.
  function dismiss() {
    if (pushedState) {
      pushedState = false;
      history.back();       // triggers popstate -> close()
    } else {
      close();
    }
  }

  window.addEventListener("popstate", function () {
    pushedState = false;
    close();
  });

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;   // let new-tab clicks through
    if (!e.target || !e.target.closest) return;

    var a = e.target.closest("a[href]");
    if (!a) return;
    if (a.target && a.target !== "_self") return;                   // e.g. the wiki links

    var m = a.getAttribute("href").match(HREF);
    if (!m) return;

    e.preventDefault();
    open(m[1]);
  });

  // Warm the cache when the browser is idle so the first tap feels instant.
  var idle = window.requestIdleCallback || function (fn) { return setTimeout(fn, 1500); };
  idle(function () { fetchCodex().catch(function () {}); });
})();
