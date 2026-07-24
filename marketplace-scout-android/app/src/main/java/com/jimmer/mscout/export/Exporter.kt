package com.jimmer.mscout.export

import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import com.jimmer.mscout.core.Listing
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object Exporter {

    // Requested fields first, decision-support fields after (same as desktop).
    private val HEADER = listOf(
        "Make", "Model", "Year", "Mileage", "Clean Carfax", "URL",
        "Avg Resale Price (Northern US)", "Asking Price", "Below Market $",
        "Below Market %", "Location", "Category", "Comps Used", "Notes",
    )

    fun writeXlsx(context: Context, listings: List<Listing>): File {
        val sorted = listings.sortedWith(
            compareBy({ it.belowMarketPct == null }, { -(it.belowMarketPct ?: 0.0) })
        )
        val rows = sorted.map { l ->
            val notes = (listOf(l.titleNotes) + l.notes).filter { it.isNotEmpty() }
            listOf(
                l.make.ifEmpty { "?" }, l.model.ifEmpty { l.title.take(28) },
                l.year, l.mileage, l.cleanCarfax, l.url, l.avgResaleNorth,
                l.askingPrice, l.belowMarket, l.belowMarketPct, l.location,
                l.category, if (l.compCount > 0) l.compCount else null,
                notes.joinToString("; "),
            )
        }

        val dir = File(context.filesDir, "exports").apply { mkdirs() }
        val stamp = SimpleDateFormat("yyyyMMdd-HHmm", Locale.US).format(Date())
        val file = File(dir, "deals-$stamp.xlsx")
        MiniXlsx.write(file, HEADER, rows)
        return file
    }

    /** Share sheet — pick Google Sheets/Drive to land it as a Google spreadsheet. */
    fun share(context: Context, file: File) {
        val uri = FileProvider.getUriForFile(context, "com.jimmer.mscout.files", file)
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_SUBJECT, file.name)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, "Share deals spreadsheet"))
    }
}
