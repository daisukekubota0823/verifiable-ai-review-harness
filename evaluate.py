import csv, json
from collections import Counter
rows = list(csv.DictReader(open('results_raw.csv')))
def metrics(rs):
    n = len(rs); agree = sum(1 for r in rs if r['pred'] == r['truth'])
    labels = ['UP','DOWN','NO_CHANGE']
    po = agree / n
    pe = 0.0
    tc = Counter(r['truth'] for r in rs); pc = Counter(r['pred'] for r in rs)
    for l in labels: pe += (tc[l]/n) * (pc[l]/n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    pos = [r for r in rs if r['truth'] in ('UP','DOWN')]
    miss = (sum(1 for r in pos if r['pred'] != r['truth']) / len(pos)) if pos else None
    direrr = sum(1 for r in pos if r['pred'] in ('UP','DOWN') and r['pred'] != r['truth'])
    neg = [r for r in rs if r['truth'] == 'NO_CHANGE']
    fd = (sum(1 for r in neg if r['pred'] in ('UP','DOWN')) / len(neg)) if neg else None
    return {'n': n, 'agreement': round(po,4), 'kappa': round(kappa,4), 'miss_rate': (round(miss,4) if miss is not None else None), 'direction_errors': direrr, 'false_detection_rate': (round(fd,4) if fd is not None else None)}
out = {
  'all_cases': metrics(rows),
  'borderline_band': metrics([r for r in rows if r['band']=='borderline']),
  'auto_judged_subset': metrics([r for r in rows if r['band']!='borderline']),
  'coverage_auto_judged': round(sum(1 for r in rows if r['band']!='borderline')/len(rows), 4),
  'parse_fails': sum(1 for r in rows if r['pred'].startswith('PARSE_FAIL')),
  'confusion': Counter((r['truth'], r['pred']) for r in rows).most_common()
}
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open('metrics.json','w'), indent=1, ensure_ascii=False)
