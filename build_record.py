import pandas as pd, json
d = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/deseq2_r_results.csv', index_col=0).dropna(subset=['padj'])
pw = pd.read_csv('/home/hatch/workspace/aist-p0f18c15/example2/fgsea_results.csv')
deg = d[(d['padj'] < 0.05) & (d['log2FoldChange'].abs() >= 1)]
top_up = deg[deg['log2FoldChange'] > 0].nlargest(5, 'log2FoldChange')
top_dn = deg[deg['log2FoldChange'] < 0].nsmallest(5, 'log2FoldChange')
sig_pw = pw[pw['padj'] < 0.05].copy(); sig_pw['absNES'] = sig_pw['NES'].abs()
top_pw = sig_pw.nlargest(8, 'absNES')
rec = {
 'experiment': 'Human kidney organoids, LY294002 (PI3K inhibitor) 10 uM, 48 h, vs control; 2 conditions x 3 replicates; RNA-seq analyzed with DESeq2 1.42.0',
 'genes_tested': int(len(d)),
 'deg_up': int((deg['log2FoldChange'] > 0).sum()), 'deg_down': int((deg['log2FoldChange'] < 0).sum()),
 'top_up': [(i, round(r.log2FoldChange, 2), float(f"{r.padj:.2g}")) for i, r in top_up.iterrows()],
 'top_down': [(i, round(r.log2FoldChange, 2), float(f"{r.padj:.2g}")) for i, r in top_dn.iterrows()],
 'pathways_significant': int(len(sig_pw)),
 'top_pathways': [(f"[{r.library}] {r.pathway}", round(r.NES, 2), float(f"{r.padj:.2g}")) for r in top_pw.itertuples()],
}
lines = [f"Experiment: {rec['experiment']}",
         f"Genes tested: {rec['genes_tested']}. Significant changes (padj < 0.05 and |log2FoldChange| >= 1): {rec['deg_up']} up, {rec['deg_down']} down.",
         "Top up-regulated genes (Ensembl ID, log2FoldChange, padj): " + "; ".join(f"{g} ({l:+.2f}, {p:.2g})" for g, l, p in rec['top_up']),
         "Top down-regulated genes: " + "; ".join(f"{g} ({l:+.2f}, {p:.2g})" for g, l, p in rec['top_down']),
         f"Pathways significant at FDR < 0.05: {rec['pathways_significant']}. Strongest by |NES| (name, NES, FDR): " + "; ".join(f"{n} ({nes:+.2f}, {p:.2g})" for n, nes, p in rec['top_pathways'])]
open('record.txt', 'w').write("\n".join(lines))
json.dump(rec, open('record.json', 'w'), indent=1)
print("\n".join(lines))
