import sys, os, csv, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/contract-dev/methods-pilot')
from dose_response import four_pl, fit_4pl, bootstrap_ic50_ci, assess_fit, QUALITY_CRITERIA
from multiprocessing import Pool
# Benchmark domain 2: dose-response fit quality-control judgments.
# Judgment: does this 4PL fit pass the pre-registered quality criteria (all five)?
# Truth: mechanical, from assess_fit on the same metrics shown to the judge.
# Borderline: any continuous metric within its margin of the threshold
# (CI width +-0.05 of 0.5; pseudo-R2 +-0.02 of 0.80; outlier fraction +-0.03 of 0.20;
# bootstrap success +-0.05 of 0.80). Quotas: 150 clear PASS / 90 clear FAIL / 60 borderline.
SEED = 20261121
DOSES = np.logspace(-3, 2, 8)
LOG_DOSES = np.log10(DOSES)
TRUE_ICS = [0.3, 1.0, 3.0]
SCEN = [(rep, cv) for rep in (3, 6) for cv in (0.10, 0.20, 0.30)]
def one(arg):
    idx, scen_idx = arg
    rng = np.random.default_rng(SEED + idx)
    rep, cv = SCEN[scen_idx]
    tic = TRUE_ICS[idx % len(TRUE_ICS)]
    y_true = four_pl(LOG_DOSES, 0.05, 1.00, np.log10(tic), 1.2)
    dose_all, y_all = [], []
    for d, yt in zip(DOSES, y_true):
        y_obs = np.clip(rng.normal(yt, cv * max(yt, 0.05), size=rep), 0.0, None)
        dose_all.extend([d] * rep); y_all.extend(y_obs)
    dose_all = np.array(dose_all); y_all = np.array(y_all)
    fit = fit_4pl(dose_all, y_all)
    ci = bootstrap_ic50_ci(dose_all, y_all, n_boot=200, seed=SEED + 500000 + idx)
    qc = assess_fit(fit, ci)
    c = QUALITY_CRITERIA
    margins = (abs(qc['ci_log10_width'] - c['max_ci_log10_width']) <= 0.05 or
               abs(fit['pseudo_r2'] - c['min_pseudo_r2']) <= 0.02 or
               abs(qc['outlier_fraction'] - c['max_outlier_fraction']) <= 0.03 or
               abs(ci['success_rate'] - c['min_bootstrap_success_rate']) <= 0.05)
    band = 'borderline' if margins else 'clear'
    return {'idx': idx, 'replicates': rep, 'cv': cv, 'true_ic50': tic,
            'ic50_est': round(float(fit['ic50']), 4), 'hill': round(float(fit['hill']), 3),
            'converged': bool(fit['converged']), 'pseudo_r2': round(float(fit['pseudo_r2']), 4),
            'ci_low': round(float(ci['ic50_ci_low']), 4), 'ci_high': round(float(ci['ic50_ci_high']), 4),
            'ci_log10_width': round(float(qc['ci_log10_width']), 4),
            'boot_success': round(float(ci['success_rate']), 3),
            'outlier_fraction': round(float(qc['outlier_fraction']), 4),
            'truth': 'PASS' if qc['passed'] else 'FAIL', 'band': band}
if __name__ == '__main__':
    quota = {('PASS', 'clear'): 150, ('FAIL', 'clear'): 90}
    border_target = 60
    got = {k: [] for k in quota}; border = []
    idx = 0
    def pick_scen():
        need_fail = len(got[('FAIL', 'clear')]) < 90
        need_bord = len(border) < border_target
        if need_fail and (not need_bord or idx % 2 == 0): return 2
        if need_bord: return 1 if idx % 2 else 4
        return 3
    with Pool(3) as pool:
        while (len(got[('PASS', 'clear')]) < 150 or len(got[('FAIL', 'clear')]) < 90 or len(border) < border_target) and idx < 6000:
            batch = [(idx + j, pick_scen()) for j in range(24)]; idx += 24
            for r in pool.map(one, batch):
                key = (r['truth'], r['band'])
                if r['band'] == 'borderline':
                    if len(border) < border_target: border.append(r)
                elif key in quota and len(got[key]) < quota[key]:
                    got[key].append(r)
            print(f'attempts {idx}: clear PASS {len(got[("PASS","clear")])}/150, clear FAIL {len(got[("FAIL","clear")])}/90, borderline {len(border)}/60', flush=True)
    rows = got[('PASS', 'clear')] + got[('FAIL', 'clear')] + border
    rng = np.random.default_rng(SEED)
    rng.shuffle(rows)
    with open('dose_cases.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print('BUILT', len(rows), Counter((r['truth'], r['band']) for r in rows))
    json.dump({'seed': SEED, 'n': len(rows), 'criteria': QUALITY_CRITERIA,
               'note': 'truth from assess_fit (pre-registered criteria of dose_response.py); curves synthetic, true IC50 in {0.3, 1.0, 3.0} uM'}, open('build_info.json', 'w'), indent=1, default=str)
