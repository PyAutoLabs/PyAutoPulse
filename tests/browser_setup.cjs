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
    // Major sections start collapsed (PyAutoBrain#490); nav cards reveal them.
    assert.deepEqual(
      await page
        .locator("details.board-section")
        .evaluateAll((nodes) => nodes.map((node) => node.open)),
      [false, false],
    );
    assert.equal(await page.locator("[data-open]").first().isVisible(), false);
    await page.locator('.board-nav-card[href="#campaigns"]').click();
    await page.waitForFunction(
      () =>
        document.getElementById("campaigns").closest("details.board-section")
          .open,
    );
    await page.locator("[data-open]").first().click();
    assert.equal(await page.locator(".campaign-detail[open]").count(), 1);
    await page.locator('.board-nav-card[href="#evidence"]').click();
    await page.waitForFunction(
      () =>
        document.getElementById("evidence").closest("details.board-section")
          .open,
    );
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
    // Legacy batch semantics and different methods must retain separate bar scales.
    await page.goto(base + "/grouping.html#" + new URL(selected).hash.slice(1));
    await root.locator(".metric-value").first().waitFor();
    const runtimePanel = root.locator('.metric-panel[data-axis="runtime"]');
    assert.equal(await runtimePanel.locator(".metric-list").count(), 4);
    assert.match(await runtimePanel.innerText(), /Batch wall time/);
    assert.match(await runtimePanel.innerText(), /Per-replica batch cost/);
    assert.equal(
      await runtimePanel
        .locator(".metric-meta")
        .filter({ hasText: /Single-call observations/ })
        .count(),
      2,
    );
    assert.deepEqual(
      await runtimePanel
        .locator(".bar")
        .evaluateAll((ns) => ns.map((n) => n.style.width)),
      ["100%", "100%", "100%", "100%"],
    );
    await root
      .locator('.measurement-choice button[data-axis="memory"]')
      .click();
    await root
      .getByText("No recorded runs for this measurement.", { exact: false })
      .waitFor();
    assert.equal(await root.locator(".metric-value").count(), 0);
    // Real captured evidence: no reference candidate must still show useful values.
    const realURL = (params, file = "measurements.html") =>
      base +
      "/" +
      file +
      "#" +
      new URLSearchParams({
        instance: "lens",
        dataset: "imaging",
        instrument: "hst",
        ...params,
      });
    const ready = async () =>
      page.waitForFunction(() => {
        const results = document.querySelector(
          '[data-setup-browser="lens"] [data-id="results"]',
        );
        return (
          results &&
          results.querySelector('[data-id="configuration"]') &&
          !results.hasAttribute("aria-busy")
        );
      });
    for (const model of ["mge", "rectangular"]) {
      await page.goto(realURL({ model }));
      await ready();
      assert(
        await root
          .locator('.metric-panel[data-axis="runtime"][open] .metric-value')
          .count(),
      );
      assert.equal(await root.locator(".measurement-choice button").count(), 4);
      for (const axis of ["breakdown", "compile", "memory", "runtime"]) {
        await root
          .locator('.measurement-choice button[data-axis="' + axis + '"]')
          .click();
        const available = real.catalogue.evidence_shards.some(
          (m) =>
            m.setup_id.startsWith("imaging/" + model + "/hst/") &&
            m.axes.includes(axis),
        );
        if (!available) {
          await root
            .getByText("No recorded runs for this measurement.", {
              exact: false,
            })
            .waitFor();
          assert.equal(await root.locator(".metric-value").count(), 0);
          continue;
        }
        await ready();
        const id = await root.locator('[data-id="configuration"]').inputValue();
        const manifest = real.catalogue.evidence_shards.find(
          (m) => m.setup_id === id,
        );
        assert(manifest.axes.includes(axis));
        assert(
          await root
            .locator(
              '.metric-panel[data-axis="' + axis + '"][open] .metric-value',
            )
            .count(),
        );
        const shard = JSON.parse(real.shards[manifest.path]);
        const values = await root
          .locator(".metric-value")
          .evaluateAll((nodes) =>
            nodes.map((n) => n.dataset.value + " " + n.dataset.unit),
          );
        assert.deepEqual(
          values.sort(),
          shard.records
            .map((r) => String(r.measurement[r.metric]) + " " + r.unit)
            .sort(),
        );
      }
      // Preserve a compatible device filter when choosing another run.
      const device = await root
        .locator('[data-id="device"] option')
        .nth(1)
        .getAttribute("value");
      await root.locator('[data-id="device"]').selectOption(device);
      await ready();
      const options = await root
        .locator('[data-id="configuration"] option')
        .evaluateAll((ns) => ns.map((n) => n.value));
      assert(options.length >= 2);
      await root.locator('[data-id="configuration"]').selectOption(options[1]);
      await ready();
      assert.equal(
        await root.locator('[data-id="device"]').inputValue(),
        device,
      );
      assert.equal(new URL(page.url()).hash.includes("device=" + device), true);
      assert.equal(
        await root.locator(".related-hazards").count(),
        model === "rectangular" ? 1 : 0,
      );
      assert.equal(await root.locator(".shared-hazards").count(), 1);
      const guidance = root.locator("details").filter({
        has: page.locator("summary", {
          hasText: /^Hazards and setup guidance$/,
        }),
      });
      await guidance.locator(":scope > summary").click();
      assert.match(
        await guidance.innerText(),
        /not evidence that it is hazard-free/,
      );
      await root.locator(".shared-hazards > summary").click();
      assert.match(
        await root.locator(".shared-hazards").innerText(),
        /does not establish/,
      );
      for (const width of [320, 390, 768, 1280]) {
        await page.setViewportSize({ width, height: 1000 });
        assert(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth + 1,
          ),
          `real ${model} overflow ${width}`,
        );
      }
      const before = page.url();
      await root
        .locator('.measurement-choice button[data-axis="breakdown"]')
        .focus();
      await page.keyboard.press("Enter");
      await ready();
      await page.goBack();
      await ready();
      assert.equal(page.url(), before);
    }
    const breakdown = real.catalogue.evidence_shards.find(
      (m) =>
        m.setup_id.startsWith("imaging/mge/") &&
        m.axes.includes("breakdown") &&
        !m.axes.includes("runtime"),
    );
    await page.goto(realURL({ model: "mge", setup: breakdown.setup_id }));
    await ready();
    assert(
      await root
        .locator('.metric-panel[data-axis="breakdown"][open] .metric-value')
        .count(),
    );
    assert.equal(
      await root.locator('[data-id="configuration"]').inputValue(),
      breakdown.setup_id,
    );
    await root.locator('.metric-panel[data-axis="runtime"] > summary').click();
    assert.match(
      await root.locator('.metric-panel[data-axis="runtime"]').innerText(),
      /other runs contain/,
    );
    const cpuBreakdown = real.catalogue.evidence_shards.find(
      (m) =>
        m.setup_id.startsWith("imaging/rectangular/") &&
        m.axis_devices.breakdown?.includes("cpu"),
    );
    await page.goto(
      realURL({
        model: "rectangular",
        setup: cpuBreakdown.setup_id,
        axis: "breakdown",
        device: "a100",
      }),
    );
    await root
      .getByText("The linked run does not record this measurement", {
        exact: false,
      })
      .waitFor();
    assert.equal(await root.locator(".metric-value").count(), 0);
    await root
      .getByRole("button", {
        name: "Open the exact run without the device filter",
      })
      .click();
    await ready();
    assert.equal(
      await root.locator('[data-id="configuration"]').inputValue(),
      cpuBreakdown.setup_id,
    );
    // Unknown device is never silently replaced with another run.
    await page.goto(realURL({ model: "mge", device: "not-recorded" }));
    await root
      .getByText("No recorded device matches this link.", { exact: false })
      .waitFor();
    assert.equal(await root.locator(".metric-value").count(), 0);
    await root
      .locator('.measurement-choice button[data-axis="runtime"]')
      .click();
    await ready();
    // Optional producer metadata: older captures retain working evidence navigation.
    await page.goto(realURL({ model: "mge" }, "legacy-devices.html"));
    await ready();
    assert(await root.locator(".metric-panel[open] .metric-value").count());
    await page.goto(realURL({ model: "mge" }, "unknown-axes.html"));
    await ready();
    assert(await root.locator(".metric-panel[open] .metric-value").count());
    assert.match(
      await root.locator(".measurement-overview").innerText(),
      /no axis summary/,
    );
    assert.deepEqual(errors, []);
    await context.close();
    const nojs = await browser.newContext({ javaScriptEnabled: false });
    const fallback = await nojs.newPage();
    await fallback.goto(base);
    // Native disclosures still open without JavaScript.
    await fallback
      .locator("details.board-section:has(#evidence) > summary")
      .click();
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
      "PASS: real MGE/rectangular axis navigation, exact values, absent memory, device persistence, qualified hazards, exact-link recovery, older metadata; pinned shards, hash refusal/retry, stale links, race, multi-project history, inline v2, clipboard, campaign routing, responsive light/dark, no-JS",
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
