import json, urllib.request, csv, re, sys

PROMPT = """You are the evaluation layer of a research data platform. Apply the stated criteria exactly.

Criteria for one gene's differential-expression result (treated vs control):
- Call UP if padj < 0.05 AND log2FoldChange >= 1.
- Call DOWN if padj < 0.05 AND log2FoldChange <= -1.
- Otherwise call NO_CHANGE.

Gene: {gid}
baseMean: {bm}
log2FoldChange: {lfc}
padj: {padj}

Answer with exactly one word: UP, DOWN, or NO_CHANGE."""

def ask(row):
    text = PROMPT.format(gid=row['index'], bm=f"{float(row['baseMean']):.4g}", lfc=f"{float(row['log2FoldChange']):.4g}", padj=f"{float(row['padj']):.4g}")
    payload = {"messages": [{"role": "user", "content": text}], "temperature": 0, "max_tokens": 8}
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    out = d['choices'][0]['message']['content'].strip().upper()
    m = re.search(r'\b(UP|DOWN|NO_CHANGE)\b', out)
    return m.group(1) if m else 'PARSE_FAIL:' + out[:30]

rows = list(csv.DictReader(open('cases.csv')))
done = set()
try:
    for r in csv.DictReader(open('results_raw.csv')): done.add(r['index'])
except FileNotFoundError:
    pass
mode = 'a' if done else 'w'
with open('results_raw.csv', mode, newline='') as f:
    w = csv.writer(f)
    if not done: w.writerow(['index','truth','band','pred'])
    for i, row in enumerate(rows):
        if row['index'] in done: continue
        pred = ask(row)
        w.writerow([row['index'], row['truth'], row['band'], pred]); f.flush()
        if (i+1) % 25 == 0: print(f'{i+1}/{len(rows)}', flush=True)
print('RUN COMPLETE')
