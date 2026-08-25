// CS 315 mermaid initialization.
//
// pymdownx.superfences emits mermaid diagrams as
//   <pre class="mermaid-diagram"><code>...</code></pre>
// (a custom class, so mkdocs-material's built-in mermaid handler — which targets
// ".mermaid" — leaves them alone and cannot clobber the source by rendering too
// early). We render them ourselves, but only AFTER web fonts are ready: mermaid
// measures text to lay out nodes, and rendering before fonts load yields NaN
// geometry. The source text is HTML-escaped in the <code> block, so we read the
// DECODED textContent, render with mermaid.render(), and inject the SVG.
(function () {
  if (typeof window.mermaid !== "undefined") {
    window.mermaid.initialize({ startOnLoad: false, theme: "default" });
  }

  async function renderAll() {
    if (typeof window.mermaid === "undefined") {
      return;
    }
    window.mermaid.initialize({ startOnLoad: false, theme: "default" });

    // Wait for fonts so text measurement is accurate.
    if (document.fonts && document.fonts.ready) {
      try { await document.fonts.ready; } catch (e) {}
    }

    var blocks = document.querySelectorAll("pre.mermaid-diagram, div.mermaid-diagram");
    var n = 0;
    for (var i = 0; i < blocks.length; i++) {
      var block = blocks[i];
      if (block.querySelector("svg")) {
        continue;
      }
      var code = block.querySelector("code");
      var definition = (code || block).textContent;
      try {
        var result = await window.mermaid.render("mermaid-svg-" + n++, definition);
        var div = document.createElement("div");
        div.className = "mermaid-diagram mermaid-rendered";
        div.innerHTML = result.svg;
        block.replaceWith(div);
      } catch (err) {
        if (window.console) {
          console.error("mermaid render failed for a diagram", err);
        }
      }
    }
  }

  if (document.readyState === "complete") {
    renderAll();
  } else {
    window.addEventListener("load", renderAll);
  }
})();
