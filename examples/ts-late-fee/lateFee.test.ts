import { describe, expect, it } from "vitest";
import { calculateLateFee } from "./lateFee.js";

describe("calculateLateFee", () => {
  // ── BDD scenarios ────────────────────────────────────────────────────

  it("no_fee_before_due_date", () => {
    expect(
      calculateLateFee(
        { amount_cents: 10000, due_date: "2026-05-31" },
        "2026-05-21"
      )
    ).toBe(0);
  });

  it("no_fee_on_due_date", () => {
    expect(
      calculateLateFee(
        { amount_cents: 10000, due_date: "2026-05-31" },
        "2026-05-31"
      )
    ).toBe(0);
  });

  it("one_month_overdue", () => {
    expect(
      calculateLateFee(
        { amount_cents: 10000, due_date: "2026-04-01" },
        "2026-05-01"
      )
    ).toBe(150);
  });

  // ── Invariants ───────────────────────────────────────────────────────

  it("does_not_mutate_input", () => {
    const invoice = { amount_cents: 10000, due_date: "2026-04-01" };
    const snapshot = JSON.stringify(invoice);
    calculateLateFee(invoice, "2026-05-01");
    expect(JSON.stringify(invoice)).toBe(snapshot);
  });

  it("deterministic_for_same_input", () => {
    const invoice = { amount_cents: 10000, due_date: "2026-04-01" };
    const today = "2026-05-01";
    const first = calculateLateFee(invoice, today);
    const second = calculateLateFee(invoice, today);
    const third = calculateLateFee(invoice, today);
    expect(second).toBe(first);
    expect(third).toBe(first);
  });

  it("fee_never_exceeds_principal", () => {
    // Many months overdue — fee should remain capped at the principal.
    const fee = calculateLateFee(
      { amount_cents: 10000, due_date: "2020-01-01" },
      "2026-01-01"
    );
    expect(fee).toBeLessThanOrEqual(10000);
  });

  // ── Failure cases ────────────────────────────────────────────────────

  it("rejects missing due_date", () => {
    expect(() =>
      calculateLateFee({ amount_cents: 10000, due_date: "" }, "2026-05-01")
    ).toThrow();
  });

  it("rejects negative amount_cents", () => {
    expect(() =>
      calculateLateFee(
        { amount_cents: -1, due_date: "2026-04-01" },
        "2026-05-01"
      )
    ).toThrow();
  });

  it("rejects malformed date string", () => {
    expect(() =>
      calculateLateFee(
        { amount_cents: 10000, due_date: "not-a-date" },
        "2026-05-01"
      )
    ).toThrow();
  });
});
