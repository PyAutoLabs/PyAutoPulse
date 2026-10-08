// npm install --no-save --no-package-lock playwright@1.63.0
// npx playwright install chromium && node tests/browser_setup.cjs
require("./measurement_presentation.cjs");
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const os = require("node:os");
const { execFileSync } = require("node:child_process");
(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "pulse-browser-"));
  execFileSync("python", ["tests/browser_fixture.py", dir]);
  const server = http.createServer((req, res) => {
    try {
      const file = path.join(
        dir,
        new URL(req.url, "http://localhost").pathname === "/"
          ? "index.html"
          : new URL(req.url, "http://localhost").pathname,
      );
      res.setHeader(
        "Content-Type",
        file.endsWith(".json") ? "application/json" : "text/html",
      );
      res.end(fs.readFileSync(file));
    } catch {
      res.writeHead(404);
      res.end();
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const base = "http://127.0.0.1:" + server.address().port;
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1280, height: 1000 },
    });
    const page = await context.newPage(),
      errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const real = JSON.parse(
      fs.readFileSync("tests/fixtures/browser_measurements.json"),
    );
    let corrupt = false,
      delay = false,
      releaseDelayed,
      requests = [];
    await context.route(
      "https://raw.githubusercontent.com/**",
      async (route) => {
        const url = route.request().url();
        requests.push(url);
        assert(
          ["b".repeat(40), real.capture_commit].some((commit) =>
            url.includes("/" + commit + "/dashboard/catalogue/shards/"),
          ),
        );
        if (delay && url.endsWith("/" + "1".repeat(20) + ".json"))
          await new Promise((resolve) => {
            releaseDelayed = resolve;
          });
        await route.fulfill({
          contentType: "application/json",
          body: corrupt
            ? "{}"
            : fs.readFileSync(
                path.join(
                  dir,
                  "catalogue/shards/" + new URL(url).pathname.split("/").at(-1),
                ),
              ),
        });
      },
    );
    const root = page.locator('[data-setup-browser="lens"]');
    async function loaded(target = page) {
      await target.waitForFunction(
        () => !document.querySelector('[aria-busy="true"]'),
      );
    }
    const modelURL = (file = "/", extra = {}) =>
      base +
      file +
      "?view=model#" +
      new URLSearchParams({
        instance: "lens",
        dataset: "imaging",
        model: "delaunay",
        ...extra,
      });
    const headlineValue = (target, id) =>
      target.locator(`[data-headline="${id}"] .headline-value`);
    await page.goto(base);
    assert.equal(
      await page
        .getByRole("button", { name: "Fix Profiling Systematically" })
        .count(),
      0,
    );
    assert.equal(await page.locator(".capture-details").count(), 0);
    await page.locator('a[href="#evidence"]').first().click();
    await root.locator('[data-id="project-picker"] > summary').click();
    await root.locator('[data-family="imaging"] > summary').click();
    const popupEvent = context.waitForEvent("page");
    await root.locator('[data-model="delaunay"]').click();
    const detail = await popupEvent;
    await detail.waitForLoadState();
    await detail.waitForSelector(".metric-value", { state: "attached" });
    await loaded(detail);
    assert(detail.url().includes("view=model"));
    assert.equal(await page.locator('[data-id="results"]:visible').count(), 0);
    assert.equal(
      await detail.locator('[data-id="results"]:visible').count(),
      1,
    );
    assert.equal(await detail.locator(".board-nav:visible").count(), 0);
    assert.equal(
      await detail.locator("#orchestration-pulse:visible").count(),
      0,
    );
    assert.equal(
      await detail.locator('[data-id="navigation"]:visible').count(),
      0,
    );
    assert.deepEqual(
      await detail
        .locator(".selectors > label")
        .evaluateAll((els) => els.map((e) => e.firstChild.textContent)),
      ["Instrument", "Device", "Configuration"],
    );
    assert.equal(
      await detail.locator(".selectors + .headline-metrics").count(),
      1,
    );
    assert.equal(await headlineValue(detail, "total").textContent(), "0.05 s");
    assert(await headlineValue(detail, "total").isVisible());
    assert.equal(
      await headlineValue(detail, "vram").textContent(),
      "Not measured yet",
    );
    assert.equal(
      await detail
        .locator('[data-id="configuration"] option:checked')
        .textContent(),
      "1500 source pixels - float64",
    );
    assert.equal(
      await detail
        .locator('[data-id="results"] > details > summary')
        .first()
        .textContent(),
      "Configuration details",
    );
    const detailText = await detail
      .locator('[data-id="results"]:visible')
      .textContent();
    for (const absent of [
      "Browse recorded runs",
      "Statistic not recorded",
      "Component observations",
      "Qualification and measurement method",
      "Shared component and method findings",
      "Browse Likelihood",
    ])
      assert(!detailText.includes(absent), absent);
    assert(
      detailText.includes("Profiling Results") &&
        detailText.includes("Profiling scripts"),
    );
    assert.equal(await detail.locator(".measurement-choices").count(), 0);
    // Capture URL state in the same task as activation: a user can reload or
    // copy the link before the browser delivers its queued details toggle event.
    const activated = await detail
      .locator('[data-axis="breakdown"] > summary')
      .evaluate((summary) => {
        summary.click();
        return {
          open: summary.parentElement.open,
          axis: new URLSearchParams(location.hash.slice(1)).get("axis"),
        };
      });
    assert.deepEqual(activated, { open: true, axis: "breakdown" });
    const componentBar = detail.locator('[data-axis="breakdown"] .bar').first();
    assert.equal(
      await componentBar.getAttribute("data-scale"),
      "Full likelihood",
    );
    assert.equal(await componentBar.evaluate((el) => el.style.width), "40%");
    await detail.reload();
    await detail.waitForSelector(".metric-value", { state: "attached" });
    assert.equal(
      await detail.locator('[data-axis="breakdown"]').getAttribute("open"),
      "",
    );
    // Native summary keyboard activation must persist the same route too.
    const memorySummary = detail.locator('[data-axis="memory"] > summary');
    await memorySummary.focus();
    await detail.keyboard.press("Enter");
    assert.equal(
      new URLSearchParams(new URL(detail.url()).hash.slice(1)).get("axis"),
      "memory",
    );
    await memorySummary.focus();
    await detail.keyboard.press("Enter");
    assert.equal(
      await detail.locator('[data-axis="memory"]').getAttribute("open"),
      null,
    );
    const breakdownSummary = detail.locator(
      '[data-axis="breakdown"] > summary',
    );
    await breakdownSummary.focus();
    await detail.keyboard.press("Enter");
    await detail.keyboard.press("Enter");
    assert.equal(
      new URLSearchParams(new URL(detail.url()).hash.slice(1)).get("axis"),
      "breakdown",
    );
    // Narrow view and desktop, light and dark, must keep controls inside the viewport.
    for (const width of [390, 768, 820, 1024, 1440]) {
      await detail.setViewportSize({ width, height: 900 });
      for (const colorScheme of ["light", "dark"]) {
        await detail.emulateMedia({ colorScheme });
        assert(
          await detail.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          `overflow ${width} ${colorScheme}`,
        );
      }
    }
    fs.mkdirSync("tmp/browser", { recursive: true });
    await detail.screenshot({ path: "tmp/browser/model.png", fullPage: true });
    await detail.close();

    // Inline evidence, incompatible method statistics and units keep separate scales.
    await page.goto(modelURL("/inline.html"));
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert.equal(await page.locator(".metric-value").count(), 4);
    await page.goto(modelURL("/grouping.html"));
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert.equal(
      await page.locator('[data-axis="runtime"] .metric-list').count(),
      4,
    );
    await page.goto(modelURL("/scaling.html"));
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert.deepEqual(
      await page
        .locator('[data-axis="runtime"] .bar')
        .evaluateAll((els) => els.map((e) => e.style.width)),
      ["100%", "50%"],
    );
    assert.deepEqual(
      await page
        .locator('[data-axis="breakdown"] .bar')
        .evaluateAll((els) => els.map((e) => e.style.width)),
      ["40%", "20%"],
    );
    assert.match(
      await headlineValue(page, "total").textContent(),
      /Multiple runs/,
    );

    // All headline fields are visible and are replaced when any selector changes.
    await page.goto(modelURL("/headlines.html"));
    assert.equal(await headlineValue(page, "total").textContent(), "0.05 s");
    assert.equal(await headlineValue(page, "batched").textContent(), "0.005 s");
    assert.match(
      await page.locator('[data-headline="batched"]').textContent(),
      /batch size 16/,
    );
    assert.equal(await headlineValue(page, "vram").textContent(), "2 GB");
    assert.match(
      await page.locator('[data-headline="memory"]').textContent(),
      /Peak host RSS/,
    );
    assert(await page.locator('[data-headline="total"] a').isVisible());
    await page.selectOption('[data-id="device"]', "gpu");
    assert.equal(await headlineValue(page, "total").textContent(), "0.1 s");
    assert.equal(await headlineValue(page, "vram").textContent(), "4 GB");
    await page.selectOption('[data-id="device"]', "cpu");
    const configLabels = await page
      .locator('[data-id="configuration"] option')
      .allTextContents();
    assert.equal(new Set(configLabels).size, configLabels.length);
    assert(configLabels.every((text) => !text.includes("Runtime")));
    await page.selectOption('[data-id="configuration"]', "compile-only");
    assert.equal(await headlineValue(page, "compile").textContent(), "7 s");
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Not measured yet",
    );
    assert.equal(
      await headlineValue(page, "memory").textContent(),
      "Not measured yet",
    );
    await page.selectOption('[data-id="instrument"]', "euclid");
    assert.equal(await headlineValue(page, "total").textContent(), "0.25 s");
    assert.equal(
      await headlineValue(page, "compile").textContent(),
      "Not measured yet",
    );
    await page.goto(
      modelURL("/headlines.html", {
        model: "unmeasured",
        implementation: "jax",
      }),
    );
    assert.equal(await page.locator(".headline-row").count(), 5);
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Not measured yet",
    );

    // A late response from the previous selection cannot overwrite a newer one.
    delay = true;
    await page.goto(modelURL("/async-headlines.html"));
    assert.equal(await headlineValue(page, "total").textContent(), "Loading…");
    await page.selectOption('[data-id="configuration"]', "compile-only");
    await loaded();
    assert.equal(await headlineValue(page, "compile").textContent(), "7 s");
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Not measured yet",
    );
    const lateResponse = page.waitForResponse((response) =>
      response.url().endsWith("/" + "1".repeat(20) + ".json"),
    );
    assert(releaseDelayed, "first shard request was held");
    releaseDelayed();
    await (await lateResponse).finished();
    // Allow the obsolete response's digest and render continuation to finish.
    await page.waitForTimeout(100);
    assert.equal(await headlineValue(page, "compile").textContent(), "7 s");
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Not measured yet",
    );
    delay = false;
    // Hash mismatch must never display measurements; retry re-verifies immutable bytes.
    corrupt = true;
    await page.goto(modelURL());
    await page.waitForSelector(".status-error");
    assert.equal(await page.locator(".metric-value").count(), 0);
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Evidence unavailable",
    );
    assert.equal(await page.locator(".headline-value[data-value]").count(), 0);
    corrupt = false;
    await page.getByRole("button", { name: "Retry evidence" }).click();
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert.equal(await headlineValue(page, "total").textContent(), "0.05 s");
    assert(
      requests.every((url) => url.includes("/dashboard/catalogue/shards/")),
    );
    // Invalid explicit setup links never silently substitute a different run.
    await page.goto(modelURL("/", { setup: "missing" }));
    assert(
      (
        await page.locator('[data-id="results"]:visible').textContent()
      ).includes("No substitute"),
    );
    assert.equal(await page.locator(".metric-value").count(), 0);

    // Retain all captures, while only float64/1500 normal defaults appear.
    await page.goto(modelURL("/filtering.html"));
    await page.waitForSelector(".metric-value", { state: "attached" });
    const options = await page
      .locator('[data-id="configuration"] option')
      .evaluateAll((els) => els.map((e) => e.value));
    assert.deepEqual(options, ["imaging/delaunay/hst/reference"]);
    await page.selectOption('[data-id="device"]', "a100");
    await loaded();
    assert.equal(await page.locator(".metric-value").count(), 0);
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Not measured yet",
    );
    assert(
      (await page.locator(".empty").first().textContent()).includes(
        "No float64 results",
      ),
    );
    await page.goto(
      modelURL("/filtering.html", { setup: "archived-float32", device: "cpu" }),
    );
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert.equal(
      await page
        .locator('[data-id="configuration"] option:checked')
        .textContent(),
      "Archived configuration (linked)",
    );
    // Real captures: default config counts are bounded; section navigation changes
    // the selected configuration rather than merging unrelated measurements.
    await page.goto(
      base +
        "/measurements.html?view=model#" +
        new URLSearchParams({
          instance: "lens",
          dataset: "imaging",
          model: "mge",
          instrument: "hst",
        }),
    );
    await page.waitForSelector(".metric-value", { state: "attached" });
    await loaded();
    assert(
      (await page.locator('[data-id="configuration"] option').count()) <= 4,
    );
    const before = await page.locator('[data-id="configuration"]').inputValue();
    assert.equal(
      await headlineValue(page, "total").getAttribute("data-value"),
      "0.11771118000033312",
    );
    assert.equal(
      await headlineValue(page, "batched").getAttribute("data-unit"),
      "s",
    );
    await page.locator('[data-axis="breakdown"] > summary').click();
    await page.waitForFunction(
      (old) =>
        document.querySelector('[data-id="configuration"]').value !== old,
      before,
    );
    await loaded();
    assert.equal(
      await headlineValue(page, "total").textContent(),
      "Not measured yet",
    );
    assert.equal(
      await page.locator('[data-axis="breakdown"] .metric-value').count(),
      1,
    );
    assert(
      (
        await page
          .locator('[data-id="configuration"] option:checked')
          .textContent()
      ).includes("float64"),
    );
    fs.mkdirSync("tmp/browser", { recursive: true });
    await page
      .locator('[data-axis="breakdown"]')
      .evaluate((e) => (e.open = true));
    await page.screenshot({
      path: "tmp/browser/real-breakdown.png",
      fullPage: true,
    });
    await page.goto(
      base +
        "/readable.html?view=model#instance=lens&dataset=imaging&model=delaunay&axis=breakdown",
    );
    await page.waitForSelector(".metric-value", { state: "attached" });
    const mainRows = page.locator(
      '[data-axis="breakdown"] > .metric-list > .metric-row',
    );
    assert.deepEqual(
      await mainRows.evaluateAll((rows) => rows.map((r) => r.dataset.metric)),
      [
        "component_total",
        "steps.Curvature matrix (F)",
        "steps.Regularized reconstruction",
        "steps.Data vector (D)",
      ],
    );
    assert.deepEqual(
      await mainRows
        .locator(".bar")
        .evaluateAll((bars) => bars.map((b) => b.style.width)),
      ["100%", "50%", "30%", "10%"],
    );
    assert.equal(
      await page.locator(".timing-diagnostics").getAttribute("open"),
      null,
    );
    assert.equal(
      await page.locator(".timing-diagnostics .metric-row").count(),
      2,
    );
    assert(
      (await mainRows.nth(2).textContent()).includes(
        "Solve for the source brightness",
      ),
    );
    assert.equal(
      await page.locator('a[href*="likelihood_runtime_numba.py"]').count(),
      0,
    );
    await page.reload();
    assert(
      (await page.locator('[data-axis="breakdown"]').getAttribute("open")) !==
        null,
    );
    await page.goto(
      base +
        "/readable.html?view=model#instance=lens&dataset=imaging&model=delaunay&implementation=numba",
    );
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert(
      (await page.locator('[data-id="results"] h2').textContent()).includes(
        "Delaunay (Numba)",
      ),
    );
    assert.equal(
      await page.locator('[data-id="configuration"] option').count(),
      1,
    );
    assert.equal(
      await page.locator('[data-id="configuration"]').inputValue(),
      "numba-cpu",
    );
    assert.equal(
      await page.locator('a[href$="likelihood_runtime.py"]').count(),
      0,
    );
    assert.equal(
      await page.locator('a[href$="likelihood_runtime_numba.py"]').count(),
      1,
    );
    assert.equal(
      await page.locator(".metric-value").getAttribute("data-value"),
      "0.4",
    );
    assert.equal(await headlineValue(page, "total").textContent(), "0.4 s");
    assert.equal(
      await headlineValue(page, "batched").textContent(),
      "Not applicable",
    );
    assert.equal(
      await page
        .locator('[data-headline="compile"], [data-headline="vram"]')
        .count(),
      0,
    );
    await page.goto(
      base +
        "/readable.html?view=model#instance=lens&dataset=imaging&model=delaunay&setup=numba-cpu",
    );
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert(
      new URLSearchParams(new URL(page.url()).hash.slice(1)).get(
        "implementation",
      ) === "numba",
    );
    await page.goto(base + "/menu-order.html");
    assert.deepEqual(
      await page.locator('[data-family="imaging"] .model-choice').allTextContents(),
      ["Delaunay (JAX)", "Delaunay (Numba)", "Rectangular (JAX)", "Rectangular (Numba)",
       "MGE (JAX)", "MGE (Numba)", "KNN (JAX)", "KNN (Numba)",
       "MGE Mass (JAX)", "MGE Mass (Numba)", "Sersic"],
    );
    assert.equal(await page.locator('.model-choice[data-implementation="unknown"]').count(), 1);
    await page.goto(base + "/readable.html");
    assert.equal(
      await page.locator('a.model-choice[data-implementation="numba"]').count(),
      1,
    );
    assert.equal(
      await page.locator('a.model-choice[data-implementation="jax"]').count(),
      1,
    );
    assert.equal(
      await page
        .locator('a.model-choice[data-implementation="numba"]')
        .getAttribute("target"),
      "_blank",
    );
    await page.goto(
      base +
        "/diagnostic-isolation.html?view=model#instance=lens&dataset=imaging&model=delaunay&axis=breakdown",
    );
    await page.waitForSelector(".metric-value", { state: "attached" });
    assert.equal(
      await page
        .locator(
          '[data-axis="breakdown"] > .metric-list [data-metric="component_total"]',
        )
        .count(),
      0,
    );
    assert.equal(
      await page
        .locator(
          '[data-axis="breakdown"] > .metric-list [data-metric="reconstruction.jit.steady_per_call_s"]',
        )
        .count(),
      1,
    );
    assert(
      (await page.locator('[data-axis="breakdown"]').textContent()).includes(
        "Component total not recorded",
      ),
    );
    await page
      .locator('[data-metric="steps.Regularized reconstruction"] summary')
      .click();
    assert(
      await page
        .locator('[data-metric="steps.Regularized reconstruction"] code')
        .isVisible(),
    );
    for (const width of [390, 1280]) {
      await page.setViewportSize({ width, height: 1000 });
      assert(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      );
    }
    assert.deepEqual(errors, []);
    console.log(
      "Browser checks passed: new tabs, filtering, scales, transport, navigation and responsive layout",
    );
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(dir, { recursive: true, force: true });
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
