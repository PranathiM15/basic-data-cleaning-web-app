"""Reusable Pandas-based cleaning functions for the CLEARCUT Data Cleaning Lab."""
from __future__ import annotations

import io
from typing import Any

import pandas as pd

MISSING_TOKENS = {"", "na", "n/a", "nan", "null", "none", "missing", "not available", "-", "?"}
IDENTIFIER_HINTS = ("id", "identifier", "phone", "mobile", "postal", "postcode", "zip", "roll no", "roll_no")


def _unique_column_names(columns: list[Any]) -> list[str]:
    """Trim column names and make blanks/duplicates unambiguous."""
    result: list[str] = []
    counts: dict[str, int] = {}
    for index, item in enumerate(columns, start=1):
        name = str(item).strip() or f"column_{index}"
        counts[name] = counts.get(name, 0) + 1
        if counts[name] > 1:
            name = f"{name}_{counts[name]}"
        result.append(name)
    return result


def _display(value: Any) -> str:
    if pd.isna(value):
        return ""
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (TypeError, ValueError):
            pass
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def clean_dataframe(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Clean a DataFrame and return the cleaned data plus a human-readable audit."""
    df = dataframe.copy()
    df.columns = _unique_column_names(list(df.columns))
    original_rows = int(len(df))
    original_columns = int(len(df.columns))

    # Trim surrounding whitespace and turn common placeholders into real missing values.
    for column in df.columns:
        series = df[column].astype("string").str.strip()
        df[column] = series.mask(series.str.lower().isin(MISSING_TOKENS))

    missing_before = int(df.isna().sum().sum())
    df = df.dropna(how="all").copy()
    empty_rows_removed = original_rows - len(df)

    # Deduplicate after trimming so whitespace-only differences don't hide duplicates.
    duplicates_removed = int(df.duplicated(keep="first").sum())
    df = df.drop_duplicates(keep="first").copy()

    type_changes: list[dict[str, str]] = []
    for column in df.columns:
        series = df[column]
        non_missing = series.dropna()
        if non_missing.empty:
            continue

        normalized = non_missing.astype(str).str.strip().str.lower()
        if normalized.isin({"true", "false", "yes", "no", "y", "n"}).all():
            bool_map = {"true": True, "yes": True, "y": True, "false": False, "no": False, "n": False}
            df[column] = series.map(lambda value: bool_map.get(str(value).strip().lower(), pd.NA) if pd.notna(value) else pd.NA).astype("boolean")
            type_changes.append({"column": column, "from": "text", "to": "boolean"})
            continue

        name_lower = column.lower()
        if any(hint in name_lower for hint in IDENTIFIER_HINTS):
            # Keep identifiers as text, preserving meaningful leading zeroes.
            continue

        if any(token in name_lower for token in ("date", "time")):
            date_values = pd.to_datetime(series, errors="coerce", format="mixed")
            valid_count = int(series.notna().sum())
            parsed_count = int(date_values[series.notna()].notna().sum())
            if valid_count and parsed_count / valid_count >= 0.8:
                missing_before += valid_count - parsed_count
                df[column] = date_values
                type_changes.append({"column": column, "from": "text", "to": "date/time"})
                continue

        # Accommodate comma-separated numbers and common currency/percentage symbols.
        numeric_text = series.astype("string").str.strip()
        numeric_text = numeric_text.str.replace(r"^[₹$€£]\s*", "", regex=True)
        numeric_text = numeric_text.str.replace(",", "", regex=False).str.replace("%", "", regex=False)
        numeric_values = pd.to_numeric(numeric_text, errors="coerce")
        valid_count = int(series.notna().sum())
        parsed_count = int(numeric_values[series.notna()].notna().sum())
        if valid_count and parsed_count / valid_count >= 0.8:
            missing_before += valid_count - parsed_count
            df[column] = numeric_values
            type_changes.append({"column": column, "from": "text", "to": "number"})

    # Fill missing values: numeric median; otherwise most common value; all-empty => Unknown.
    for column in df.columns:
        series = df[column]
        if not series.isna().any():
            continue
        if pd.api.types.is_numeric_dtype(series):
            median = series.median()
            df[column] = series.astype("float64").fillna(float(median) if pd.notna(median) else 0.0)
        elif pd.api.types.is_datetime64_any_dtype(series):
            modes = series.mode(dropna=True)
            fill_value = modes.iloc[0] if not modes.empty else pd.Timestamp("1970-01-01")
            df[column] = series.fillna(fill_value)
        else:
            modes = series.mode(dropna=True)
            fill_value = modes.iloc[0] if not modes.empty else "Unknown"
            df[column] = series.fillna(fill_value)

    missing_after = int(df.isna().sum().sum())
    columns = list(df.columns)
    preview_limit = 8
    preview_rows = [[_display(value) for value in row] for row in df.head(preview_limit).itertuples(index=False, name=None)]
    schema = [
        {
            "column": column,
            "dtype": str(df[column].dtype),
            "missing": int(df[column].isna().sum()),
            "sample": _display(df[column].iloc[0]) if len(df) else "",
        }
        for column in columns
    ]

    report_lines = [
        "CLEARCUT DATA CLEANING LAB — CLEANING AUDIT",
        "=" * 48,
        f"Original rows: {original_rows}",
        f"Cleaned rows: {len(df)}",
        f"Columns: {original_columns}",
        f"Missing cells before cleaning: {missing_before}",
        f"Missing cells after cleaning: {missing_after}",
        f"Duplicate rows removed: {duplicates_removed}",
        f"Completely empty rows removed: {empty_rows_removed}",
        "",
        "CLEANING RULES APPLIED",
        "1. Trimmed surrounding spaces in cell values and column names.",
        "2. Treated blank cells and common placeholders (NA, N/A, null, -, ?) as missing.",
        "3. Removed completely empty rows and duplicate rows (kept the first occurrence).",
        "4. Converted recognisable boolean, date/time, and numeric columns to suitable types.",
        "5. Filled numeric gaps with the column median; other gaps with the most common value.",
        "   If a column had no usable value, used Unknown.",
        "6. Kept identifier-like columns as text to preserve leading zeroes.",
        "",
        "DATA-TYPE CORRECTIONS",
    ]
    if type_changes:
        report_lines.extend([f"- {item['column']}: {item['from']} -> {item['to']}" for item in type_changes])
    else:
        report_lines.append("- No data-type corrections were needed.")
    report_lines.extend(["", "FINAL COLUMN TYPES"])
    report_lines.extend([f"- {column}: {df[column].dtype}" for column in columns])
    report_lines.extend(["", "Note: Review the cleaned file before using it for high-stakes decisions."])

    return {
        "cleaned_dataframe": df,
        "cleaned_csv": df.to_csv(index=False, lineterminator="\n"),
        "summary": {
            "original_rows": original_rows,
            "cleaned_rows": int(len(df)),
            "columns": original_columns,
            "missing_before": missing_before,
            "missing_after": missing_after,
            "duplicates_removed": duplicates_removed,
            "empty_rows_removed": empty_rows_removed,
            "type_changes": type_changes,
        },
        "columns": columns,
        "preview_rows": preview_rows,
        "schema": schema,
        "report_text": "\n".join(report_lines) + "\n",
    }


def clean_csv_text(csv_text: str) -> dict[str, Any]:
    """Parse UTF-8 CSV text and clean it, preserving input values as text initially."""
    if not csv_text or not csv_text.strip():
        raise ValueError("The CSV file is empty. Choose a CSV containing a header and at least one row.")
    try:
        dataframe = pd.read_csv(io.StringIO(csv_text), dtype=str, keep_default_na=False, na_filter=False)
    except Exception as exc:
        raise ValueError(f"Could not read this CSV. Check that it is a valid comma-separated file. Details: {exc}") from exc
    if len(dataframe.columns) == 0:
        raise ValueError("No columns were found. The first row should contain column headings.")
    return clean_dataframe(dataframe)
