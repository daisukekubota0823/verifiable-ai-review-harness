import pandas as pd
# Japanese variant of pilot 2: identical picks/faults as claims.csv (same seed & construction order);
# statements rendered in Japanese, entity names and values unchanged.
seed = 20261108
pw = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/fgsea_results.csv')
gn = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/deseq2_r_results.csv', index_col=0).dropna(subset=['padj'])
items = []
def fmt_ev_pw(rows):
    return "\n".join(f"- [{r.library}] {r.pathway}: NES = {r.NES:.2f}, FDR = {r.padj:.3g}" for r in rows.itertuples())
def fmt_ev_gn(rows):
    return "\n".join(f"- {i}: baseMean = {r.baseMean:.4g}, log2FoldChange = {r.log2FoldChange:.3g}, padj = {r.padj:.3g}" for i, r in rows.iterrows())
pw_sig = pw[pw['padj'] < 0.05]; pw_non = pw[pw['padj'] >= 0.05]
picks = pd.concat([pw_sig.sample(21, random_state=seed), pw_non.sample(21, random_state=seed)])
for j, (_, r) in enumerate(picks.iterrows()):
    truth_supported = (j % 2 == 0)
    sig = r['padj'] < 0.05
    direction = '上昇' if r['NES'] > 0 else '低下'
    nes_show, dir_show, form_sig = r['NES'], direction, sig
    if not truth_supported:
        fault = j % 3
        if fault == 0 and sig: dir_show = '低下' if direction == '上昇' else '上昇'; nes_show = -r['NES']
        elif fault == 0: form_sig = True
        elif fault == 1: form_sig = not sig
        else:
            other = pw.sample(1, random_state=seed + j).iloc[0]; nes_show = other['NES']
            if not sig: form_sig = False
    if form_sig:
        stmt = f"パスウェイ解析において、{r['library']}パスウェイ「{r['pathway']}」は有意に{dir_show}している（NES = {nes_show:.2f}、FDR = {r['padj']:.3g}）。"
    else:
        stmt = f"パスウェイ解析において、{r['library']}パスウェイ「{r['pathway']}」に有意な変化はない（NES = {nes_show:.2f}、FDR = {r['padj']:.3g}）。"
    distr = pw.sample(2, random_state=seed + 100 + j)
    ev = fmt_ev_pw(pd.concat([pd.DataFrame([r]), distr]).sample(frac=1, random_state=seed + j))
    border = 0.03 <= r['padj'] <= 0.08
    items.append({'kind': 'pathway', 'evidence': ev, 'statement': stmt, 'truth': 'SUPPORTED' if truth_supported else 'CONTRADICTED', 'band': 'borderline' if border else 'clear'})
deg = gn[(gn['padj'] < 0.05) & (gn['log2FoldChange'].abs() >= 1)]
nondeg = gn[~((gn['padj'] < 0.05) & (gn['log2FoldChange'].abs() >= 1))]
picks_g = pd.concat([deg.sample(21, random_state=seed), nondeg.sample(21, random_state=seed)])
for j, (gid, r) in enumerate(picks_g.iterrows()):
    truth_supported = (j % 2 == 0)
    is_deg = (r['padj'] < 0.05) and abs(r['log2FoldChange']) >= 1
    direction = '上昇' if r['log2FoldChange'] > 0 else '低下'
    lfc_show, dir_show, form_deg = r['log2FoldChange'], direction, is_deg
    if not truth_supported:
        fault = j % 3
        if fault == 0 and is_deg: dir_show = '低下' if direction == '上昇' else '上昇'; lfc_show = -r['log2FoldChange']
        elif fault == 0: form_deg = True
        elif fault == 1: form_deg = not is_deg
        else:
            other = gn.sample(1, random_state=seed + j).iloc[0]; lfc_show = other['log2FoldChange']
            if not is_deg: form_deg = False
    if form_deg:
        stmt = f"遺伝子 {gid} は有意に変化した遺伝子であり、{dir_show}している（log2FoldChange = {lfc_show:.3g}、padj = {r['padj']:.3g}）。"
    else:
        stmt = f"遺伝子 {gid} に有意な変化はない（log2FoldChange = {lfc_show:.3g}、padj = {r['padj']:.3g}）。"
    distr = gn.sample(2, random_state=seed + 200 + j)
    ev = fmt_ev_gn(pd.concat([pd.DataFrame([r]), distr]).sample(frac=1, random_state=seed + j))
    border = (0.03 <= r['padj'] <= 0.08) or (0.85 <= abs(r['log2FoldChange']) <= 1.15)
    items.append({'kind': 'gene', 'evidence': ev, 'statement': stmt, 'truth': 'SUPPORTED' if truth_supported else 'CONTRADICTED', 'band': 'borderline' if border else 'clear'})
import csv
with open('claims_jp.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind','evidence','statement','truth','band'])
    w.writeheader(); w.writerows(items)
from collections import Counter
print('items:', len(items), Counter(i['truth'] for i in items))
