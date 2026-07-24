package com.jimmer.mscout.core

/**
 * Clean-Carfax scoring from listing text, ported from the desktop carfax.py.
 * A heuristic on seller claims, NOT a real Carfax pull — verify with the VIN
 * before money changes hands.
 */
object Carfax {

    // Evidence the history is BAD — any hit forces 0 regardless of clean claims.
    private val DIRTY = Regex(
        listOf(
            """salvage""", """rebuilt\s+title""", """rebuild\s+title""",
            """branded\s+title""", """flood""", """lemon\s+law""",
            """odometer\s+(?:rollback|discrepancy|exempt)""",
            """true\s+miles\s+unknown""", """tmu\b""", """frame\s+damage""",
            """theft\s+recovery""", """r\s*title""",
        ).joinToString("|"),
        RegexOption.IGNORE_CASE,
    )

    // Evidence the seller affirmatively claims clean history.
    private val CLEAN = Regex(
        listOf(
            """clean\s+carfax""", """clean\s+car\s*fax""", """clean\s+autocheck""",
            """clean\s+title""", """clear\s+title""", """no\s+accidents?""",
            """accident[-\s]free""", """one\s+owner""",
        ).joinToString("|"),
        RegexOption.IGNORE_CASE,
    )

    fun score(listing: Listing) {
        val text = "${listing.title}\n${listing.description}"
        val dirty = DIRTY.find(text)
        val clean = CLEAN.find(text)

        when {
            dirty != null -> {
                listing.cleanCarfax = 0
                listing.titleNotes = "flag: '${dirty.value.trim()}'"
            }
            clean != null -> {
                listing.cleanCarfax = 1
                listing.titleNotes = "seller claims: '${clean.value.trim()}'"
            }
            else -> {
                listing.cleanCarfax = null
                listing.titleNotes = "no history evidence in ad"
            }
        }
        if (listing.vin.isNotEmpty()) {
            listing.notes.add("VIN ${listing.vin} — pull real Carfax before buying")
        }
    }

    /** Returns the blocked keyword hit, or null if the text is fine. */
    fun blockedKeyword(text: String): String? {
        val low = text.lowercase()
        return Config.Filters.blockedKeywords.firstOrNull { low.contains(it) }
    }
}
