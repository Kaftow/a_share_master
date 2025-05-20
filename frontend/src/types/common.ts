export type ISODateString = string;
export type ISODateTimeString = string;
export interface TableRow {
  key: string;
  label: string;
  value: string | number | null | undefined;
}
