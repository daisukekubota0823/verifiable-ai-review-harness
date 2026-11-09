import json, urllib.request, re
record = open('record.txt').read()
def ask(text, max_tokens=340):
    payload = {"messages": [{"role": "user", "content": text}], "temperature": 0, "max_tokens": max_tokens}
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r: d = json.load(r)
    return d['choices'][0]['message']['content'].strip()
promptA = f"""You are drafting a review of an experiment record for a researcher.

Record:
{record}

Write a structured review of at most 200 words with three parts: Key changes / Pathway picture / Points for human attention. Use only values from the record."""
draftA = ask(promptA)
open('draftA.txt', 'w').write(draftA)
skeleton = f"""Review of the experiment record (all values inserted from the record):
- 15,167 genes tested; 152 significantly up-regulated and 436 significantly down-regulated genes (padj < 0.05 and |log2FoldChange| >= 1).
- Strongest increases: ENSG00000089199 (+4.37) and ENSG00000120738 (+4.04). Strongest decreases: ENSG00000124491 (-5.60) and ENSG00000019991 (-4.29).
- 138 pathways are significant at FDR < 0.05; the strongest are translation-related Reactome sets with NES around +3.5."""
promptB = f"""{skeleton}

Write a 2-3 sentence interpretation of what this pattern means for the experiment, for the researcher reviewing it. Do not introduce any new numbers, gene IDs, or pathway names that are not in the text above."""
draftB = ask(promptB, max_tokens=160)
open('draftB.txt', 'w').write(skeleton + "\n\nInterpretation (model): " + draftB)
print("=== A ==="); print(draftA); print("=== B interpretation ==="); print(draftB)
