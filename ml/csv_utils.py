import csv
from io import TextIOWrapper
from typing import List

def read_csv_features(uploaded_file) -> List[float]:
    """
    Supports:
    - Single row with 80 columns
    - Single column with 80 rows
    - Values separated by commas
    """

    # Django uploads file in binary mode; wrap to text
    text_file = TextIOWrapper(uploaded_file.file, encoding="utf-8", newline="")
    reader = csv.reader(text_file)

    rows = [row for row in reader if row and any(cell.strip() for cell in row)]

    if not rows:
        raise ValueError("CSV is empty.")

    # Case 1: single row with many columns
    if len(rows) == 1 and len(rows[0]) > 1:
        return [float(x.strip()) for x in rows[0] if x.strip()]

    # Case 2: many rows, single column
    if all(len(r) == 1 for r in rows):
        return [float(r[0].strip()) for r in rows if r[0].strip()]

    # Case 3: fallback: flatten everything
    flat = []
    for r in rows:
        for cell in r:
            c = cell.strip()
            if c:
                flat.append(float(c))
    return flat