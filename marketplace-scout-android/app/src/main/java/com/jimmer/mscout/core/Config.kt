package com.jimmer.mscout.core

/** Mirror of the desktop tool's config.yaml. Edit here and rebuild. */
object Config {

    // Marketplace city slugs to sweep for deals (the buy side).
    val searchAreas = listOf(
        "raleigh", "charlotte", "greensboro", "winstonsalem",
        "fayetteville", "asheville", "wilmington",
    )

    // Northern-US metros used only to build comparable-price medians.
    val compMetros = listOf(
        "boston", "nyc", "philadelphia", "pittsburgh", "cleveland", "detroit",
        "chicago", "minneapolis", "milwaukee", "seattle", "portland",
    )

    data class Category(
        val queries: List<String>,
        val minYear: Int? = null,
        val maxYear: Int? = null,
    )

    val categories: Map<String, Category> = linkedMapOf(
        "pickup_trucks" to Category(
            maxYear = 1999,
            queries = listOf(
                "classic pickup truck", "chevy c10", "chevy k10 4x4",
                "square body chevy", "ford f100", "ford f150 obs", "dodge d100",
                "dodge ram cummins 12 valve", "toyota pickup 4x4",
                "gmc sierra classic",
            ),
        ),
        "classic_cars" to Category(
            maxYear = 1985,
            queries = listOf(
                "classic car", "chevelle", "camaro", "mustang fastback",
                "nova ss", "dodge charger", "plymouth barracuda", "pontiac gto",
                "oldsmobile 442", "vw beetle classic", "datsun 240z",
            ),
        ),
        "import_tuners_90s" to Category(
            minYear = 1988, maxYear = 2002,
            queries = listOf(
                "toyota supra", "mazda rx-7", "nissan 240sx", "nissan 300zx",
                "nissan skyline", "toyota mr2", "acura integra", "honda civic si",
                "honda prelude", "acura nsx", "mitsubishi eclipse gsx",
                "eagle talon tsi", "mitsubishi 3000gt", "subaru impreza wrx",
                "mitsubishi lancer evolution", "toyota celica all-trac",
                "mazda miata",
            ),
        ),
        "custom_vehicles" to Category(
            queries = listOf(
                "restomod", "hot rod", "rat rod", "custom truck", "lifted truck",
                "lowrider", "engine swap", "ls swap", "pro street",
            ),
        ),
    )

    object Filters {
        const val minPrice = 1_500       // below this on FB it's nearly all scams/parts cars
        const val maxPrice = 60_000
        const val maxMileage = 250_000
        const val dealThresholdPct = 15.0
        const val minComps = 5
        const val compYearWindow = 3
        const val compTrimPct = 10
        val blockedKeywords = listOf("parts only", "no title", "bill of sale only", "scrap", "read")
    }

    object Pacing {
        const val minDelayMs = 2_000L
        const val maxDelayMs = 6_000L
        const val maxCardsPerSearch = 40
        const val maxDetailPages = 120
        const val pageLoadTimeoutMs = 30_000L
    }

    const val compCacheTtlDays = 14
}
