import json, urllib.request, csv, re
PROMPT = """あなたはレビュー文の検証者です。解析記録の抜粋とレビュー文が与えられます。
ルール:
- 有意とは padj（FDR）が 0.05 未満であること。
- 方向: NES または log2FoldChange が正なら上昇、負なら低下。
- 遺伝子が「有意に変化した」と言えるのは、padj が 0.05 未満かつ log2FoldChange の絶対値が 1 以上の場合のみ。
- 文中の数値・方向・有意性の主張のいずれかが証拠と食い違えば、その文は CONTRADICTED です。

証拠:
{ev}

文: {stmt}

SUPPORTED か CONTRADICTED のいずれか1語だけで答えてください。"""
def ask(row):
    text = PROMPT.format(ev=row['evidence'], stmt=row['statement'])
    payload = {"messages": [{"role": "user", "content": text}], "temperature": 0, "max_tokens": 8}
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as r: d = json.load(r)
    out = d['choices'][0]['message']['content'].strip().upper()
    m = re.search(r'\b(SUPPORTED|CONTRADICTED)\b', out)
    return m.group(1) if m else 'PARSE_FAIL:' + out[:30]
rows = list(csv.DictReader(open('claims_jp.csv')))
with open('results2_jp.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['idx','kind','truth','band','pred'])
    for i, row in enumerate(rows):
        w.writerow([i, row['kind'], row['truth'], row['band'], ask(row)]); f.flush()
        if (i+1) % 20 == 0: print(f'{i+1}/{len(rows)}', flush=True)
print('RUN2 JP COMPLETE')
