/**
 * Registry of well-known named invariants.
 *
 * Spec authors can reference these by name in `invariants:`. Postulate
 * recognises them and reports them separately from custom invariants.
 *
 * This registry is intentionally tiny in v0.1. The roadmap is to grow it
 * and eventually pair each entry with a property-test generator (e.g.
 * fast-check) so that "does_not_mutate_input" can be checked without the
 * author writing the property test by hand.
 */
export type KnownInvariant = {
  name: string;
  description: string;
};

export const KNOWN_INVARIANTS: ReadonlyArray<KnownInvariant> = [
  {
    name: "does_not_mutate_input",
    description: "Function arguments are unchanged after the call returns."
  },
  {
    name: "deterministic_output",
    description: "Same inputs produce the same output across repeated calls."
  },
  {
    name: "deterministic_for_same_input",
    description: "Same inputs produce the same output across repeated calls."
  },
  {
    name: "pure",
    description: "No observable side effects; output depends only on arguments."
  },
  {
    name: "idempotent",
    description: "Calling the operation twice has the same effect as once."
  },
  {
    name: "total",
    description: "Function is defined for every input that satisfies preconditions."
  }
];

export const KNOWN_INVARIANT_NAMES: ReadonlySet<string> = new Set(
  KNOWN_INVARIANTS.map((i) => i.name)
);
