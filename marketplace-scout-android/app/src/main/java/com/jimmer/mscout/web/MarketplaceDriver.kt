package com.jimmer.mscout.web

import android.annotation.SuppressLint
import android.net.Uri
import android.webkit.WebView
import android.webkit.WebViewClient
import com.jimmer.mscout.core.Config
import com.jimmer.mscout.core.Listing
import com.jimmer.mscout.core.Normalize
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.delay
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeoutOrNull
import org.json.JSONArray
import org.json.JSONTokener
import kotlin.coroutines.resume
import kotlin.random.Random

class NotLoggedInException : Exception("Not logged into Facebook — tap Login first")

/**
 * Drives the on-screen WebView the way the desktop tool drives Playwright:
 * your own logged-in session, random 2–6 s delays, scroll caps, and a hard
 * limit on detail-page fetches per run. Must be called on the main thread
 * (all methods are suspend and non-blocking).
 */
class MarketplaceDriver(private val web: WebView) {

    private var pageLoaded: CompletableDeferred<Unit>? = null
    private var detailFetches = 0

    init {
        web.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                pageLoaded?.complete(Unit)
            }
        }
    }

    fun resetRunCaps() {
        detailFetches = 0
    }

    val loggedIn: Boolean
        get() {
            val url = web.url ?: return false
            return listOf("login", "checkpoint", "recover").none { url.contains(it) }
        }

    // -- page mechanics ----------------------------------------------------
    private suspend fun load(url: String) {
        val gate = CompletableDeferred<Unit>()
        pageLoaded = gate
        web.loadUrl(url)
        withTimeoutOrNull(Config.Pacing.pageLoadTimeoutMs) { gate.await() }
        sleepJitter()
    }

    private suspend fun js(script: String): String =
        suspendCancellableCoroutine { cont ->
            web.evaluateJavascript(script) { result -> cont.resume(result ?: "null") }
        }

    /** evaluateJavascript returns a JSON-encoded value; unwrap string results. */
    private suspend fun jsString(script: String): String {
        val raw = js(script)
        return (JSONTokener(raw).nextValue() as? String) ?: ""
    }

    private suspend fun sleepJitter() {
        delay(Random.nextLong(Config.Pacing.minDelayMs, Config.Pacing.maxDelayMs))
    }

    // -- search ------------------------------------------------------------
    @SuppressLint("SetJavaScriptEnabled")
    suspend fun search(
        city: String,
        query: String,
        minYear: Int? = null,
        maxYear: Int? = null,
    ): List<Listing> {
        val url = Uri.Builder()
            .scheme("https").authority("www.facebook.com")
            .appendPath("marketplace").appendPath(city).appendPath("search")
            .appendQueryParameter("query", query)
            .appendQueryParameter("exact", "false")
            .appendQueryParameter("sortBy", "creation_time_descend")
            .appendQueryParameter("minPrice", Config.Filters.minPrice.toString())
            .appendQueryParameter("maxPrice", Config.Filters.maxPrice.toString())
            .apply {
                minYear?.let { appendQueryParameter("minYear", it.toString()) }
                maxYear?.let { appendQueryParameter("maxYear", it.toString()) }
            }
            .build().toString()

        load(url)
        if (!loggedIn) throw NotLoggedInException()

        val found = LinkedHashMap<String, Listing>()
        var stagnantScrolls = 0
        while (found.size < Config.Pacing.maxCardsPerSearch && stagnantScrolls < 3) {
            val before = found.size
            val cards = JSONArray(jsString(Scripts.EXTRACT_CARDS))
            for (i in 0 until cards.length()) {
                val card = cards.getJSONObject(i)
                val id = card.getString("id")
                if (found.containsKey(id)) continue
                found[id] = cardToListing(id, card.getString("text"))
                if (found.size >= Config.Pacing.maxCardsPerSearch) break
            }
            stagnantScrolls = if (found.size == before) stagnantScrolls + 1 else 0
            js(Scripts.SCROLL)
            sleepJitter()
        }
        return found.values.toList()
    }

    private fun cardToListing(id: String, text: String): Listing {
        // Card text is newline-separated: price / title / location / (mileage)
        val lines = text.split("\n").map { it.trim() }.filter { it.isNotEmpty() }
        return Listing(
            url = "https://www.facebook.com/marketplace/item/$id/",
            title = lines.firstOrNull { !it.startsWith("$") && it.length > 8 } ?: "",
            askingPrice = lines.firstNotNullOfOrNull { Normalize.parsePrice(it) },
            location = lines.firstOrNull { Regex(""",\s*[A-Z]{2}$""").containsMatchIn(it) } ?: "",
            mileage = lines.firstNotNullOfOrNull { Normalize.parseMileage(it) },
        )
    }

    // -- detail ------------------------------------------------------------
    /** Open the listing page; fill mileage, description, VIN. */
    suspend fun fetchDetail(listing: Listing) {
        if (detailFetches >= Config.Pacing.maxDetailPages) {
            listing.notes.add("detail fetch skipped (run cap reached)")
            return
        }
        detailFetches++

        load(listing.url)
        js(Scripts.CLICK_SEE_MORE)
        delay(800)

        val body = jsString(Scripts.BODY_TEXT)
        listing.description = body
        if (listing.mileage == null) listing.mileage = Normalize.parseMileage(body)
        if (listing.askingPrice == null) listing.askingPrice = Normalize.parsePrice(body)
        listing.vin = Normalize.parseVin(body)
    }
}
