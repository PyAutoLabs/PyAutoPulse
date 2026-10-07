/* Presentation of recorded producer measurements. Never infer totals or backend
 * from hardware/dependency versions. Names follow the likelihood producers;
 * original metric keys and evidence remain available in measurement details. */
(() => {
  "use strict";
  function implementation(setup, records = []) {
    const path = setup.evidence?.path || setup.path || "";
    if (/(?:^|[_/.-])numba(?:[_/.-]|$)/i.test(path)) return "numba";
    if (
      /(?:^|[_/.-])(?:jax|jit)(?:[_/.-]|$)/i.test(path) ||
      /^(?:jit|vmap)$/.test(setup.configuration?.transform?.value) ||
      ["vmap_batch", "vmap_batch_size"].some(
        (key) => setup.configuration?.[key]?.value > 0,
      ) ||
      records.some(
        (r) =>
          r.identity?.backend === "jax" ||
          /single_jit|(?:^|[._])jit[._]|vmap/.test(r.metric),
      ) ||
      // These scientific entrypoints are the JAX implementations; their Numba
      // siblings are explicitly suffixed. This is a source-path convention,
      // not a claim that every CPU result is JAX.
      /\/likelihood_(?:runtime|breakdown)(?:_jax)?\.py$/.test(path)
    )
      return "jax";
    return "unknown";
  }
  const operations = {
    ray_trace_data: "Ray-trace the image grid",
    ray_trace_mesh: "Ray-trace the source mesh",
    lens_image: "Evaluate lens light",
    blurred_image: "Convolve lens light with the PSF",
    profile_subtract: "Subtract lens light from the data",
    inversion_setup: "Build the source mapping and apply the PSF",
    data_vector: "Build the data vector (D)",
    curvature_matrix: "Build the curvature matrix (F)",
    regularization_matrix: "Build the regularization matrix (H)",
    reconstruction: "Solve for the source brightness",
    log_evidence: "Evaluate the model image and log evidence",
    mapping: "Build the mapping matrix",
    inversion: "Solve the inversion",
  };
  const steps = {
    "Ray-trace data grid": operations.ray_trace_data,
    "Ray-trace mesh grid": operations.ray_trace_mesh,
    "Lens light images (pre-PSF)": operations.lens_image,
    "Blurred image (PSF convolution)": operations.blurred_image,
    "Profile-subtracted image": operations.profile_subtract,
    "Inversion setup (steps 5-8 combined)": operations.inversion_setup,
    "Data vector (D)": operations.data_vector,
    "Curvature matrix (F)": operations.curvature_matrix,
    "Regularization matrix (H)": operations.regularization_matrix,
    "Regularized reconstruction": operations.reconstruction,
    "Mapped recon + log evidence": operations.log_evidence,
    "Reconstruction solve (BLAS)": operations.reconstruction + " (BLAS)",
    "Regularization matrix H": operations.regularization_matrix,
    "Data vector D [numba]": operations.data_vector + " (Numba)",
    "FitImaging construct": "Construct the imaging fit",
    "Profile subtracted image": operations.profile_subtract,
    "Blurred image (FFT convolve)": "Convolve lens light with the PSF (FFT)",
    "Inversion build (trace+Delaunay+mapper)":
      "Ray-trace and build the Delaunay source mapping",
    "F + H": "Add curvature and regularization matrices",
  };
  const runtime = {
    single_call: "Full likelihood — single evaluation",
    single_jit_block:
      "Full likelihood — JAX-compiled (post-compilation average)",
    single_jit_median: "Full likelihood — JAX-compiled (steady median)",
    cube_single_jit: "Full datacube likelihood — JAX-compiled",
    direct_call: "Full likelihood — direct function call",
    "vmap.per_call": "Average per likelihood in a batch",
    batch_per_call: "Average per likelihood in a batch",
    "vmap.batch_time": "Total batch time",
    batch_wall: "Total batch time",
    component_total: "Recorded component total",
    cube_component_total: "Recorded datacube component total",
  };
  function describe(r) {
    const key = r.metric;
    if (runtime[key]) return runtime[key];
    const prefix = key.match(
      /^setup_prefix_(5|6|7|8|11)(?:_vmap(\d+))?(?:[._]jit)?\.(.*)$/,
    );
    if (prefix) {
      const endpoints = {
        5: "border relocation",
        6: "Delaunay interpolation and source mapper",
        7: "mapping matrix",
        8: "PSF-convolved mapping matrix",
        11: "regularization matrix",
      };
      return (
        `Cumulative setup through ${endpoints[prefix[1]]}` +
        (prefix[2] ? ` — batch of ${prefix[2]}` : "") +
        (prefix[3] === "first_call_s"
          ? " (first evaluation)"
          : prefix[3] === "steady_per_call_s"
            ? " (repeated evaluation)"
            : ` (${prefix[3].replaceAll("_", " ")})`)
      );
    }
    const prefixes = {
      setup_prefix: "Cumulative likelihood setup",
      regularization_matrix_prefix: "Cumulative setup through regularization",
      interpolator_prefix: "Cumulative setup through interpolation",
    };
    const prefixKey = key.replace(/_vmap_per_call$/, "");
    if (prefixes[prefixKey])
      return (
        prefixes[prefixKey] +
        (key !== prefixKey ? " — batch average per likelihood" : "")
      );
    const step = key.replace(
      /^(?:steps|steps_median|dense_steps|steps_vmap_per_call)\./,
      "",
    );
    if (step !== key) {
      const suffix = key.startsWith("steps_vmap_per_call.")
        ? " — batch average per likelihood"
        : key.startsWith("steps_median.")
          ? " — median"
          : "";
      return (steps[step] || step) + suffix;
    }
    const full = key.match(
      /^(full_call|full_pipeline)\.(per_call_s|mean_s|median_s|min_s|max_s)$/,
    );
    if (full)
      return (
        "Full likelihood — " +
        {
          per_call_s: "single evaluation",
          mean_s: "mean",
          median_s: "median",
          min_s: "minimum",
          max_s: "maximum",
        }[full[2]]
      );
    const batched = key.match(/^(.*?)_vmap(\d+)\.steady_per_call_s$/);
    if (batched && operations[batched[1]])
      return (
        operations[batched[1]] +
        ` — average per likelihood in a batch of ${batched[2]}`
      );
    const match = key.match(
      /^(.*?)(?:[._]jit)?\.(lower_s|compile_s|first_call_s|steady_per_call_s)$/,
    );
    if (match) {
      const operation = operations[match[1]] || match[1].replaceAll("_", " ");
      const phase = {
        lower_s: "prepare compiler input",
        compile_s: "compile",
        first_call_s: "first evaluation",
        steady_per_call_s: "repeated evaluation",
      }[match[2]];
      return operation + " — " + phase;
    }
    if (operations[key]) return operations[key];
    // Unmapped metrics retain their producer's wording, rather than pretending
    // that a technical measurement has a known scientific interpretation.
    return key.replaceAll("_", " ");
  }
  function category(r, compatibleRows) {
    if (/^(?:cube_)?component_total$/.test(r.metric)) return "total";
    if (r.axis !== "breakdown") return "main";
    if (/prefix|(?:sparse|reconstruction)_sub|sparse_setup/.test(r.metric))
      return "diagnostic";
    const batched = r.metric.match(/^(.*?)_vmap\d+\.steady_per_call_s$/);
    if (
      batched &&
      operations[batched[1]] &&
      compatibleRows.some(
        (other) =>
          other.metric.startsWith("steps_vmap_per_call.") &&
          steps[other.metric.slice("steps_vmap_per_call.".length)] ===
            operations[batched[1]],
      )
    )
      return "diagnostic";
    const match = r.metric.match(/^(.*?)(?:[._]jit)\.steady_per_call_s$/);
    if (
      match &&
      operations[match[1]] &&
      compatibleRows.some(
        (other) =>
          other.metric.startsWith("steps.") &&
          describe(other) === operations[match[1]],
      )
    )
      return "diagnostic";
    return "main";
  }
  // Explicit producer keys only: a component sum, first call, compiler memory
  // estimate or total batch wall time is never a likelihood headline.
  const headlineMetrics = [
    {
      id: "total",
      label: "Likelihood Run Time Total",
      axis: "runtime",
      unit: "s",
      keys: [
        "single_jit_block",
        "single_jit_median",
        "cube_single_jit",
        "single_call",
        "direct_call",
        "full_call.per_call_s",
        "full_pipeline.per_call_s",
        "full_call.mean_s",
        "full_pipeline.mean_s",
        "full_call.median_s",
        "full_pipeline.median_s",
      ],
    },
    {
      id: "batched",
      label: "Likelihood Run Time Batched",
      axis: "runtime",
      unit: "s",
      keys: ["vmap.per_call", "batch_per_call"],
    },
    {
      id: "compile",
      label: "JAX Compile Time",
      axis: "compile",
      unit: "s",
      keys: ["full_pipeline.compile", "cold_compile", "compile"],
    },
    {
      id: "vram",
      label: "VRAM Use",
      axis: "memory",
      unit: "GB",
      keys: ["device_peak_allocated"],
    },
    {
      id: "memory",
      label: "Memory Use",
      axis: "memory",
      unit: "GB",
      keys: ["host_peak_rss"],
    },
  ];
  const memoryUnits = {
    B: 1e-9,
    bytes: 1e-9,
    KiB: 1024 / 1e9,
    MiB: 1024 ** 2 / 1e9,
    GiB: 1024 ** 3 / 1e9,
    kB: 1e-6,
    MB: 1e-3,
    GB: 1,
  };
  const canonical = (value) =>
    JSON.stringify(value, (_, v) =>
      v && typeof v === "object" && !Array.isArray(v)
        ? Object.fromEntries(
            Object.entries(v).sort(([a], [b]) => a.localeCompare(b)),
          )
        : v,
    );
  function headlines(setup, records, backend = implementation(setup, records)) {
    const definitions = headlineMetrics.filter(
      (d) => backend !== "numba" || !["compile", "vram"].includes(d.id),
    );
    const candidates = definitions.map((d) =>
      records.filter(
        (r) =>
          r.setup_id === setup.id &&
          r.axis === d.axis &&
          d.keys.includes(r.metric) &&
          (d.unit === "s"
            ? r.unit === "s"
            : Object.hasOwn(memoryUnits, r.unit)) &&
          Number.isFinite(r.measurement?.[r.metric]) &&
          r.measurement[r.metric] >= 0,
      ),
    );
    // A headline must not silently assemble different runs or hardware/software
    // identities into a synthetic result. Keep those observations in details.
    const cohorts = new Set(
      candidates
        .flat()
        .map((r) => canonical([r.run_id, r.identity, r.provenance?.host])),
    );
    return definitions.map((d, i) => {
      const rows = candidates[i];
      const result = { ...d, status: "Not measured yet" };
      if (!rows.length) {
        if (d.id === "batched" && backend === "numba")
          result.status = "Not applicable";
        return result;
      }
      if (cohorts.size > 1)
        return { ...result, status: "Multiple runs — see details" };
      const key = d.keys.find((key) => rows.some((r) => r.metric === key));
      const selected = rows.filter((r) => r.metric === key);
      if (selected.length !== 1)
        return { ...result, status: "Multiple measurements — see details" };
      const record = selected[0];
      const value =
        record.measurement[key] *
        (d.unit === "GB" ? memoryUnits[record.unit] : 1);
      const batch = ["vmap_batch", "vmap_batch_size", "batch_size"]
        .map((key) => setup.configuration?.[key]?.value)
        .find((n) => Number.isFinite(n) && n > 0);
      const note =
        d.id === "batched"
          ? "Per likelihood" +
            (batch ? ` · batch size ${batch}` : " · batch size not recorded")
          : d.id === "memory"
            ? "Peak host RSS"
            : d.id === "vram"
              ? "Peak device allocation"
              : d.id === "compile" &&
                  setup.configuration?.transform?.value === "vmap"
                ? "Batched compilation" +
                  (batch ? ` · batch size ${batch}` : "")
                : record.method?.statistic || "";
      return { ...result, status: null, value, record, note };
    });
  }
  const api = { implementation, describe, category, headlines };
  globalThis.PulsePresentation = api;
  if (typeof module !== "undefined") module.exports = api;
})();
