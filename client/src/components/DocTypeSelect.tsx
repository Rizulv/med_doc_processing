import * as React from "react";
import { DOCUMENT_TYPES, type DocumentType } from "@shared/schema";

export type DocTypeChoice = DocumentType | "AUTO";

type Props = {
  value: DocTypeChoice;
  onChange: (v: DocTypeChoice) => void;
};

export default function DocTypeSelect({ value, onChange }: Props) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-medium mb-2">
        Select document type (or let AI decide)
      </label>
      <select
        className="w-full rounded-md border px-3 py-2"
        value={value}
        onChange={(e) => onChange(e.target.value as DocTypeChoice)}
      >
        <option value="AUTO">AUTO — let AI classify</option>
        {DOCUMENT_TYPES.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
      <p className="text-xs text-muted-foreground mt-1">
        Choosing a type can boost accuracy and skip classification later.
      </p>
    </div>
  );
}
