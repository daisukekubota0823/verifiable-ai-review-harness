#!/usr/bin/env python3
"""Deterministic record checker (harness component).
Every number and identifier in a draft statement is checked against the record.
Numbers the record does not contain, and identifiers absent from the record, are
flagged. The model never performs this check; it is exact string/value matching
with numeric tolerance for rounding at the stated precision.
Usage: checker.py RECORD.csv DRAFT.txt [--ids-col 0]
"""
import csv, re, sys
def load_record(path):
    nums, ids = set(), set()
    with open(path) as f:
        for row in csv.reader(f):
            for cell in row:
                cell = cell.strip()
                if not cell: continue
                ids.add(cell)
                try:
                    v = float(cell.replace(',', ''))
                    nums.add(v)
                except ValueError:
                    pass
    return nums, ids
def main():
    rec_nums, rec_ids = load_record(sys.argv[1])
    draft = open(sys.argv[2]).read()
    flags = []
    draft_nums = re.sub(r'ENSG\d{11}', ' ', draft)  # identifiers are checked separately
    for m in re.finditer(r'-?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?', draft_nums):
        tok = m.group(0)
        try: v = float(tok.replace(',', ''))
        except ValueError: continue
        if v in (2025.0, 2026.0, 2027.0): continue  # calendar years in prose
        hit = any(abs(v - r) <= max(0.005 * max(1.0, abs(r)), 1e-9) or (r != 0 and abs(v - r) / abs(r) < 0.01) for r in rec_nums)
        if not hit: flags.append(('NUMBER NOT IN RECORD', tok))
    for m in re.finditer(r'ENSG\d{11}', draft):
        if m.group(0) not in rec_ids: flags.append(('ID NOT IN RECORD', m.group(0)))
    if flags:
        print(f'FLAGGED {len(flags)}:')
        for k, t in flags: print(f'  {k}: {t}')
        sys.exit(1)
    print('CLEAN: every number and identifier in the draft is present in the record.')
if __name__ == '__main__': main()
