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
    function rank(s, axis) {
      if (hasAxis(s, axis)) return s.role === "reference_candidate" ? 0 : 1;
      return manifestFor(s) ? 2 : s.role === "planned_baseline" ? 4 : 3;
    }
    function ordered(setups, axis) {
      return [...setups].sort(
        (a, b) =>
          rank(a, axis) - rank(b, axis) ||
          configurationLabel(a).localeCompare(configurationLabel(b)) ||
          a.id.localeCompare(b.id),
      );
    }
    function chooseAxis(setup) {
      return (
        Object.keys(axes).find((axis) => hasAxis(setup, axis)) || "runtime"
      );
    }
    function goAxis(axis, device = "") {
      route({
        dataset: state.dataset,
        model: state.model,
        instrument: state.instrument,
        axis,
        device,
      });
    }
    function overview(setups) {
      const section = append(
        results,
        "section",
        undefined,
        "measurement-overview",
      );
      append(section, "h3", "Available measurements");
      append(
        section,
        "p",
        "Browse recorded runs by measurement and device. Runs can have different settings and revisions; they are not a combined benchmark.",
        "axis-note",
      );
      const unknown = setups.filter(
        (s) => manifestFor(s) && !axesFor(s).length,
      );
      if (unknown.length)
        append(
          section,
          "p",
          `${unknown.length} recorded runs have no axis summary; open a run to inspect its evidence.`,
          "metric-meta",
        );
      const grid = append(section, "div", undefined, "measurement-choices");
      for (const [axis, title] of Object.entries(axes)) {
        const matches = setups.filter((s) => hasAxis(s, axis));
        const card = append(grid, "div", undefined, "measurement-choice");
        const button = append(card, "button", title);
        button.type = "button";
        button.dataset.axis = axis;
        button.setAttribute("aria-pressed", String(state.axis === axis));
        button.onclick = () => goAxis(axis);
        append(
          card,
          "p",
          matches.length
            ? `${matches.length} recorded runs`
            : unknown.length
              ? "Axis coverage not recorded"
              : "No recorded measurements",
          "metric-meta",
        );
        const devices = [
          ...new Set(matches.flatMap((s) => devicesFor(s, axis))),
        ].sort();
        append(
          card,
          "p",
          devices.map(label).join(" · ") ||
            (matches.length ? "Device breakdown not recorded" : ""),
          "metric-meta",
        );
      }
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
      delaunay_nn: "Delaunay natural neighbour",
    };
    const label = (value) =>
      models[value] || names[value] || String(value).replaceAll("_", " ");
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
    function configurationLabel(s) {
      if (s.role === "planned_baseline") return "Baseline · not measured";
      const info = (catalogue.evidence_shards || []).find(
        (item) => item.setup_id === s.id,
      );
      const axes = {
        runtime: "Runtime",
        breakdown: "Breakdown",
        compile: "Compile",
        memory: "Memory",
      };
      const recorded = catalogue.records.filter((r) => r.setup_id === s.id);
      const axisNames = info?.axes || [...new Set(recorded.map((r) => r.axis))];
      const devices = info?.devices || [
        ...new Set(recorded.map((r) => r.identity.device).filter(Boolean)),
      ];
      const precisions = info?.precisions || [
        ...new Set(recorded.map((r) => r.identity.precision).filter(Boolean)),
      ];
      const pixels = s.configuration.source_pixels?.value;
      return [
        s.role === "reference_candidate" ? "Reference candidate" : "Archive",
        axisNames.map((a) => axes[a] || a).join(" + ") ||
          "Recorded configuration",
        devices.map((d) => d.toUpperCase()).join(" / "),
        precisions.join(" / "),
        pixels == null ? null : pixels + " source pixels",
        (s.configuration_id || s.id).slice(-6),
      ]
        .filter(Boolean)
        .join(" · ");
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
      route(incoming.instance === capture.instance ? incoming : {}, false);
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
              .map((s) => s.model),
            ...(catalogue.navigation || [])
              .filter(
                (s) =>
                  s.category === "scientific_entrypoint" &&
                  s.dataset === dataset,
              )
              .map((s) => s.model),
          ]),
        ].sort();
        for (const model of choices) {
          const button = append(family, "button", label(model), "model-choice");
          button.type = "button";
          button.dataset.dataset = dataset;
          button.dataset.model = model;
          button.onclick = () => {
            route({ dataset, model });
            $("results").scrollIntoView({ behavior: "smooth", block: "start" });
          };
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
      const details = disclosure(results, "Profiling evidence and scripts");
      const ul = append(details, "ul", "", "evidence-list");
      const anchors = new Map();
      if (setup.evidence)
        anchors.set(JSON.stringify(setup.evidence), setup.evidence);
      records.forEach((r) =>
        anchors.set(JSON.stringify(r.evidence), r.evidence),
      );
      for (const ev of anchors.values()) {
        const li = append(ul, "li");
        link(li, ev.path, ev.path);
        if (ev.fragment) append(li, "code", " · " + ev.fragment);
      }
      const scripts = (catalogue.navigation || []).filter(
        (s) => s.dataset === setup.dataset && s.model === setup.model,
      );
      scripts.forEach((s) => link(append(ul, "li"), s.path, s.path));
      if (!anchors.size && !scripts.length)
        append(details, "p", "No evidence has been recorded for this setup.");
    }
    function qualification(records) {
      const heading = results.querySelector(".context .qualification");
      if (heading)
        heading.textContent =
          "Evidence status: " +
          [...new Set(records.map((r) => r.validation.status))].join(" / ");
      const d = disclosure(results, "Qualification and measurement method");
      for (const r of records) {
        const p = append(d, "p");
        append(p, "strong", r.metric + ": ");
        append(
          p,
          "span",
          "Exact recorded value: " +
            r.measurement[r.metric] +
            " " +
            r.unit +
            ". ",
        );
        append(p, "span", r.validation.status + " — " + r.validation.reason);
        append(
          d,
          "p",
          "Host: " +
            (r.provenance.host || "not recorded") +
            " · precision: " +
            (r.identity.precision || "not recorded") +
            " · software: " +
            JSON.stringify(r.identity.software),
          "metric-meta",
        );
        append(d, "p", "Method: " + JSON.stringify(r.method), "metric-meta");
      }
    }
    function panels(records, setups) {
      const axes = {
        runtime: [
          "Likelihood runtime",
          "Full likelihood observations. Single-JIT blocks can include first-call effects; batch timings are not single-call latency.",
        ],
        breakdown: [
          "Likelihood breakdown",
          "Instrumented component costs are not the full compiled likelihood time. Bars compare values only within this setup and unit.",
        ],
        compile: [
          "Compilation and setup",
          "Trace, compile, first call and setup wall time are distinct measurements; do not add them together.",
        ],
        memory: [
          "Memory",
          "Observed host RSS is not GPU VRAM. Static compiler estimates are shown separately.",
        ],
      };
      for (const [axis, [title, note]] of Object.entries(axes)) {
        const section = disclosure(results, title);
        section.className = "metric-panel";
        section.dataset.axis = axis;
        section.open =
          axis ===
          (records.some((r) => r.axis === state.axis)
            ? state.axis
            : Object.keys(axes).find((a) => records.some((r) => r.axis === a)));
        append(section, "p", note, "axis-note");
        const rows = records.filter((r) => r.axis === axis);
        if (!rows.length) {
          const available = setups.filter((s) => hasAxis(s, axis));
          append(
            section,
            "p",
            available.length
              ? `Not recorded in this run. ${available.length} other runs contain ${label(axis)} measurements; settings may differ.`
              : setups.some((s) => manifestFor(s) && !axesFor(s).length)
                ? "Other runs have no axis summary; their measurement coverage is unknown."
                : "No recorded measurements for this model and instrument.",
            "empty",
          );
          if (available.length) {
            const browse = append(
              section,
              "button",
              `Browse ${label(axis)} runs`,
              "retry",
            );
            browse.type = "button";
            browse.onclick = () => goAxis(axis);
          }
          continue;
        }
        const groups = new Map();
        for (const r of rows) {
          const scope =
            {
              "vmap.batch_time": "Batch wall time",
              batch_wall: "Batch wall time",
              "vmap.per_call": "Per-replica batch cost",
              batch_per_call: "Per-replica batch cost",
              single_jit_block: "Single-call observations",
              single_call: "Single-call observations",
            }[r.metric] ||
            (axis === "runtime"
              ? label(r.metric) + " observations"
              : "Component observations");
          const caption = [
            scope,
            r.identity.device || "device unknown",
            r.identity.backend || "backend unknown",
            r.identity.precision || "precision unknown",
            r.provenance.host || "host unknown",
            r.unit,
          ].join(" · ");
          const key = JSON.stringify([caption, r.identity, r.method]);
          if (!groups.has(key)) groups.set(key, { caption, rows: [] });
          groups.get(key).rows.push(r);
        }
        for (const { caption, rows: group } of groups.values()) {
          append(section, "p", caption, "metric-meta");
          const list = append(section, "ul", "", "metric-list");
          const max = Math.max(...group.map((r) => r.measurement[r.metric]));
          for (const r of group) {
            const value = r.measurement[r.metric];
            const li = append(list, "li", "", "metric-row");
            const line = append(li, "div", "", "metric-title");
            append(line, "span", label(r.metric));
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
            bar.style.width = (max > 0 ? (100 * value) / max : 0) + "%";
            append(
              li,
              "p",
              (r.method.statistic || "Statistic not recorded") +
                " · " +
                (r.method.repetitions === null
                  ? "repetitions not recorded"
                  : r.method.repetitions + " repetitions"),
              "metric-meta",
            );
          }
        }
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
      const shared = findings.filter((f) => f.discovery?.shared);
      if (shared.length) {
        const other = disclosure(
          d,
          `Shared component and method findings (${shared.length})`,
        );
        other.className = "shared-hazards";
        append(
          other,
          "p",
          "These concern shared components or methods. Their presence here does not establish that this model uses them or that this run is affected.",
        );
        findingList(other, shared);
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
      const choices = catalogue.setups.filter(
        (s) => s.dataset === state.dataset && s.model === state.model,
      );
      nav
        .querySelectorAll(".model-choice")
        .forEach((b) =>
          b.setAttribute(
            "aria-current",
            String(
              b.dataset.dataset === state.dataset &&
                b.dataset.model === state.model,
            ),
          ),
        );
      nav.querySelectorAll("[data-family]").forEach((d) => {
        if (d.dataset.family === state.dataset) d.open = true;
      });
      if (!state.dataset || !state.model) {
        results.hidden = true;
        $("project-picker").querySelector("summary").textContent =
          capture.label;
        return;
      }
      results.hidden = false;
      const picker = $("project-picker");
      picker.open = false;
      picker.querySelector("summary").textContent =
        capture.label +
        " / " +
        label(state.dataset) +
        " / " +
        label(state.model) +
        " · change setup";
      append(results, "h2", label(state.dataset) + " / " + label(state.model));
      if (!choices.length) {
        append(
          results,
          "p",
          "No catalogue measurements for this model yet.",
          "empty",
        );
        evidence({ dataset: state.dataset, model: state.model }, []);
        return;
      }
      const instruments = [...new Set(choices.map(instrument))].sort();
      if (
        (state.setup && !choices.some((s) => s.id === state.setup)) ||
        (state.instrument && !instruments.includes(state.instrument)) ||
        (state.axis && !Object.hasOwn(axes, state.axis))
      ) {
        append(
          results,
          "p",
          "This linked configuration is not in the published catalogue. No substitute measurements are shown.",
          "empty",
        );
        const choose = append(
          results,
          "button",
          "Choose an available configuration",
          "retry",
        );
        choose.type = "button";
        choose.onclick = () =>
          route({ dataset: state.dataset, model: state.model });
        return;
      }
      const requested = choices.find((s) => s.id === state.setup);
      const selectedInstrument = requested
        ? instrument(requested)
        : instruments.includes(state.instrument)
          ? state.instrument
          : instrument(
              choices.find((s) => s.role === "reference_candidate") ||
                choices[0],
            );
      const instrumentSetups = choices.filter(
        (s) => instrument(s) === selectedInstrument,
      );
      const axis =
        state.axis ||
        (requested
          ? chooseAxis(requested)
          : chooseAxis(ordered(instrumentSetups, "runtime")[0]));
      const devices = [
        ...new Set(instrumentSetups.flatMap((s) => devicesFor(s, axis))),
      ].sort();
      if (state.device && !devices.includes(state.device)) {
        append(
          results,
          "p",
          "No recorded device matches this link. Choose a measurement to browse available runs.",
          "empty",
        );
        state.instrument = selectedInstrument;
        overview(instrumentSetups);
        return;
      }
      const device = state.device || "";
      if (
        device &&
        requested &&
        manifestFor(requested) &&
        !devicesFor(requested, axis).includes(device)
      ) {
        append(
          results,
          "p",
          "The linked run does not record this measurement on the selected device. No substitute measurements are shown.",
          "empty",
        );
        const reset = append(
          results,
          "button",
          "Open the exact run without the device filter",
          "retry",
        );
        reset.type = "button";
        reset.onclick = () =>
          route({ ...state, device: "", axis: chooseAxis(requested) });
        return;
      }
      const matches = ordered(
        instrumentSetups.filter(
          (s) =>
            hasAxis(s, axis) &&
            (!device || devicesFor(s, axis).includes(device)),
        ),
        axis,
      );
      // Keep explicit baseline/failed selections reachable without calling them measurements.
      const variants = [
        ...matches,
        ...instrumentSetups.filter(
          (s) => !matches.includes(s) && !axesFor(s).length,
        ),
      ];
      if (requested && !variants.some((s) => s.id === requested.id))
        variants.unshift(requested);
      const setup = requested || variants[0];
      state = {
        instance: capture.instance,
        dataset: state.dataset,
        model: state.model,
        instrument: selectedInstrument,
        axis,
        ...(device ? { device } : {}),
        ...(setup ? { setup: setup.id } : {}),
      };
      history.replaceState(null, "", "#" + new URLSearchParams(state));
      const instrumentFields = append(results, "div", "", "selectors");
      selector(
        instrumentFields,
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
            instrument: value,
          }),
      );
      overview(instrumentSetups);
      const fields = append(results, "div", "", "selectors");
      selector(
        fields,
        "device",
        "Recorded device",
        [["", "All recorded devices"], ...devices.map((d) => [d, label(d)])],
        device,
        (value) => goAxis(axis, value),
      );
      if (!setup) {
        append(
          results,
          "p",
          "No recorded runs for this measurement. Choose another measurement above.",
          "empty",
        );
        advice({ dataset: state.dataset, model: state.model });
        evidence({ dataset: state.dataset, model: state.model }, []);
        return;
      }
      selector(
        fields,
        "configuration",
        "Configuration / evidence run",
        variants.map((s) => [s.id, configurationLabel(s)]),
        setup.id,
        (value) => {
          const selected = variants.find((s) => s.id === value);
          const nextAxis = hasAxis(selected, axis)
            ? axis
            : chooseAxis(selected);
          route({
            ...state,
            setup: value,
            axis: nextAxis,
            device: devicesFor(selected, nextAxis).includes(device)
              ? device
              : "",
          });
        },
      );
      const context = append(results, "div", "", "context");
      append(
        context,
        "p",
        setup.role === "planned_baseline"
          ? "Baseline pending · no accepted measurement"
          : "Recorded evidence · inspect qualification below",
        "qualification",
      );
      append(
        context,
        "p",
        "Other devices or runs may have different settings. This view keeps each recorded configuration separate.",
        "muted",
      );
      const keySettings = [
        "source_pixels",
        "psf_shape",
        "image_pixels_masked",
        "n_vis",
      ];
      const facts = append(context, "p", "", "metric-meta");
      facts.textContent = keySettings
        .map(
          (k) =>
            label(k) +
            ": " +
            (setup.configuration[k]?.value == null
              ? "not recorded"
              : JSON.stringify(setup.configuration[k].value)),
        )
        .join(" · ");
      if (setup.role === "planned_baseline") {
        const slots = (catalogue.planned_cells || []).filter(
          (c) => c.setup_id === setup.id,
        );
        append(
          context,
          "p",
          [...new Set(slots.map((s) => s.device.toUpperCase()))].join(" / ") +
            " · " +
            slots.length +
            " measurement slots not measured.",
        );
        panels([], instrumentSetups);
        metadata(setup);
        advice(setup);
        evidence(setup, []);
        return;
      }
      const manifest = (catalogue.evidence_shards || []).find(
        (s) => s.setup_id === setup.id,
      );
      if (!manifest) {
        const inline = catalogue.records.filter((r) => r.setup_id === setup.id);
        if (inline.length) {
          panels(inline, instrumentSetups);
          metadata(setup);
          qualification(inline);
          advice(setup);
          evidence(setup, inline);
          return;
        }

        const failed = catalogue.selections.filter(
          (s) => s.setup_id === setup.id,
        );
        append(
          context,
          "p",
          failed.map((s) => s.status + ": " + s.reason).join("; ") ||
            "No measured evidence is available.",
        );
        panels([], instrumentSetups);
        metadata(setup);
        advice(setup);
        evidence(setup, []);
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
        panels(shard.records, instrumentSetups);
        metadata(setup);
        qualification(shard.records);
        advice(setup);
        evidence(setup, shard.records);
        status.textContent = "";
      } catch (error) {
        if (ticket !== generation) return;
        status.textContent = "Evidence unavailable. " + error.message;
        status.className = "status-error";
        const retry = append(results, "button", "Retry evidence", "retry");
        retry.type = "button";
        retry.onclick = () => {
          cache.delete(manifest.sha256);
          render();
        };
        metadata(setup);
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
