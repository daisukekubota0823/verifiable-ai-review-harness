import sys, csv, json
import numpy as np, pandas as pd
sys.path.insert(0, '/home/hatch/workspace/contract-dev/sem-trial')
sys.path.insert(0, '/home/hatch/workspace/contract-dev/sem-trial/validation')
from validate_synthetic import CONDITIONS, render, match_objects
from analyze_sem import PARAMS, object_table, segment
# Benchmark domain 3: microscopy (SEM) quantification judgments.
# 154 synthetic images (7 conditions x 22 replicates, seeds offset +500000 from the
# original validation so no image is reused). Per-image metrics computed with the
# same pipeline and matching as the original validation.
# Cases (300): QC judgments on all 154 images + 146 verification statements.
# QC criteria (pre-registered here): miss rate <= 0.05, false-positive rate <= 0.05,
# area-fraction absolute error <= 0.5 pp, median diameter relative error <= 0.05.
# Borderline: any metric within margin (0.01 / 0.01 / 0.1 pp / 0.01) of its line.
SEED_OFF = 500000
rows = []
for ci, cond in enumerate(CONDITIONS):
    name, polarity = cond[0], cond[1]
    for rep in range(22):
        rng = np.random.default_rng(SEED_OFF + 1000 + 97 * ci + rep)
        img, true_mask, truth = render(rng, cond)
        image_id = f"{name}_b{rep + 1}"
        seg = segment(img.astype(np.float32), polarity, PARAMS)
        detected = object_table(seg, 1.0, image_id, name, PARAMS)
        if len(detected): detected = detected[~detected['touches_border']].reset_index(drop=True)
        pairs, missed, fps = match_objects(truth, detected)
        errs = [abs(float(detected.loc[di, 'equiv_diameter_px']) - float(truth[ti]['equiv_diameter_px'])) / float(truth[ti]['equiv_diameter_px']) for ti, di in pairs]
        af_true = float(true_mask.mean()); af_est = float(seg['mask'].mean())
        n_true = len(truth)
        rows.append({'image_id': image_id, 'condition': name, 'n_true': n_true,
                     'n_detected': int(len(detected)), 'n_missed': len(missed), 'n_fp': len(fps),
                     'miss_rate': round(len(missed) / n_true, 4), 'fp_rate': round(len(fps) / n_true, 4),
                     'area_fraction_true_pct': round(af_true * 100, 3), 'area_fraction_est_pct': round(af_est * 100, 3),
                     'area_fraction_abs_error_pp': round(abs(af_est - af_true) * 100, 4),
                     'diameter_median_abs_rel_error': round(float(np.median(errs)) if errs else 0.0, 4)})
df = pd.DataFrame(rows)
def qc(r):
    checks = [r['miss_rate'] <= 0.05, r['fp_rate'] <= 0.05, r['area_fraction_abs_error_pp'] <= 0.5, r['diameter_median_abs_rel_error'] <= 0.05]
    margins = [abs(r['miss_rate'] - 0.05) <= 0.01, abs(r['fp_rate'] - 0.05) <= 0.01, abs(r['area_fraction_abs_error_pp'] - 0.5) <= 0.1, abs(r['diameter_median_abs_rel_error'] - 0.05) <= 0.01]
    return ('PASS' if all(checks) else 'FAIL'), ('borderline' if any(margins) else 'clear')
df['truth'], df['band'] = zip(*df.apply(qc, axis=1))
df.to_csv('micro_qc_cases.csv', index=False)
from collections import Counter
print('QC cases:', len(df), Counter(zip(df['truth'], df['band'])))
# verification statements: 146, half supported, half with one controlled fault
rng = np.random.default_rng(20261122)
items = []
sample = df.sample(146, random_state=20261122)
for j, (_, r) in enumerate(sample.iterrows()):
    ts = (j % 2 == 0)
    kind = ['count', 'area', 'diameter'][j % 3]
    ev = (f"Image {r['image_id']} (condition {r['condition']}): true objects = {r['n_true']}, detected = {r['n_detected']}, "
          f"missed = {r['n_missed']}, false positives = {r['n_fp']}, true area fraction = {r['area_fraction_true_pct']}%, "
          f"estimated area fraction = {r['area_fraction_est_pct']}%, median diameter relative error = {r['diameter_median_abs_rel_error']}")
    if kind == 'count':
        val = r['n_detected'] if ts else int(df.sample(1, random_state=20261122 + j).iloc[0]['n_detected'])
        if not ts and val == r['n_detected']: val = r['n_detected'] + 3
        en = f"For image {r['image_id']}, the pipeline detected {val} objects."
        jp = f"画像 {r['image_id']} について、パイプラインは {val} 個の対象を検出した。"
    elif kind == 'area':
        val = r['area_fraction_est_pct'] if ts else round(r['area_fraction_est_pct'] * 1.2, 3)
        en = f"For image {r['image_id']}, the estimated area fraction was {val}%."
        jp = f"画像 {r['image_id']} について、推定された面積分率は {val}% であった。"
    else:
        val = r['n_missed'] if ts else r['n_missed'] + 2
        en = f"For image {r['image_id']}, the pipeline missed {val} of the {r['n_true']} true objects."
        jp = f"画像 {r['image_id']} について、パイプラインは真の対象 {r['n_true']} 個のうち {val} 個を見逃した。"
    items.append({'kind': kind, 'evidence': ev, 'statement_en': en, 'statement_jp': jp,
                  'truth': 'SUPPORTED' if ts else 'CONTRADICTED', 'band': r['band']})
with open('micro_verification_items.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind','evidence','statement_en','statement_jp','truth','band'])
    w.writeheader(); w.writerows(items)
print('verification items:', len(items), Counter(i['truth'] for i in items))
json.dump({'seed_offset': SEED_OFF, 'qc_cases': len(df), 'verification_items': len(items)}, open('build_info.json', 'w'), indent=1)
