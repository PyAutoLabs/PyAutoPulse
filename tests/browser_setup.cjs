// npm install --no-save --no-package-lock playwright@1.63.0
// npx playwright install chromium && node tests/browser_setup.cjs
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
        if (delay) await new Promise((resolve) => setTimeout(resolve, 250));
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
    await detail.locator('[data-axis="breakdown"] > summary').click();
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
    // Hash mismatch must never display measurements; retry re-verifies immutable bytes.
    corrupt = true;
    await page.goto(modelURL());
    await page.waitForSelector(".status-error");
    assert.equal(await page.locator(".metric-value").count(), 0);
    corrupt = false;
    await page.getByRole("button", { name: "Retry evidence" }).click();
    await page.waitForSelector(".metric-value", { state: "attached" });
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
    await page.locator('[data-axis="breakdown"] > summary').click();
    await page.waitForFunction(
      (old) =>
        document.querySelector('[data-id="configuration"]').value !== old,
      before,
    );
    await loaded();
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
