package com.jimmer.mscout.core

/** Title/text parsing, ported from the desktop tool's normalize.py. */
object Normalize {

    private val MAKES: Map<String, List<String>> = mapOf(
        "Chevrolet" to listOf("chevrolet", "chevy", "chev"),
        "Ford" to listOf("ford"),
        "Dodge" to listOf("dodge"),
        "Ram" to listOf("ram"),
        "GMC" to listOf("gmc"),
        "Toyota" to listOf("toyota"),
        "Nissan" to listOf("nissan", "datsun"),
        "Honda" to listOf("honda"),
        "Acura" to listOf("acura"),
        "Mazda" to listOf("mazda"),
        "Mitsubishi" to listOf("mitsubishi", "mitsu"),
        "Subaru" to listOf("subaru"),
        "Eagle" to listOf("eagle"),
        "Plymouth" to listOf("plymouth"),
        "Pontiac" to listOf("pontiac"),
        "Oldsmobile" to listOf("oldsmobile", "olds"),
        "Buick" to listOf("buick"),
        "Cadillac" to listOf("cadillac", "caddy"),
        "Chrysler" to listOf("chrysler"),
        "Jeep" to listOf("jeep"),
        "Volkswagen" to listOf("volkswagen", "vw"),
        "Mercedes-Benz" to listOf("mercedes-benz", "mercedes", "benz"),
        "BMW" to listOf("bmw"),
        "Porsche" to listOf("porsche"),
        "AMC" to listOf("amc"),
        "International" to listOf("international", "ih"),
        "Studebaker" to listOf("studebaker"),
        "Lexus" to listOf("lexus"),
        "Infiniti" to listOf("infiniti"),
    )

    private val aliasToMake: Map<String, String> =
        MAKES.flatMap { (make, aliases) -> aliases.map { it to make } }.toMap()

    private val YEAR = Regex("""\b(19[3-9]\d|20[0-2]\d)\b""")
    private val MILEAGE_PATTERNS = listOf(
        Regex("""[Dd]riven\s+([\d,]+)\s*miles"""),
        Regex("""\b([\d,]{4,7})\s*(?:original\s+)?miles\b""", RegexOption.IGNORE_CASE),
        Regex("""\b(\d{1,3})\s*[kK]\s*(?:original\s+)?miles?\b"""),
        Regex("""\bmileage[:\s]+([\d,]+)""", RegexOption.IGNORE_CASE),
    )
    private val PRICE = Regex("""\$\s*([\d,]+)""")
    private val VIN = Regex("""\b([A-HJ-NPR-Z0-9]{17})\b""")

    fun parseYear(text: String): Int? = YEAR.find(text)?.value?.toInt()

    /** "1972 Chevy C10 shortbed" -> ("Chevrolet", "C10 shortbed"). */
    fun parseMakeModel(title: String): Pair<String, String> {
        val words = title.split(Regex("""\s+"""))
        for ((i, w) in words.withIndex()) {
            val make = aliasToMake[w.lowercase().trim('.', ',')] ?: continue
            val modelWords = mutableListOf<String>()
            for (mw in words.drop(i + 1).take(3)) {
                if (YEAR.matches(mw) || mw.startsWith("$")) break
                modelWords.add(mw.trim('.', ','))
            }
            return make to modelWords.joinToString(" ")
        }
        return "" to ""
    }

    fun parseMileage(text: String): Int? {
        for (pat in MILEAGE_PATTERNS) {
            val m = pat.find(text) ?: continue
            val raw = m.groupValues[1].replace(",", "")
            var value = raw.toIntOrNull() ?: continue
            if (m.value.lowercase().contains("k") && value < 1000) value *= 1000
            if (value in 100..1_000_000) return value
        }
        return null
    }

    fun parsePrice(text: String): Int? {
        val m = PRICE.find(text) ?: return null
        val value = m.groupValues[1].replace(",", "").toIntOrNull() ?: return null
        return if (value > 0) value else null
    }

    /** 17-char modern VINs only; pre-1981 VINs are free-form and skipped. */
    fun parseVin(text: String): String {
        for (m in VIN.findAll(text.uppercase())) {
            val vin = m.groupValues[1]
            if (vin.any { it.isDigit() } && vin.any { it.isLetter() }) return vin
        }
        return ""
    }
}
