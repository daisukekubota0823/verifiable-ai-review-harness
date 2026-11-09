import csv, json
from collections import Counter
def metrics(rs):
    n = len(rs); po = sum(1 for r in rs if r['pred'] == r['truth']) / n
    tc = Counter(r['truth'] for r in rs); pc = Counter(r['pred'] for r in rs)
    pe = sum((tc[l]/n) * (pc[l]/n) for l in ['UP','DOWN','NO_CHANGE'])
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    pos = [r for r in rs if r['truth'] in ('UP','DOWN')]
    neg = [r for r in rs if r['truth'] == 'NO_CHANGE']
    return {'n': n, 'agreement': round(po,4), 'kappa': round(kappa,4),
            'miss_rate': round(sum(1 for r in pos if r['pred'] != r['truth']) / len(pos), 4) if pos else None,
            'false_detection_rate': round(sum(1 for r in neg if r['pred'] in ('UP','DOWN')) / len(neg), 4) if neg else None}
for name, fn in [('EN', 'results_raw.csv'), ('JP', 'results_jp.csv')]:
    rows = list(csv.DictReader(open(fn)))
    out = {'all': metrics(rows), 'auto_subset': metrics([r for r in rows if r['band'] != 'borderline']),
           'coverage': round(sum(1 for r in rows if r['band'] != 'borderline') / len(rows), 4),
           'parse_fails': sum(1 for r in rows if r['pred'].startswith('PARSE_FAIL'))}
    print(name, json.dumps(out, indent=1))
