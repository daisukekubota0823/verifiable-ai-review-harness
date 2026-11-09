import json, urllib.request, csv, re
PROMPT = """You verify draft review statements against an analysis record.

Rules:
- Significant means padj (FDR) < 0.05.
- Direction: a positive NES or log2FoldChange means up, negative means down.
- A gene counts as significantly changed only if padj < 0.05 AND the absolute log2FoldChange is at least 1.
- A statement is CONTRADICTED if any number, direction, or significance claim in it does not match the evidence.

Evidence:
{ev}

Statement: {stmt}

Answer with exactly one word: SUPPORTED or CONTRADICTED."""
def ask(row):
    text = PROMPT.format(ev=row['evidence'], stmt=row['statement'])
    payload = {"messages": [{"role": "user", "content": text}], "temperature": 0, "max_tokens": 8}
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as r: d = json.load(r)
    out = d['choices'][0]['message']['content'].strip().upper()
    m = re.search(r'\b(SUPPORTED|CONTRADICTED)\b', out)
    return m.group(1) if m else 'PARSE_FAIL:' + out[:30]
rows = list(csv.DictReader(open('claims.csv')))
with open('results2_raw.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['idx','kind','truth','band','pred'])
    for i, row in enumerate(rows):
        pred = ask(row)
        w.writerow([i, row['kind'], row['truth'], row['band'], pred]); f.flush()
        if (i+1) % 20 == 0: print(f'{i+1}/{len(rows)}', flush=True)
print('RUN2 COMPLETE')
