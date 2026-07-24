package com.jimmer.mscout

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.WindowManager
import android.webkit.CookieManager
import android.webkit.WebView
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.jimmer.mscout.export.Exporter
import com.jimmer.mscout.web.MarketplaceDriver
import com.jimmer.mscout.web.NotLoggedInException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView
    private lateinit var status: TextView
    private lateinit var progress: ProgressBar
    private lateinit var btnRun: Button
    private lateinit var btnShare: Button

    private lateinit var driver: MarketplaceDriver
    private var sweepJob: Job? = null
    private var lastExport: File? = null

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        web = findViewById(R.id.web)
        status = findViewById(R.id.status)
        progress = findViewById(R.id.progress)
        btnRun = findViewById(R.id.btnRun)
        btnShare = findViewById(R.id.btnShare)

        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            // A mobile-Chrome UA keeps Facebook on the normal m-site markup.
            userAgentString = userAgentString.replace("; wv", "")
        }
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true)
        driver = MarketplaceDriver(web)

        findViewById<Button>(R.id.btnLogin).setOnClickListener {
            web.loadUrl("https://www.facebook.com/")
            status.text = "Log in, then come back and tap Run sweep."
        }

        btnRun.setOnClickListener {
            if (sweepJob?.isActive == true) stopSweep() else startSweep()
        }

        btnShare.setOnClickListener {
            lastExport?.let { Exporter.share(this, it) }
        }
    }

    private fun startSweep() {
        btnRun.setText(R.string.btn_stop)
        progress.visibility = ProgressBar.VISIBLE
        progress.isIndeterminate = true
        // WebViews pause off-screen, so the sweep only runs while visible.
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        sweepJob = lifecycleScope.launch {
            try {
                val result = ScoutController(driver, this@MainActivity)
                    .runSweep { msg -> status.text = msg }
                lastExport = result.file
                btnShare.isEnabled = true
                status.text = "Done: ${result.dealCount} deals (of ${result.totalFound} " +
                    "found) ≥${com.jimmer.mscout.core.Config.Filters.dealThresholdPct}% " +
                    "below northern-US comps. Tap Share results."
            } catch (e: CancellationException) {
                throw e // user-requested Stop — stopSweep() already set the status
            } catch (e: NotLoggedInException) {
                status.text = e.message
            } catch (e: Exception) {
                status.text = "Sweep failed: ${e.javaClass.simpleName}: ${e.message}"
            } finally {
                sweepDone()
            }
        }
    }

    private fun stopSweep() {
        sweepJob?.cancel()
        status.text = "Stopped."
        sweepDone()
    }

    private fun sweepDone() {
        btnRun.setText(R.string.btn_run)
        progress.visibility = ProgressBar.GONE
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }
}
