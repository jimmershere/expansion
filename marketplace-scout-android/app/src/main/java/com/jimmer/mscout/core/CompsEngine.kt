package com.jimmer.mscout.core

import android.content.Context
import com.jimmer.mscout.web.MarketplaceDriver
import org.json.JSONObject
import java.io.File

/**
 * Average northern-US resale value = trimmed median of comparable Marketplace
 * asking prices across the configured northern metros. Same comps logic as
 * the desktop valuation.py; the cache is a JSON file in app storage keyed by
 * make/model/year-bucket so twenty '72 C10s research the value once.
 */
class CompsEngine(private val driver: MarketplaceDriver, context: Context) {

    private val cacheFile = File(context.filesDir, "comps-cache.json")
    private val cache: JSONObject =
        if (cacheFile.exists()) JSONObject(cacheFile.readText()) else JSONObject()

    suspend fun value(listing: Listing, onStatus: (String) -> Unit) {
        if (listing.make.isEmpty() || listing.year == null) {
            listing.notes.add("no comps: could not normalize make/year")
            return
        }

        val key = listing.compKey(Config.Filters.compYearWindow)
        cachedMedian(key)?.let { (median, n) ->
            listing.avgResaleNorth = median
            listing.compCount = n
            return
        }

        onStatus("comps: ${listing.year} ${listing.make} ${listing.model}")
        val prices = gatherCompPrices(listing)
        if (prices.size < Config.Filters.minComps) {
            listing.notes.add("no comps: only ${prices.size} found (need ${Config.Filters.minComps})")
            return
        }

        val median = trimmedMedian(prices, Config.Filters.compTrimPct)
        listing.avgResaleNorth = median
        listing.compCount = prices.size
        cache.put(key, JSONObject()
            .put("median", median)
            .put("n", prices.size)
            .put("at", System.currentTimeMillis()))
        cacheFile.writeText(cache.toString())
    }

    // -- internals ---------------------------------------------------------
    private fun cachedMedian(key: String): Pair<Int, Int>? {
        val entry = cache.optJSONObject(key) ?: return null
        val ttlMs = Config.compCacheTtlDays * 86_400_000L
        if (System.currentTimeMillis() - entry.getLong("at") > ttlMs) return null
        return entry.getInt("median") to entry.getInt("n")
    }

    private suspend fun gatherCompPrices(listing: Listing): List<Int> {
        val window = Config.Filters.compYearWindow
        val query = "${listing.year} ${listing.make} ${listing.model}".trim()
        val prices = mutableListOf<Int>()
        for (metro in Config.compMetros) {
            try {
                for (comp in driver.search(
                    metro, query,
                    minYear = listing.year!! - window, maxYear = listing.year!! + window,
                )) {
                    val price = comp.askingPrice ?: continue
                    if (plausible(comp, listing)) prices.add(price)
                }
            } catch (e: com.jimmer.mscout.web.NotLoggedInException) {
                throw e // stop the whole run
            } catch (e: Exception) {
                listing.notes.add("comps: $metro failed (${e.javaClass.simpleName})")
            }
            // enough signal? stop burning page loads
            if (prices.size >= 4 * Config.Filters.minComps) break
        }
        return prices
    }

    /** Comp must mention the model and sit in the year window. */
    private fun plausible(comp: Listing, target: Listing): Boolean {
        val title = comp.title.lowercase()
        val modelHead = target.model.split(" ").firstOrNull()?.lowercase() ?: ""
        if (modelHead.isNotEmpty() && !title.contains(modelHead)) return false
        val compYear = Normalize.parseYear(comp.title)
        val targetYear = target.year
        if (compYear != null && targetYear != null &&
            kotlin.math.abs(compYear - targetYear) > Config.Filters.compYearWindow
        ) return false
        val price = comp.askingPrice ?: 0
        return price in Config.Filters.minPrice..Config.Filters.maxPrice
    }

    private fun trimmedMedian(prices: List<Int>, trimPct: Int): Int {
        val sorted = prices.sorted()
        val k = sorted.size * trimPct / 100
        val trimmed = if (sorted.size > 2 * k) sorted.subList(k, sorted.size - k) else sorted
        val mid = trimmed.size / 2
        return if (trimmed.size % 2 == 1) trimmed[mid]
        else (trimmed[mid - 1] + trimmed[mid]) / 2
    }
}
