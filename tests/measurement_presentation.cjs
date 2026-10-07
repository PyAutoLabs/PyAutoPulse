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
