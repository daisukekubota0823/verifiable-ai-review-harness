import csv, json
from collections import Counter
rows = list(csv.DictReader(open('results2_raw.csv')))
def metrics(rs):
    n = len(rs); po = sum(1 for r in rs if r['pred'] == r['truth']) / n
    tc = Counter(r['truth'] for r in rs); pc = Counter(r['pred'] for r in rs)
    pe = sum((tc[l]/n) * (pc[l]/n) for l in ['SUPPORTED','CONTRADICTED'])
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    con = [r for r in rs if r['truth'] == 'CONTRADICTED']
    sup = [r for r in rs if r['truth'] == 'SUPPORTED']
    return {'n': n, 'agreement': round(po,4), 'kappa': round(kappa,4),
            'dangerous_miss_rate': round(sum(1 for r in con if r['pred'] == 'SUPPORTED') / len(con), 4) if con else None,
            'false_flag_rate': round(sum(1 for r in sup if r['pred'] == 'CONTRADICTED') / len(sup), 4) if sup else None}
out = {'all': metrics(rows),
       'by_kind': {k: metrics([r for r in rows if r['kind'] == k]) for k in ['pathway','gene']},
       'auto_subset': metrics([r for r in rows if r['band'] != 'borderline']),
       'coverage': round(sum(1 for r in rows if r['band'] != 'borderline') / len(rows), 4),
       'parse_fails': sum(1 for r in rows if r['pred'].startswith('PARSE_FAIL')),
       'confusion': Counter((r['truth'], r['pred']) for r in rows).most_common()}
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open('metrics2.json','w'), indent=1, ensure_ascii=False)
