package com.jimmer.mscout.core

/** One Marketplace vehicle ad, progressively enriched by the pipeline. */
data class Listing(
    val url: String,
    var title: String = "",
    var askingPrice: Int? = null,
    var location: String = "",
    var category: String = "",

    // filled by Normalize
    var year: Int? = null,
    var make: String = "",
    var model: String = "",
    var mileage: Int? = null,

    // filled by detail fetch
    var description: String = "",
    var vin: String = "",

    // filled by Carfax heuristics: 1 clean, 0 branded/dirty, null unknown
    var cleanCarfax: Int? = null,
    var titleNotes: String = "",

    // filled by CompsEngine
    var avgResaleNorth: Int? = null,
    var compCount: Int = 0,

    val notes: MutableList<String> = mutableListOf(),
) {
    val belowMarket: Int?
        get() {
            val a = askingPrice ?: return null
            val v = avgResaleNorth ?: return null
            return v - a
        }

    val belowMarketPct: Double?
        get() {
            val b = belowMarket ?: return null
            val v = avgResaleNorth ?: return null
            if (v == 0) return null
            return Math.round(1000.0 * b / v) / 10.0
        }

    /** Cache key for comps: make/model/year-bucket. */
    fun compKey(yearWindow: Int): String {
        val bucket = year?.let { (it / yearWindow) * yearWindow } ?: 0
        return "${make.lowercase()}|${model.lowercase()}|$bucket~$yearWindow"
    }
}
