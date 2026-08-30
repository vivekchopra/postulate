export type Invoice = {
  amount_cents: number;
  due_date: string;
};

export function calculateLateFee(invoice: Invoice, todayIso: string): number {
  if (!invoice.due_date) throw new Error("invoice.due_date is required");
  if (invoice.amount_cents < 0) {
    throw new Error("invoice.amount_cents must be non-negative");
  }

  const due = new Date(invoice.due_date + "T00:00:00Z");
  const today = new Date(todayIso + "T00:00:00Z");

  if (Number.isNaN(due.getTime()) || Number.isNaN(today.getTime())) {
    throw new Error("invalid date");
  }

  if (today <= due) return 0;

  const monthsOverdue =
    (today.getUTCFullYear() - due.getUTCFullYear()) * 12 +
    (today.getUTCMonth() - due.getUTCMonth()) -
    (today.getUTCDate() < due.getUTCDate() ? 1 : 0);

  const fullMonths = Math.max(0, monthsOverdue);
  const fee = Math.round(invoice.amount_cents * 0.015 * fullMonths);
  return Math.min(fee, invoice.amount_cents);
}
