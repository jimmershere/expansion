package com.jimmer.mscout

import android.content.Context
import com.jimmer.mscout.core.Carfax
import com.jimmer.mscout.core.CompsEngine
import com.jimmer.mscout.core.Config
import com.jimmer.mscout.core.Listing
import com.jimmer.mscout.core.Normalize
import com.jimmer.mscout.export.Exporter
import com.jimmer.mscout.web.MarketplaceDriver
import kotlinx.coroutines.CancellationException
import java.io.File

/** The Android equivalent of the desktop tool's `mscout run`. */
class ScoutController(
    private val driver: MarketplaceDriver,
    private val context: Context,
) {

    data class Result(val file: File, val dealCount: Int, val totalFound: Int)

    suspend fun runSweep(onStatus: (String) -> Unit): Result {
        driver.resetRunCaps()
        val found = LinkedHashMap<String, Listing>()

        for ((catName, cat) in Config.categories) {
            for (area in Config.searchAreas) {
                for (query in cat.queries) {
                    onStatus("[$catName] $area: \"$query\"")
                    val cards = try {
                        driver.search(area, query, cat.minYear, cat.maxYear)
                    } catch (e: CancellationException) {
                        throw e // Stop tapped — end the sweep, don't march on
                    } catch (e: com.jimmer.mscout.web.NotLoggedInException) {
                        throw e
                    } catch (e: Exception) {
                        onStatus("search failed: ${e.javaClass.simpleName}")
                        continue
                    }
                    for (l in cards) {
                        if (found.containsKey(l.url)) continue
                        if (Carfax.blockedKeyword(l.title) != null) continue
                        l.category = catName
                        l.year = l.year ?: Normalize.parseYear(l.title)
                        Normalize.parseMakeModel(l.title).let { (make, model) ->
                            l.make = make; l.model = model
                        }
                        if (yearOk(l, cat) && basicsOk(l)) found[l.url] = l
                    }
                }
            }
        }

        onStatus("Found ${found.size} listings; fetching details + valuing…")
        val comps = CompsEngine(driver, context)
        found.values.forEachIndexed { i, l ->
            onStatus("detail ${i + 1}/${found.size}: ${l.title.take(40)}")
            driver.fetchDetail(l)
            Carfax.score(l)
            // A card missing price/mileage passed the first filter pass; the
            // detail page may have revealed values outside the bounds.
            if (!basicsOk(l)) {
                l.notes.add("dropped after detail: outside price/mileage bounds")
                return@forEachIndexed
            }
            comps.value(l, onStatus)
        }

        val deals = found.values.filter {
            basicsOk(it) && (it.belowMarketPct ?: -1.0) >= Config.Filters.dealThresholdPct
        }
        val file = Exporter.writeXlsx(context, deals)
        return Result(file, deals.size, found.size)
    }

    private fun yearOk(l: Listing, cat: Config.Category): Boolean {
        val y = l.year ?: return true // keep; detail page may reveal it
        if (cat.minYear != null && y < cat.minYear) return false
        if (cat.maxYear != null && y > cat.maxYear) return false
        return true
    }

    private fun basicsOk(l: Listing): Boolean {
        l.askingPrice?.let {
            if (it !in Config.Filters.minPrice..Config.Filters.maxPrice) return false
        }
        l.mileage?.let { if (it > Config.Filters.maxMileage) return false }
        return true
    }
}
