const assert = require("node:assert/strict");
const {
  implementation,
  describe,
  category,
} = require("../pulse/measurement_presentation.js");
assert.equal(
  implementation({ evidence: { path: "results/delaunay_numba.json" } }),
  "numba",
);
assert.equal(
  implementation({}, [
    {
      metric: "single_jit_block",
      identity: { backend: "cpu" },
      dependency_versions: { numba: "1" },
    },
  ]),
  "jax",
);
assert.equal(
  implementation({}, [
    {
      metric: "single_call",
      identity: { backend: "cpu" },
      dependency_versions: { numba: "1", jax: "1" },
    },
  ]),
  "unknown",
);
assert.equal(
  implementation({ configuration: { vmap_batch_size: { value: 3 } } }),
  "jax",
);
assert.equal(
  describe({ metric: "single_jit_block" }),
  "Full likelihood — JAX-compiled (post-compilation average)",
);
assert.equal(
  describe({ metric: "vmap.per_call" }),
  "Average per likelihood in a batch",
);
assert.equal(describe({ metric: "vmap.batch_time" }), "Total batch time");
assert.equal(
  describe({ metric: "reconstruction.jit.steady_per_call_s" }),
  "Solve for the source brightness — repeated evaluation",
);
assert(
  describe({ metric: "setup_prefix_7.jit.steady_per_call_s" }).includes(
    "Cumulative setup through mapping matrix",
  ),
);
assert.equal(describe({ metric: "unknown_operation" }), "unknown operation");
const row = {
  axis: "breakdown",
  metric: "reconstruction.jit.steady_per_call_s",
};
assert.equal(category(row, []), "main");
assert.equal(
  category(row, [{ metric: "steps.Regularized reconstruction" }]),
  "diagnostic",
);
assert.equal(
  category({ axis: "breakdown", metric: "setup_prefix" }, []),
  "diagnostic",
);
assert.equal(
  category({ axis: "breakdown", metric: "component_total" }, []),
  "total",
);
assert.equal(
  category(
    { axis: "breakdown", metric: "inversion_setup_vmap16.steady_per_call_s" },
    [{ metric: "steps_vmap_per_call.Inversion setup (steps 5-8 combined)" }],
  ),
  "diagnostic",
);
assert.equal(
  category(row, [{ metric: "steps_vmap_per_call.Regularized reconstruction" }]),
  "main",
);

const { headlines } = require("../pulse/measurement_presentation.js");
const setup = {
  id: "selected",
  configuration: { vmap_batch_size: { value: 16 } },
};
const measurement = (
  metric,
  value,
  axis = "runtime",
  unit = "s",
  extra = {},
) => ({
  setup_id: setup.id,
  run_id: "same-run",
  metric,
  axis,
  unit,
  measurement: { [metric]: value },
  identity: { device: "gpu", backend: "jax", precision: "float64" },
  provenance: { host: "same-host" },
  ...extra,
});
const selectedMetric = (rows, id = "total", backend = "jax") =>
  headlines(setup, rows, backend).find((m) => m.id === id);
const total = measurement("single_jit_block", 0.125);
const batched = measurement("vmap.per_call", 0.01);
assert.equal(selectedMetric([total]).value, 0.125);
assert.equal(selectedMetric([total, batched], "batched").value, 0.01);
assert.match(selectedMetric([batched], "batched").note, /batch size 16/);
assert.equal(
  selectedMetric([total, measurement("single_jit_median", 0.1)]).value,
  0.125,
);
for (const row of [
  measurement("component_total", 3, "breakdown"),
  measurement("full_pipeline.first_call", 3, "compile"),
  measurement("single_jit_block", 3, "breakdown"),
  measurement("single_jit_block", 3, "runtime", "MiB"),
  measurement("single_jit_block", -1),
  measurement("single_jit_block", Infinity),
  { ...total, setup_id: "another-setup" },
])
  assert.equal(selectedMetric([row]).status, "Not measured yet");
assert.equal(
  selectedMetric([measurement("vmap.batch_time", 8)], "batched").status,
  "Not measured yet",
);
assert.equal(
  selectedMetric(
    [measurement("full_pipeline.compile", 8, "compile")],
    "compile",
  ).value,
  8,
);
assert.equal(
  selectedMetric(
    [measurement("ray_trace_data_jit.compile_s", 8, "compile")],
    "compile",
  ).status,
  "Not measured yet",
);
assert.equal(
  selectedMetric(
    [measurement("host_peak_rss", 1024, "memory", "MiB")],
    "memory",
  ).value,
  1.073741824,
);
assert.equal(
  selectedMetric(
    [measurement("device_peak_allocated", 2e9, "memory", "B")],
    "vram",
  ).value,
  2,
);
assert.equal(
  selectedMetric(
    [measurement("static_memory_estimate", 2e9, "memory", "B")],
    "vram",
  ).status,
  "Not measured yet",
);
assert.equal(
  selectedMetric([measurement("host_peak_rss", 0, "memory", "GB")], "memory")
    .value,
  0,
);
for (const change of [
  { run_id: "other-run" },
  { identity: { ...total.identity, device: "cpu" } },
  { identity: { ...total.identity, backend: "numpy" } },
  { identity: { ...total.identity, precision: "float32" } },
  { provenance: { host: "other-host" } },
])
  assert.match(
    selectedMetric([total, { ...batched, ...change }]).status,
    /Multiple runs/,
  );
assert.match(
  selectedMetric([total, { ...total, method: { statistic: "median" } }]).status,
  /Multiple measurements/,
);
const numbaMetrics = headlines(
  setup,
  [measurement("direct_call", 0.4)],
  "numba",
);
assert.deepEqual(
  numbaMetrics.map((m) => m.id),
  ["total", "batched", "memory"],
);
assert.equal(numbaMetrics[0].value, 0.4);
assert.equal(numbaMetrics[1].status, "Not applicable");
assert.equal(
  selectedMetric([measurement("batch_per_call", 0.1)], "batched", "numba")
    .value,
  0.1,
);
