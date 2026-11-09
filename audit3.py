import re, json
rec = json.load(open('record.json'))
record_text = open('record.txt').read()
# allowed numeric values from the record (as floats), with their printed forms
allowed = set()
for tok in re.findall(r'\d+\.?\d*(?:e-?\d+)?', record_text.replace(',', '')):
    try: allowed.add(float(tok))
    except ValueError: pass
allowed |= {15167.0, 152.0, 436.0, 138.0, 10.0, 48.0, 2.0, 3.0, 0.05, 1.0, 200.0}
def num_supported(x):
    return any(abs(x - a) <= max(0.011, 0.02 * abs(a)) for a in allowed)
def audit(text, label):
    nums = [float(t) for t in re.findall(r'\d+\.?\d*(?:e-?\d+)?', text.replace(',', '')) if not (len(t) <= 4 and float(t) >= 1900 and float(t) <= 2100)]
    bad_nums = [n for n in nums if not num_supported(n)]
    gene_ids = set(re.findall(r'ENSG\d{11}', text))
    bad_genes = [g for g in gene_ids if g not in record_text]
    pw_keys = ['Translation Elongation', 'Peptide Chain Elongation', 'Selenocysteine', 'Translation Termination', 'Viral mRNA Translation', 'Selenoamino Acid', 'Nonsense Mediated Decay', 'SRP-dependent']
    bad_pw = [k for k in pw_keys if k.lower() in text.lower() and k not in record_text]
    print(f"{label}: numbers={len(nums)} unsupported={len(bad_nums)} {bad_nums[:8]} | gene IDs={len(gene_ids)} not-in-record={bad_genes} | pathway mentions checked={len(pw_keys)} bad={bad_pw}")
    return {'numbers': len(nums), 'unsupported_numbers': bad_nums, 'genes_not_in_record': bad_genes, 'pathways_bad': bad_pw}
a = audit(open('draftA.txt').read(), 'Task A (free draft)')
b_text = open('draftB.txt').read().split('Interpretation (model): ')[1]
b = audit(b_text, 'Task B (interpretation only)')
json.dump({'A': a, 'B': b}, open('metrics3.json', 'w'), indent=1, default=str)
