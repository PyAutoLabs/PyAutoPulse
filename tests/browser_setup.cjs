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
      const file = path.join(dir, req.url === "/" ? "index.html" : req.url);
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
    let corrupt = false,
      delay = false,
      requests = [];
    await context.route(
      "https://raw.githubusercontent.com/**",
      async (route) => {
        const url = route.request().url();
        requests.push(url);
        assert(
          url.includes("/" + "b".repeat(40) + "/dashboard/catalogue/shards/"),
        );
        if (delay) await new Promise((resolve) => setTimeout(resolve, 250));
        await route.fulfill({
          contentType: "application/json",
          body: corrupt
            ? "{}"
            : fs.readFileSync(
                path.join(dir, "catalogue/shards/" + "a".repeat(20) + ".json"),
              ),
        });
      },
    );
    const root = page.locator('[data-setup-browser="lens"]');
    async function choose(target = root) {
      await target.locator('[data-id="project-picker"] > summary').click();
      await target.locator('[data-family="imaging"] > summary').click();
      await target.locator('[data-model="delaunay"]').focus();
      await page.keyboard.press("Enter");
    }
    await page.goto(base);
    assert.equal(await page.locator('[data-id="results"]:visible').count(), 0);
    assert.equal(await page.locator(".campaign-detail[open]").count(), 0);
    await page.evaluate(() =>
      Object.defineProperty(navigator, "clipboard", {
        value: {
          writeText: async (text) => {
            window.copied = text;
          },
        },
        configurable: true,
      }),
    );
    await page
      .getByRole("button", {
        name: "Fix Profiling Systematically",
        exact: true,
      })
      .click();
    await page.waitForFunction(
      () => window.copied === document.querySelector("#fix-prompt").value,
    );
    // Explicit clipboard rejection must expose the edited prompt for manual copying.
    await page.evaluate(() =>
      Object.defineProperty(navigator, "clipboard", {
        value: { writeText: () => Promise.reject(Error("denied")) },
        configurable: true,
      }),
    );
    // The domain fix prompt keeps its own editable field and manual fallback.
    await page.locator("#fix-details").evaluate((el) => (el.open = true));
    await page.locator("#fix-prompt").fill("Edited fix prompt");
    await page
      .getByRole("button", {
        name: "Fix Profiling Systematically",
        exact: true,
      })
      .click();
    await page.waitForFunction(() =>
      document
        .querySelector("#copy-status")
        .textContent.includes("Select and copy"),
    );
    assert.equal(
      await page.locator("#fix-prompt").inputValue(),
      "Edited fix prompt",
    );
    await page.locator("#fix-details").evaluate((el) => (el.open = false));
    // The check-in prompt now lives in the shared orchestration panel: the
    // user's direction is appended to the exact preview, and a rejected
    // clipboard opens and selects that preview for manual copying.
    const panel = page.locator("#orchestration-pulse");
    assert.equal(
      await panel.locator("[data-orchestration-preview][open]").count(),
      0,
    );
    await panel
      .locator("[data-orchestration-direction]")
      .fill("Edited check-in direction");
    await panel
      .getByRole("button", { name: "Profiling Check In", exact: true })
      .click();
    await page.waitForFunction(
      () =>
        document.querySelector("#orchestration-pulse .orchestration-status")
          .textContent !== "",
    );
    assert.equal(
      await panel.locator("[data-orchestration-preview][open]").count(),
      1,
    );
    const preview = await panel
      .locator("[data-orchestration-prompt]")
      .inputValue();
    const owner = await panel
      .locator("[data-orchestration-prompt]")
      .evaluate((el) => el.defaultValue);
    assert(owner.startsWith("Use PyAutoPulse as the home"), owner.slice(0, 80));
    assert.equal(
      preview,
      owner +
        "\n\nOptional direction (user context):\nEdited check-in direction",
    );
    assert(
      await page.evaluate(
        () =>
          document.activeElement ===
          document.querySelector("#orchestration-pulse-prompt"),
      ),
    );
    await panel
      .locator("[data-orchestration-preview]")
      .evaluate((el) => (el.open = false));
    await page.locator("[data-open]").first().click();
    assert.equal(await page.locator(".campaign-detail[open]").count(), 1);
    await choose();
    await root.locator(".metric-value").first().waitFor();
    assert.equal(
      await root.locator(".metric-value").first().getAttribute("data-value"),
      "0.05",
    );
    assert(requests.length > 0);
    assert.equal(await root.locator(".metric-panel[open]").count(), 1);
    assert.equal(
      await root.locator('[data-id="configuration"] option').count(),
      1,
    );
    const selected = page.url();
    await choose(page.locator('[data-setup-browser="galaxy"]'));
    await page
      .locator('[data-setup-browser="galaxy"] .metric-value')
      .first()
      .waitFor();
    assert.equal(await root.locator('[data-id="results"]:visible').count(), 0);
    await page.goBack();
    await root.locator(".metric-value").first().waitFor();
    assert.equal(
      await page
        .locator('[data-setup-browser="galaxy"] [data-id="results"]:visible')
        .count(),
      0,
    );
    await page.goto(selected.replace(/setup=[^&]+/, "setup=missing-setup"));
    await root
      .getByText(
        "This linked configuration is not in the published catalogue.",
        { exact: false },
      )
      .waitFor();
    assert.equal(await root.locator(".metric-value").count(), 0);
    corrupt = true;
    await page.goto(selected);
    await page.reload();
    await root.getByRole("button", { name: "Retry evidence" }).waitFor();
    assert.equal(await root.locator(".metric-value").count(), 0);
    corrupt = false;
    await root.getByRole("button", { name: "Retry evidence" }).click();
    await root.locator(".metric-value").first().waitFor();
    delay = true;
    await page.goto(selected);
    await page.reload();
    await page.evaluate(() => {
      location.hash = "";
    });
    await page.waitForTimeout(400);
    assert.equal(await root.locator('[data-id="results"]:visible').count(), 0);
    delay = false;
    await page.goto(base + "/inline.html#" + new URL(selected).hash.slice(1));
    await root.locator(".metric-value").first().waitFor();
    // Configuration metadata, values, and native controls must fit narrow screens.
    for (const width of [390, 760, 1280])
      for (const colorScheme of ["light", "dark"]) {
        await page.setViewportSize({ width, height: 1000 });
        await page.emulateMedia({ colorScheme });
        assert(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth + 1,
          ),
          `overflow at ${width}/${colorScheme}`,
        );
      }
    assert.deepEqual(errors, []);
    await context.close();
    const nojs = await browser.newContext({ javaScriptEnabled: false });
    const fallback = await nojs.newPage();
    await fallback.goto(base);
    await fallback
      .getByText("Original setup evidence (JavaScript disabled)", {
        exact: true,
      })
      .first()
      .click();
    assert(
      await fallback
        .getByRole("link", { name: /results\/fixture.json/ })
        .first()
        .isVisible(),
    );
    await nojs.close();
    console.log(
      "PASS: pinned shards, hash refusal/retry, stale links, race, multi-project history, inline v2, clipboard, campaign routing, responsive light/dark, no-JS",
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
