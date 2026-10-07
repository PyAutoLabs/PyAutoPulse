/* Pulse v2 reader UI; conventions shared with the project setup browser.
 * Consumes captured producer data only. No cross-setup joins or scientific judgement. */
(() => {
  "use strict";
  for (const root of document.querySelectorAll("[data-setup-browser]")) {
    const capture = JSON.parse(
      root.querySelector(".setup-payload").textContent,
    );
    const prefix = "setup-" + capture.instance + "-";
    const $ = (id) => root.querySelector('[data-id="' + id + '"]');
    const status = $("load-status"),
      nav = $("navigation"),
      results = $("results");
    const repo = capture.repo;
    let catalogue = capture.catalogue,
      state = {},
      generation = 0;
    const cache = new Map();
    const presentation = globalThis.PulsePresentation;
    // Use captured index evidence so loading a shard cannot move a setup into
    // another implementation or change the available navigation.
    const implementations = new Map(
      catalogue.setups.map((setup) => [
        setup.id,
        presentation.implementation(
          setup,
          catalogue.records.filter((r) => r.setup_id === setup.id),
        ),
      ]),
    );
    const implementationFor = (s) =>
      implementations.get(s.id) || presentation.implementation(s);
    const modelLabel = (model, implementation) =>
      label(model) +
      (implementation === "numba"
        ? " (Numba)"
        : implementation === "unknown"
          ? " (implementation unspecified)"
          : "");
    const axes = {
      runtime: "Runtime",
      breakdown: "Breakdown",
      compile: "Compilation",
      memory: "Memory",
    };
    const manifestFor = (s) =>
      (catalogue.evidence_shards || []).find((m) => m.setup_id === s.id);
    const recordsFor = (s) => {
      const manifest = manifestFor(s);
      return (
        cache.get(manifest?.sha256)?.records ||
        catalogue.records.filter((r) => r.setup_id === s.id)
      );
    };
    const axesFor = (s) =>
      manifestFor(s)?.axes || [...new Set(recordsFor(s).map((r) => r.axis))];
    const hasAxis = (s, axis) => axesFor(s).includes(axis);
    const devicesFor = (s, axis) =>
      manifestFor(s)?.axis_devices?.[axis] || [
        ...new Set(
          recordsFor(s)
            .filter((r) => r.axis === axis)
            .map((r) => r.identity.device || "unknown"),
        ),
      ];
    function chooseAxis(setup) {
      return (
        Object.keys(axes).find((axis) => hasAxis(setup, axis)) || "runtime"
      );
    }
    const names = {
      imaging: "Imaging",
      interferometer: "Interferometer",
      datacube: "Datacube",
      point_source_image: "Point source · image plane",
      point_source_source: "Point source · source plane",
      multi_dataset: "Multiple datasets",
      cluster: "Cluster",
      lens: "Lens components",
      experiments: "Other experiments",
    };
    const models = {
      delaunay: "Delaunay",
      rectangular: "Rectangular",
      mge: "MGE",
      delaunay_nn: "DelaunayNN",
      delaunay_matern: "Delaunay Matern",
      knn: "KNN",
      mge_mass: "MGE Mass",
      sersic: "Sersic",
    };
    const label = (value) =>
      models[value] ||
      names[value] ||
      String(value)
        .replaceAll("_", " ")
        .replace(/\bpixelized\b/gi, "")
        .trim()
        .replace(/\b[a-z]/g, (c) => c.toUpperCase())
        .replace(/\b(psf|cpu|gpu|jax|rss|nnls|jit|knn|mge)\b/gi, (word) =>
          word.toUpperCase(),
        );
    function node(tag, text, cls) {
      const el = document.createElement(tag);
      if (text !== undefined) el.textContent = text;
      if (cls) el.className = cls;
      return el;
    }
    function append(parent, tag, text, cls) {
      const el = node(tag, text, cls);
      parent.append(el);
      return el;
    }
    function source(path) {
      if (
        typeof path !== "string" ||
        path.split("/").some((p) => !p || p === "." || p === "..") ||
        /[\\:\x00-\x1f]/.test(path)
      )
        throw Error("Unsafe evidence path");
      return (
        repo +
        "/blob/" +
        encodeURIComponent(capture.commit || "main") +
        "/" +
        path.split("/").map(encodeURIComponent).join("/")
      );
    }
    function link(parent, path, text) {
      const a = append(parent, "a", text);
      a.href = source(path);
      return a;
    }
    function disclosure(parent, title) {
      const d = append(parent, "details");
      append(d, "summary", title);
      return d;
    }
    const instrument = (s) => s.instrument || "unspecified";
    const precisionsFor = (s) =>
      manifestFor(s)?.precisions || [
        ...new Set(recordsFor(s).map((r) => r.identity.precision)),
      ];
    const allDevices = (s) =>
      manifestFor(s)?.devices || [
        ...new Set(recordsFor(s).map((r) => r.identity.device)),
      ];
    function eligible(s) {
      const pixels = s.configuration.source_pixels?.value;
      const pixelModel = /delaunay|rectangular|knn|pixelized/i.test(s.model);
      return (
        precisionsFor(s).includes("float64") &&
        ((!pixelModel && pixels == null) || pixels === 1500)
      );
    }
    // Prefer the unmodified producer filenames over named experiments; retain
    // one setup per measurement axis/device, with no cross-source record joins.
    function defaultRank(s, axis) {
      const filename = s.evidence?.path.split("/").at(-1) || "";
      const experiment =
        /autotune|constant_split|control|lever|thread|memo|experiment|no_|preload|chunk|stream/.test(
          filename,
        );
      const purposeBuilt =
        s.evidence?.path.includes(`/results/${axis}/`) ||
        s.evidence?.path.startsWith(`results/${axis}/`);
      return (
        (purposeBuilt ? -1000 : 0) +
        (s.role === "reference_candidate" ? -100 : 0) +
        (experiment ? 100 : 0) +
        filename.length
      );
    }
    function curated(setups, device) {
      const candidates = setups.filter(
        (s) => eligible(s) && allDevices(s).includes(device),
      );
      return [
        ...new Set(
          Object.keys(axes)
            .map((axis) =>
              [...candidates]
                .sort(
                  (a, b) =>
                    defaultRank(a, axis) - defaultRank(b, axis) ||
                    a.id.localeCompare(b.id),
                )
                .find(
                  (s) =>
                    hasAxis(s, axis) && devicesFor(s, axis).includes(device),
                ),
            )
            .filter(Boolean),
        ),
      ];
    }
    function configurationLabel(s) {
      const pixels = s.configuration.source_pixels?.value;
      return [pixels == null ? null : pixels + " source pixels", "float64"]
        .filter(Boolean)
        .join(" - ");
    }
    function configurationOptions(variants) {
      const options = variants.map((s) => {
        let text = configurationLabel(s);
        if (
          variants.filter((other) => configurationLabel(other) === text)
            .length > 1
        ) {
          const detail = axesFor(s)
            .filter((axis) => axis !== "runtime")
            .map((axis) => axes[axis]);
          for (const key of [
            "transform",
            "solver",
            "vmap_batch_size",
            "batch_size",
          ]) {
            const value = s.configuration[key]?.value;
            if (
              value != null &&
              variants.some(
                (other) => other.configuration[key]?.value !== value,
              )
            )
              detail.push(`${label(key)}: ${value}`);
          }
          if (detail.length) text += " — " + detail.join(" · ");
        }
        return [s.id, text];
      });
      // Keep otherwise indistinguishable evidence choices selectable without
      // changing their IDs or treating them as one configuration.
      return options.map(([id, text]) => [
        id,
        options.filter(([, other]) => other === text).length > 1
          ? text +
            " — " +
            variants
              .find((s) => s.id === id)
              .evidence.path.split("/")
              .at(-1)
          : text,
      ]);
    }
    function headlinePanel(parent, setup, records, message) {
      parent.replaceChildren();
      const metrics = presentation.headlines(
        setup || {},
        records,
        state.implementation,
      );
      const list = append(parent, "dl", "", "headline-list");
      for (const metric of metrics) {
        const row = append(list, "div", "", "headline-row");
        row.dataset.headline = metric.id;
        append(row, "dt", metric.label);
        const cell = append(row, "dd");
        const text = message || metric.status;
        const value = append(
          cell,
          "strong",
          text || Number(metric.value.toPrecision(4)) + " " + metric.unit,
          "headline-value",
        );
        if (!text) {
          value.dataset.value = String(metric.value);
          value.dataset.unit = metric.unit;
          value.title = `Recorded: ${metric.record.measurement[metric.record.metric]} ${metric.record.unit} · ${metric.record.metric} · Run: ${metric.record.run_id}`;
          if (metric.note) append(cell, "span", metric.note, "headline-note");
          const provenance = append(cell, "span", "", "headline-note");
          if (metric.record.evidence?.path)
            link(provenance, metric.record.evidence.path, "Source");
          if (!metric.record.provenance?.qualified)
            append(provenance, "span", " · Unqualified measurement");
        }
      }
    }

    async function verified(path, expected) {
      const response = await fetch(path);
      if (!response.ok)
        throw Error("Could not load evidence (HTTP " + response.status + ").");
      const bytes = await response.arrayBuffer();
      if (!crypto.subtle)
        throw Error(
          "Evidence verification needs HTTPS or localhost. Original evidence links remain available.",
        );
      const actual = Array.from(
        new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
        (x) => x.toString(16).padStart(2, "0"),
      ).join("");
      if (actual !== expected)
        throw Error(
          "Evidence changed since this page was published. Reload the page to get a matching catalogue.",
        );
      return JSON.parse(new TextDecoder().decode(bytes));
    }
    function route(next, push = true) {
      next = Object.keys(next).length
        ? { ...next, instance: capture.instance }
        : {};
      state = next;
      const hash = new URLSearchParams(
        Object.entries(next).filter(([, v]) => v),
      );
      if (push && location.hash.slice(1) !== hash.toString())
        history.pushState(null, "", "#" + hash);
      render();
      if (push)
        window.dispatchEvent(
          new CustomEvent("setup-route", { detail: capture.instance }),
        );
    }
    function fromURL() {
      const incoming = Object.fromEntries(
        new URLSearchParams(location.hash.slice(1)),
      );
      const linked = incoming.instance === capture.instance;
      // A setup deep link is not an element ID, so reveal the collapsed
      // board sections around this browser itself (PyAutoBrain#490).
      if (linked)
        for (let p = root.parentElement; p; p = p.parentElement)
          if (p.tagName === "DETAILS") p.open = true;
      route(linked ? incoming : {}, false);
    }
    function navigation() {
      nav.replaceChildren();
      const project = disclosure(nav, capture.label);
      project.dataset.id = "project-picker";
      project.open = false;
      const families = [
        ...new Set([
          ...catalogue.setups.map((s) => s.dataset),
          ...(catalogue.navigation || [])
            .filter((s) => s.category === "scientific_entrypoint")
            .map((s) => s.dataset),
        ]),
      ];
      families.sort(
        (a, b) => Object.keys(names).indexOf(a) - Object.keys(names).indexOf(b),
      );
      for (const dataset of families) {
        const family = disclosure(project, label(dataset));
        family.dataset.family = dataset;
        const choices = [
          ...new Set([
            ...catalogue.setups
              .filter((s) => s.dataset === dataset)
              .map((s) => `${s.model}|${implementationFor(s)}`),
            ...(catalogue.navigation || [])
              .filter(
                (s) =>
                  s.category === "scientific_entrypoint" &&
                  s.dataset === dataset,
              )
              .map((s) => `${s.model}|${implementationFor(s)}`),
          ]),
        ]
          .filter((choice) => !choice.startsWith("pixelized|"))
          .sort();
        for (const choice of choices) {
          const [model, implementation] = choice.split("|");
          const button = append(
            family,
            "a",
            modelLabel(model, implementation),
            "model-choice",
          );
          button.dataset.implementation = implementation;
          button.dataset.dataset = dataset;
          button.dataset.model = model;
          const url = new URL(location.href);
          url.searchParams.set("view", "model");
          url.hash = new URLSearchParams({
            instance: capture.instance,
            dataset,
            model,
            implementation,
          });
          button.href = url.href;
          button.target = "_blank";
          button.rel = "noopener";
        }
      }
      const shared = disclosure(project, "Shared measurement tools");
      const tools = [
        ...new Set(
          (catalogue.navigation || [])
            .filter((s) => s.category === "shared_measurement_tools")
            .map((s) => s.path.split("/")[2]),
        ),
      ];
      for (const tool of tools) {
        const details = disclosure(shared, label(tool));
        const ul = append(details, "ul", "", "evidence-list");
        (catalogue.navigation || [])
          .filter(
            (s) =>
              s.category === "shared_measurement_tools" &&
              s.path.split("/")[2] === tool,
          )
          .forEach((s) =>
            link(append(ul, "li"), s.path, s.path.split("/").at(-1)),
          );
      }
    }
    function selector(parent, id, title, options, value, change) {
      const l = append(parent, "label", title);
      l.htmlFor = prefix + id;
      const select = append(l, "select");
      select.id = prefix + id;
      select.dataset.id = id;
      options.forEach(([v, t]) => {
        const o = append(select, "option", t);
        o.value = v;
      });
      select.value = value;
      select.onchange = () => change(select.value);
      return select;
    }
    function metadata(setup) {
      const details = disclosure(results, "Configuration details");
      const dl = append(details, "dl", "", "config");
      const entries = Object.entries(setup.configuration || {});
      const priority = [
        "source_pixels",
        "psf_shape",
        "image_shape",
        "image_pixels_masked",
        "n_vis",
        "regularization",
        "transformer",
        "oversampling",
      ];
      entries.sort(
        ([a], [b]) =>
          (priority.includes(a) ? priority.indexOf(a) : 99) -
          (priority.includes(b) ? priority.indexOf(b) : 99),
      );
      for (const [key, entry] of entries) {
        append(dl, "dt", label(key));
        const dd = append(dl, "dd");
        if (entry.value === null) {
          append(dd, "span", "Not recorded", "muted");
          dd.title = entry.reason || "Unknown";
        } else
          append(
            dd,
            typeof entry.value === "object" ? "code" : "span",
            typeof entry.value === "object"
              ? JSON.stringify(entry.value)
              : String(entry.value),
          );
      }
    }
    function evidence(setup, records) {
      const details = disclosure(results, "Profiling Results");
      const ul = append(details, "ul", "", "evidence-list");
      const anchors = new Map();
      if (setup.evidence)
        anchors.set(JSON.stringify(setup.evidence), setup.evidence);
      if (!setup.id)
        catalogue.setups
          .filter(
            (s) =>
              s.dataset === setup.dataset &&
              s.model === setup.model &&
              implementationFor(s) === state.implementation &&
              s.evidence,
          )
          .forEach((s) => anchors.set(JSON.stringify(s.evidence), s.evidence));
      records.forEach((r) =>
        anchors.set(JSON.stringify(r.evidence), r.evidence),
      );
      for (const ev of anchors.values()) {
        const li = append(ul, "li");
        link(li, ev.path, ev.path);
        if (ev.fragment) append(li, "code", " · " + ev.fragment);
      }
      const scripts = (catalogue.navigation || []).filter(
        (s) =>
          s.dataset === setup.dataset &&
          s.model === setup.model &&
          implementationFor(s) === state.implementation,
      );
      const scriptDetails = disclosure(results, "Profiling scripts");
      const scriptList = append(scriptDetails, "ul", "", "evidence-list");
      scripts.forEach((s) => link(append(scriptList, "li"), s.path, s.path));
      if (!scripts.length)
        append(scriptDetails, "p", "No scripts recorded for this model.");
      if (!anchors.size)
        append(details, "p", "No evidence has been recorded for this setup.");
    }
    function timingScope(r) {
      if (/batch_time|batch_wall|vmap_batch/.test(r.metric))
        return "Batch wall time";
      if (/vmap.*per_call|batch_per_call/.test(r.metric))
        return "Per-replica batch cost";
      return r.axis === "runtime" ? "Single-call runtime" : "Component time";
    }
    function scaleKey(r) {
      // Method IDs identify individual components in legacy captures. Compare
      // their recorded timing semantics, never those opaque IDs.
      const { id, unknowns, ...method } = r.method;
      return JSON.stringify([
        r.setup_id,
        r.axis === "runtime" ? null : r.run_id,
        r.identity,
        r.provenance.host,
        r.unit,
        method,
        timingScope(r),
      ]);
    }
    function panels(records, setups) {
      const titles = {
        runtime: "Likelihood runtime",
        breakdown: "Likelihood breakdown",
        compile: "Compilation and setup",
        memory: "Memory",
      };
      for (const [axis, title] of Object.entries(titles)) {
        const section = disclosure(results, title);
        section.className = "metric-panel";
        section.dataset.axis = axis;
        section.open = axis === state.axis;
        const rows = records.filter((r) => r.axis === axis);
        // Persist an opening synchronously with summary activation (including
        // keyboard-generated clicks). Native toggle events are queued: reloading
        // or copying the URL before delivery would otherwise lose this selection.
        section.querySelector("summary").addEventListener("click", (event) => {
          if (section.open) return;
          event.preventDefault();
          section.open = true;
          state.axis = axis;
          history.replaceState(null, "", "#" + new URLSearchParams(state));
          if (!rows.length) {
            const next = setups.find(
              (s) =>
                hasAxis(s, axis) && devicesFor(s, axis).includes(state.device),
            );
            if (next && next.id !== state.setup)
              route({ ...state, setup: next.id, axis });
          }
        });
        if (!rows.length) {
          append(
            section,
            "p",
            "No recorded measurements for this configuration.",
            "empty",
          );
          continue;
        }
        const groups = new Map();
        for (const r of rows) {
          const key =
            scaleKey(r) +
            ":" +
            (presentation.category(
              r,
              rows.filter((other) => scaleKey(other) === scaleKey(r)),
            ) === "diagnostic"
              ? "diagnostic"
              : "main");
          if (!groups.has(key)) groups.set(key, []);
          groups.get(key).push(r);
        }
        let diagnostics;
        for (const group of groups.values()) {
          const first = group[0];
          const diagnostic =
            presentation.category(
              first,
              rows.filter((r) => scaleKey(r) === scaleKey(first)),
            ) === "diagnostic";
          if (diagnostic && !diagnostics) {
            diagnostics = disclosure(section, "Timing diagnostics");
            diagnostics.className = "timing-diagnostics";
            append(
              diagnostics,
              "p",
              "Cumulative prefixes and overlapping probes; these are not additional likelihood steps.",
              "metric-meta",
            );
          }
          const target = diagnostic ? diagnostics : section;
          group.sort((a, b) => {
            const total = (r) =>
              presentation.category(r, group) === "total" ? 1 : 0;
            return (
              total(b) - total(a) ||
              b.measurement[b.metric] - a.measurement[a.metric]
            );
          });
          // A component_total is instrumented component time, not a compiled
          // likelihood. Prefer it for its own group; otherwise use a matching
          // full single-call runtime, and finally the largest component.
          let reference;
          if (
            !diagnostic &&
            axis === "breakdown" &&
            timingScope(first) === "Component time"
          ) {
            reference = records.find(
              (r) =>
                r.axis === "runtime" &&
                ["single_call", "single_jit_block"].includes(r.metric) &&
                r.run_id === first.run_id &&
                r.setup_id === first.setup_id &&
                r.unit === first.unit &&
                JSON.stringify(r.identity) === JSON.stringify(first.identity) &&
                r.provenance.host === first.provenance.host &&
                [
                  "statistic",
                  "repetitions",
                  "warmup",
                  "cache_state",
                  "synchronization",
                ].every((k) => r.method[k] === first.method[k]),
            );
          }
          reference =
            group.find((r) => /^(?:cube_)?component_total$/.test(r.metric)) ||
            reference;
          const maximum = Math.max(
            ...group.map((r) => r.measurement[r.metric]),
          );
          const denominator =
            reference?.measurement[reference.metric] ?? maximum;
          const scale = reference
            ? /^(?:cube_)?component_total$/.test(reference.metric)
              ? "Component total"
              : "Full likelihood"
            : axis === "breakdown"
              ? "Largest component"
              : "Largest recorded value";
          const caption = axis === "runtime" ? timingScope(first) : scale;
          append(
            target,
            "p",
            caption + " · " + first.unit,
            "metric-meta scale-caption",
          );
          if (
            axis === "breakdown" &&
            !diagnostic &&
            !group.some((r) => /^(?:cube_)?component_total$/.test(r.metric))
          )
            append(
              target,
              "p",
              "Component total not recorded for these measurements.",
              "metric-meta",
            );
          const list = append(target, "ul", "", "metric-list");
          for (const r of group) {
            const value = r.measurement[r.metric];
            const li = append(list, "li", "", "metric-row");
            const detail = append(
              li,
              "details",
              undefined,
              "measurement-details",
            );
            const line = append(detail, "summary", undefined, "metric-title");
            line.title = "Show measurement details and original source";
            li.dataset.metric = r.metric;
            li.dataset.kind = presentation.category(r, group);
            append(line, "span", presentation.describe(r));
            const displayUnit =
              r.unit === "s" && value > 0 && value < 1 ? "ms" : r.unit;
            const displayValue = displayUnit === "ms" ? value * 1000 : value;
            const measured = append(
              line,
              "strong",
              Number(displayValue.toPrecision(4)) + " " + displayUnit,
              "metric-value",
            );
            measured.dataset.value = String(value);
            measured.dataset.unit = r.unit;
            measured.title = "Exact recorded value: " + value + " " + r.unit;
            const track = append(li, "div", "", "bar-track");
            track.setAttribute("aria-hidden", "true");
            const bar = append(track, "div", "", "bar");
            // Preserve the denominator even when a component exceeds its total;
            // values stay visible and the tooltip reports the unclipped percentage.
            const percent = denominator > 0 ? (100 * value) / denominator : 0;
            bar.style.width = Math.min(100, percent) + "%";
            bar.dataset.scale = scale;
            bar.dataset.denominator = String(denominator);
            li.title = `${percent.toFixed(1)}% of ${scale.toLowerCase()} (${denominator} ${r.unit})`;

            append(detail, "code", r.metric);
            const setup = catalogue.setups.find((s) => s.id === r.setup_id);
            const batch =
              setup?.configuration?.vmap_batch?.value ||
              setup?.configuration?.vmap_batch_size?.value ||
              setup?.configuration?.batch_size?.value;
            const semantics = [
              r.method.statistic,
              r.method.repetitions == null
                ? null
                : `${r.method.repetitions} repetitions`,
              batch == null ? null : `Batch size: ${batch}`,
            ].filter(Boolean);
            if (semantics.length) append(detail, "p", semantics.join(" · "));
            if (r.evidence?.path)
              link(detail, r.evidence.path, "Original measurement");
          }
        }
        if (diagnostics) section.append(diagnostics);
      }
    }
    function advice(setup) {
      const items = [
        ...(catalogue.hazards || []),
        ...(catalogue.recommendations || []),
      ].filter((x) => x.applies_to.setup_ids.includes(setup.id));
      const d = disclosure(results, "Hazards and setup guidance");
      if (!items.length)
        append(
          d,
          "p",
          "No version-qualified hazard or recommendation is bound to this configuration. This is not evidence that it is hazard-free.",
        );
      for (const item of items) {
        append(d, "h4", item.title);
        append(d, "p", item.description);
        append(d, "p", item.applies_to.limitations);
        const scope = disclosure(d, "Qualification and version applicability");
        append(
          scope,
          "pre",
          JSON.stringify(
            { validation: item.validation, applies_to: item.applies_to },
            null,
            2,
          ),
        );
        item.evidence.forEach((ev) => link(append(d, "p"), ev.path, ev.path));
      }
      const findings = catalogue.unbound_findings || [];
      const unbound = findings.filter((f) =>
        (f.discovery?.models || []).some(
          (m) => m.dataset === setup.dataset && m.model === setup.model,
        ),
      );
      function findingList(parent, entries) {
        for (const f of entries) {
          append(parent, "h4", f.title);
          append(parent, "p", f.discovery.reason);
          append(parent, "p", f.reason, "metric-meta");
          link(append(parent, "p"), f.evidence.path, "Original finding");
        }
      }
      if (unbound.length) {
        const other = disclosure(
          d,
          `Related model findings · applicability unverified (${unbound.length})`,
        );
        other.className = "related-hazards";
        findingList(other, unbound);
      }
      const uncategorized = findings.filter((f) => !f.discovery);
      if (uncategorized.length) {
        const other = disclosure(
          d,
          `Uncategorized findings (${uncategorized.length})`,
        );
        append(
          other,
          "p",
          "Model association and applicability have not been established.",
        );
        for (const f of uncategorized)
          link(append(other, "p"), f.evidence.path, f.title);
      }
      const estimates = (catalogue.static_memory_estimates || []).filter(
        (e) => setup.evidence && e.evidence.path === setup.evidence.path,
      );
      if (estimates.length) {
        const other = disclosure(d, "Static compiler memory estimates");
        estimates.forEach((e) =>
          append(
            other,
            "p",
            e.per_replica.value + " " + e.per_replica.unit + " · " + e.reason,
          ),
        );
      }
    }
    async function render() {
      const ticket = ++generation;
      results.replaceChildren();
      results.removeAttribute("aria-busy");
      status.textContent = "";
      status.className = "";
      const detailPage =
        new URLSearchParams(location.search).get("view") === "model";
      const selected = Boolean(state.dataset && state.model);
      if (selected && !state.implementation) {
        const linked = catalogue.setups.find((s) => s.id === state.setup);
        state.implementation = linked
          ? implementationFor(linked)
          : catalogue.setups.some(
                (s) =>
                  s.dataset === state.dataset &&
                  s.model === state.model &&
                  implementationFor(s) === "jax",
              )
            ? "jax"
            : "unknown";
      }
      if (detailPage) {
        document.body.classList.add("model-page");
        root.hidden = !selected;
        if (selected) {
          document.title = `${modelLabel(state.model, state.implementation)} · ${capture.label} profiling`;
          root.closest("details.board-section")?.classList.add("model-section");
        }
      }
      nav.hidden = detailPage;
      results.hidden = !selected;
      if (!selected) return;
      const back = append(results, "a", "← Profiling Results", "back-link");
      const home = new URL(location.href);
      home.searchParams.delete("view");
      home.hash = "evidence";
      back.href = home.href;
      append(
        results,
        "h2",
        capture.label +
          " / " +
          label(state.dataset) +
          " / " +
          modelLabel(state.model, state.implementation),
      );
      const choices = catalogue.setups.filter(
        (s) =>
          s.dataset === state.dataset &&
          s.model === state.model &&
          implementationFor(s) === state.implementation,
      );
      const instruments = [...new Set(choices.map(instrument))].sort();
      const requested = choices.find((s) => s.id === state.setup);
      if (
        (state.setup && !requested) ||
        (state.instrument && !instruments.includes(state.instrument)) ||
        (state.axis && !Object.hasOwn(axes, state.axis))
      ) {
        append(
          results,
          "p",
          "This linked configuration is not in the published catalogue. No substitute measurements are shown.",
          "empty",
        );
        return;
      }
      const selectedInstrument = requested
        ? instrument(requested)
        : state.instrument ||
          (instruments.includes("hst") ? "hst" : instruments[0]);
      const instrumentSetups = choices.filter(
        (s) => instrument(s) === selectedInstrument,
      );
      const devices = [...new Set(instrumentSetups.flatMap(allDevices))].sort();
      const device =
        state.device ||
        (requested ? allDevices(requested)[0] : null) ||
        (devices.includes("cpu") ? "cpu" : devices[0]);
      const variants = curated(instrumentSetups, device);
      const axis =
        state.axis || (variants[0] ? chooseAxis(variants[0]) : "runtime");
      let setup =
        requested || variants.find((s) => hasAxis(s, axis)) || variants[0];
      // An archived deep link remains inspectable, but is never injected into the
      // default selector. All other archived evidence remains linked at source.
      const archived = requested && !variants.includes(requested);
      if (state.device && !devices.includes(state.device)) setup = null;
      state = {
        instance: capture.instance,
        dataset: state.dataset,
        model: state.model,
        implementation: state.implementation,
        ...(selectedInstrument ? { instrument: selectedInstrument } : {}),
        axis,
        ...(device ? { device } : {}),
        ...(setup ? { setup: setup.id } : {}),
      };
      history.replaceState(null, "", "#" + new URLSearchParams(state));
      const fields = append(results, "div", "", "selectors");
      selector(
        fields,
        "instrument",
        "Instrument",
        instruments.map((i) => [
          i,
          i === "unspecified" ? "Not specified" : i.toUpperCase(),
        ]),
        selectedInstrument,
        (value) =>
          route({
            dataset: state.dataset,
            model: state.model,
            implementation: state.implementation,
            instrument: value,
          }),
      );
      selector(
        fields,
        "device",
        "Device",
        devices.map((d) => [d, d.toUpperCase()]),
        device,
        (value) =>
          route({
            dataset: state.dataset,
            model: state.model,
            implementation: state.implementation,
            instrument: selectedInstrument,
            device: value,
            axis,
          }),
      );
      const configOptions = configurationOptions(variants);
      if (archived)
        configOptions.unshift([
          requested.id,
          "Archived configuration (linked)",
        ]);
      selector(
        fields,
        "configuration",
        "Configuration",
        configOptions,
        setup?.id || "",
        (value) => route({ ...state, setup: value }),
      );
      const headline = append(results, "section", "", "headline-metrics");
      headline.setAttribute("aria-label", "Headline measurements");
      headline.setAttribute("aria-live", "polite");
      headlinePanel(headline, setup, [], setup ? "Loading…" : null);
      if (!setup) {
        append(
          results,
          "p",
          "No float64 results" +
            (/delaunay|rectangular|knn|pixelized/i.test(state.model)
              ? " with 1500 source pixels"
              : "") +
            " recorded for this instrument and device.",
          "empty",
        );
        evidence({ dataset: state.dataset, model: state.model }, []);
        return;
      }
      metadata(setup);
      const display = (allRecords) => {
        const records = allRecords.filter(
          (r) =>
            r.setup_id === setup.id &&
            (!device || r.identity.device === device) &&
            (archived || r.identity.precision === "float64"),
        );
        headlinePanel(headline, setup, records);
        panels(records, variants);
        advice(setup);
        evidence(setup, records);
      };
      const manifest = manifestFor(setup);
      if (!manifest) {
        display(recordsFor(setup));
        return;
      }
      status.textContent = "Loading selected setup…";
      results.setAttribute("aria-busy", "true");
      try {
        if (!/^catalogue\/shards\/[a-f0-9]{20}\.json$/.test(manifest.path))
          throw Error("Invalid evidence shard path.");
        let shard = cache.get(manifest.sha256);
        if (!shard) {
          if (!capture.remote_shards)
            throw Error(
              "Remote detail is unavailable for a local checkout; use the project dashboard or original evidence.",
            );
          shard = await verified(
            capture.shard_base + manifest.path,
            manifest.sha256,
          );
          cache.set(manifest.sha256, shard);
        }
        if (ticket !== generation) return;
        if (
          shard.version !== 2 ||
          shard.schema !== "profiling-summary" ||
          shard.setups.length !== 1 ||
          shard.setups[0].id !== setup.id ||
          JSON.stringify(shard.setups[0]) !== JSON.stringify(setup) ||
          shard.records.length !== manifest.records ||
          new Set(shard.records.map((r) => r.id)).size !==
            shard.records.length ||
          shard.records.some(
            (r) =>
              r.setup_id !== setup.id ||
              !Number.isFinite(r.measurement[r.metric]) ||
              r.measurement[r.metric] < 0,
          )
        )
          throw Error("Evidence does not match the selected setup.");
        display(shard.records);
        status.textContent = "";
      } catch (error) {
        if (ticket !== generation) return;
        status.textContent = "Evidence unavailable. " + error.message;
        status.className = "status-error";
        headlinePanel(headline, setup, [], "Evidence unavailable");
        const retry = append(results, "button", "Retry evidence", "retry");
        retry.type = "button";
        retry.onclick = () => {
          cache.delete(manifest.sha256);
          render();
        };
        evidence(setup, []);
      } finally {
        if (ticket === generation) results.removeAttribute("aria-busy");
      }
    }
    navigation();
    window.addEventListener("hashchange", fromURL);
    window.addEventListener("setup-route", (event) => {
      if (event.detail !== capture.instance) fromURL();
    });
    fromURL();
  }
})();
