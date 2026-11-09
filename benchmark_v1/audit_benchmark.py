import pandas as pd, numpy as np, csv, re, sys
ok = True
d = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/deseq2_r_results.csv', index_col=0).dropna(subset=['padj'])
d['truth'] = np.where((d['padj'] < 0.05) & (d['log2FoldChange'] >= 1), 'UP', np.where((d['padj'] < 0.05) & (d['log2FoldChange'] <= -1), 'DOWN', 'NO_CHANGE'))
cases = pd.read_csv('classification_cases.csv')
bad = 0
for _, c in cases.iterrows():
    src = d.loc[c['index']]
    band = 'positive' if src['truth'] != 'NO_CHANGE' else ('borderline' if (0.03 <= src['padj'] <= 0.08) or (0.85 <= abs(src['log2FoldChange']) <= 1.15) else 'clear')
    if src['truth'] != c['truth'] or band != c['band'] or abs(src['padj'] - c['padj']) > 1e-12: bad += 1
print(f'classification audit: {len(cases)} cases, mismatches: {bad}')
ok &= (bad == 0)
items = list(csv.DictReader(open('verification_items.csv')))
def nums(s): return sorted(re.findall(r'-?\d+\.?\d*(?:e-?\d+)?', s))
mism = 0
for it in items:
    if nums(it['statement_en'].replace(',', '')) != nums(it['statement_jp'].replace(',', '')): mism += 1
print(f'verification audit: {len(items)} items, EN/JP numeric-token mismatches: {mism}')
ok &= (mism == 0)
# truth spot-recomputation for gene items is embedded in construction; pathway truths derive from fgsea rows in evidence:
print('AUDIT', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
