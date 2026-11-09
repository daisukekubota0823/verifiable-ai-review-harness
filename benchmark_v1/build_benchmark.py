import pandas as pd, numpy as np, csv, json
# Benchmark v1 (RNA-seq domain), construction fixed in SPEC.md.
# 600 classification cases (positive 300 / borderline 120 / clear-negative 180 = 5:2:3),
# 120 verification statements (60 supported / 60 contradicted), each in EN and JP versions
# with identical values and ground truth. Seed 20261120 (distinct from the pilot samples).
SEED = 20261120
d = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/deseq2_r_results.csv', index_col=0).dropna(subset=['padj'])
d['truth'] = np.where((d['padj'] < 0.05) & (d['log2FoldChange'] >= 1), 'UP', np.where((d['padj'] < 0.05) & (d['log2FoldChange'] <= -1), 'DOWN', 'NO_CHANGE'))
def band(r):
    if r['truth'] != 'NO_CHANGE': return 'positive'
    if (0.03 <= r['padj'] <= 0.08) or (0.85 <= abs(r['log2FoldChange']) <= 1.15): return 'borderline'
    return 'clear'
d['band'] = d.apply(band, axis=1)
pos = d[d['band'] == 'positive'].sample(300, random_state=SEED)
bor = d[d['band'] == 'borderline'].sample(120, random_state=SEED)
clr = d[d['band'] == 'clear'].sample(180, random_state=SEED)
cases = pd.concat([pos, bor, clr]).sample(frac=1, random_state=SEED).reset_index()
cases_out = cases[['index', 'baseMean', 'log2FoldChange', 'padj', 'truth', 'band']]
cases_out.to_csv('classification_cases.csv', index=False)
print('classification:', len(cases_out), cases_out['band'].value_counts().to_dict(), cases_out['truth'].value_counts().to_dict())
# verification statements: reuse the audited v2 construction at larger scale
pw = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/fgsea_results.csv')
items = []
pw_sig = pw[pw['padj'] < 0.05]; pw_non = pw[pw['padj'] >= 0.05]
picks = pd.concat([pw_sig.sample(30, random_state=SEED), pw_non.sample(30, random_state=SEED)])
for j, (_, r) in enumerate(picks.iterrows()):
    ts = (j % 2 == 0); sig = r['padj'] < 0.05
    direction = 'up' if r['NES'] > 0 else 'down'
    nes_show, dir_show, form_sig = r['NES'], direction, sig
    if not ts:
        fault = j % 3
        if fault == 0 and sig: dir_show = 'down' if direction == 'up' else 'up'; nes_show = -r['NES']
        elif fault == 0: form_sig = True
        elif fault == 1: form_sig = not sig
        else:
            other = pw.sample(1, random_state=SEED + j).iloc[0]; nes_show = other['NES']
            if not sig: form_sig = False
    en = (f"In the pathway analysis, the {r['library']} pathway '{r['pathway']}' is significantly {dir_show}-regulated (NES = {nes_show:.2f}, FDR = {r['padj']:.3g})." if form_sig else
          f"In the pathway analysis, the {r['library']} pathway '{r['pathway']}' shows no significant change (NES = {nes_show:.2f}, FDR = {r['padj']:.3g}).")
    dj = '上昇' if dir_show == 'up' else '低下'
    jp = (f"パスウェイ解析において、{r['library']}パスウェイ「{r['pathway']}」は有意に{dj}している（NES = {nes_show:.2f}、FDR = {r['padj']:.3g}）。" if form_sig else
          f"パスウェイ解析において、{r['library']}パスウェイ「{r['pathway']}」に有意な変化はない（NES = {nes_show:.2f}、FDR = {r['padj']:.3g}）。")
    distr = pw.sample(2, random_state=SEED + 100 + j)
    ev = "\n".join(f"- [{x.library}] {x.pathway}: NES = {x.NES:.2f}, FDR = {x.padj:.3g}" for x in pd.concat([pd.DataFrame([r]), distr]).sample(frac=1, random_state=SEED + j).itertuples())
    items.append({'kind': 'pathway', 'evidence': ev, 'statement_en': en, 'statement_jp': jp, 'truth': 'SUPPORTED' if ts else 'CONTRADICTED', 'band': 'borderline' if 0.03 <= r['padj'] <= 0.08 else 'clear'})
deg = d[d['band'] == 'positive']
nondeg = d[d['truth'] == 'NO_CHANGE']
picks_g = pd.concat([deg.sample(30, random_state=SEED), nondeg.sample(30, random_state=SEED)])
for j, (gid, r) in enumerate(picks_g.iterrows()):
    ts = (j % 2 == 0); is_deg = r['truth'] in ('UP', 'DOWN')
    direction = 'up' if r['log2FoldChange'] > 0 else 'down'
    lfc_show, dir_show, form_deg = r['log2FoldChange'], direction, is_deg
    if not ts:
        fault = j % 3
        if fault == 0 and is_deg: dir_show = 'down' if direction == 'up' else 'up'; lfc_show = -r['log2FoldChange']
        elif fault == 0: form_deg = True
        elif fault == 1: form_deg = not is_deg
        else:
            other = d.sample(1, random_state=SEED + j).iloc[0]; lfc_show = other['log2FoldChange']
            if not is_deg: form_deg = False
    en = (f"Gene {gid} is a significantly changed gene, {dir_show}-regulated (log2FoldChange = {lfc_show:.3g}, padj = {r['padj']:.3g})." if form_deg else
          f"Gene {gid} shows no significant change (log2FoldChange = {lfc_show:.3g}, padj = {r['padj']:.3g}).")
    dj = '上昇' if dir_show == 'up' else '低下'
    jp = (f"遺伝子 {gid} は有意に変化した遺伝子であり、{dj}している（log2FoldChange = {lfc_show:.3g}、padj = {r['padj']:.3g}）。" if form_deg else
          f"遺伝子 {gid} に有意な変化はない（log2FoldChange = {lfc_show:.3g}、padj = {r['padj']:.3g}）。")
    distr = d.sample(2, random_state=SEED + 200 + j)
    ev = "\n".join(f"- {i}: baseMean = {x.baseMean:.4g}, log2FoldChange = {x.log2FoldChange:.3g}, padj = {x.padj:.3g}" for i, x in pd.concat([pd.DataFrame([r]), distr]).sample(frac=1, random_state=SEED + j).iterrows())
    border = (0.03 <= r['padj'] <= 0.08) or (0.85 <= abs(r['log2FoldChange']) <= 1.15)
    items.append({'kind': 'gene', 'evidence': ev, 'statement_en': en, 'statement_jp': jp, 'truth': 'SUPPORTED' if ts else 'CONTRADICTED', 'band': 'borderline' if border else 'clear'})
with open('verification_items.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind','evidence','statement_en','statement_jp','truth','band'])
    w.writeheader(); w.writerows(items)
from collections import Counter
print('verification:', len(items), Counter(i['truth'] for i in items))
json.dump({'seed': SEED, 'classification_n': 600, 'verification_n': 120, 'source': 'GEO GSE264217, DESeq2 1.42.0 / fgsea'}, open('build_info.json', 'w'), indent=1)
