export interface ExportRow {
  orderId: string;
  total: number;
}

/** The big report: every order in a quarter, as CSV. */
export class QuarterlyExport {
  constructor(private readonly rows: ExportRow[]) {}

  toCsv(): string {
    return this.rows.map((row) => `${row.orderId},${row.total}`).join("\n");
  }
}

export const exportFileName = (quarter: string): string => `orders-${quarter}.csv`;
