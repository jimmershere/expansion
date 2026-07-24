package com.jimmer.mscout.web

/**
 * All Facebook-specific JavaScript lives here. When Facebook changes markup
 * and a sweep returns 0 cards, this is the file to patch (same role as fb.py
 * in the desktop tool).
 */
object Scripts {

    /** Returns JSON array of {id, text} for every listing card on screen. */
    val EXTRACT_CARDS = """
        (function () {
          var out = [];
          var seen = {};
          var links = document.querySelectorAll('a[href*="/marketplace/item/"]');
          for (var i = 0; i < links.length; i++) {
            var m = links[i].href.match(/\/marketplace\/item\/(\d+)/);
            if (!m || seen[m[1]]) continue;
            seen[m[1]] = 1;
            out.push({ id: m[1], text: links[i].innerText || '' });
          }
          return JSON.stringify(out);
        })();
    """.trimIndent()

    /** Scrolls the results feed by roughly two viewports. */
    val SCROLL = """
        (function () {
          window.scrollBy(0, Math.floor(window.innerHeight * (1.8 + Math.random() * 0.6)));
          return 'ok';
        })();
    """.trimIndent()

    /** Expands a truncated description if a "See more" toggle is present. */
    val CLICK_SEE_MORE = """
        (function () {
          var spans = document.querySelectorAll('span');
          for (var i = 0; i < spans.length; i++) {
            if (spans[i].innerText === 'See more') { spans[i].click(); return 'clicked'; }
          }
          return 'none';
        })();
    """.trimIndent()

    /** Full visible page text (detail pages: price, mileage, description, VIN). */
    val BODY_TEXT = """
        (function () {
          return JSON.stringify((document.body && document.body.innerText || '').slice(0, 8000));
        })();
    """.trimIndent()
}
