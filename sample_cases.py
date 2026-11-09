import json, pandas as pd, numpy as np
cfg = json.load(open('config.json'))
df = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/deseq2_r_results.csv', index_col=0)
df = df.dropna(subset=['padj'])
def truth(r):
    if r['padj'] < 0.05 and r['log2FoldChange'] >= 1: return 'UP'
    if r['padj'] < 0.05 and r['log2FoldChange'] <= -1: return 'DOWN'
    return 'NO_CHANGE'
df['truth'] = df.apply(truth, axis=1)
rng = np.random.RandomState(cfg['sampling']['seed'])
pos = df[df['truth'].isin(['UP','DOWN'])]
if len(pos) > 150: pos = pos.sample(150, random_state=cfg['sampling']['seed'])
neg = df[df['truth'] == 'NO_CHANGE'].copy()
border = neg[((neg['padj'] < 0.05) & (neg['log2FoldChange'].abs() >= 0.7) & (neg['log2FoldChange'].abs() < 1.0)) |
             ((neg['padj'] >= 0.05) & (neg['log2FoldChange'].abs() >= 1.0) & (neg['padj'] < 0.2))]
if len(border) > 60: border = border.sample(60, random_state=cfg['sampling']['seed'])
clear = neg.drop(border.index)
clear = clear.sample(90, random_state=cfg['sampling']['seed'])
cases = pd.concat([pos.assign(band='positive'), border.assign(band='borderline'), clear.assign(band='clear')])
cases = cases.sample(frac=1, random_state=cfg['sampling']['seed']).reset_index()
cases.to_csv('cases.csv', index=False)
print('total cases:', len(cases))
print(cases['truth'].value_counts().to_dict())
print(cases['band'].value_counts().to_dict())
