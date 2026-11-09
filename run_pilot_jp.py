import json, urllib.request, csv, re
PROMPT = """あなたは研究データの評価者です。
ルール: padj が 0.05 未満で log2FoldChange が 1 以上なら UP、padj が 0.05 未満で log2FoldChange が -1 以下なら DOWN、それ以外は NO_CHANGE です。
遺伝子 {gid}: baseMean = {bm}、log2FoldChange = {lfc}、padj = {p}。
UP、DOWN、NO_CHANGE のいずれか1語だけで答えてください。"""
def ask(row):
    text = PROMPT.format(gid=row['index'], bm=f"{float(row['baseMean']):.4g}", lfc=f"{float(row['log2FoldChange']):.4g}", p=f"{float(row['padj']):.4g}")
    payload = {"messages": [{"role": "user", "content": text}], "temperature": 0, "max_tokens": 8}
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as r: d = json.load(r)
    out = d['choices'][0]['message']['content'].strip().upper()
    m = re.search(r'\b(UP|DOWN|NO_CHANGE)\b', out)
    return m.group(1) if m else 'PARSE_FAIL:' + out[:30]
rows = list(csv.DictReader(open('cases.csv')))
with open('results_jp.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['index', 'truth', 'band', 'pred'])
    for i, row in enumerate(rows):
        w.writerow([row['index'], row['truth'], row['band'], ask(row)]); f.flush()
        if (i+1) % 50 == 0: print(f'{i+1}/{len(rows)}', flush=True)
print('RUN JP COMPLETE')
