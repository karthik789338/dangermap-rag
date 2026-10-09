#!/usr/bin/env python3
"""DangerMap-RAG R2: frozen stratified citation-entailment diagnostic.

Reuses existing 72K responses; no model generation or source modification.
The NLI value is an *imperfect proxy*, not established citation faithfulness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import time
from collections import Counter, defaultdict
from pathlib import Path

MODELS = ('qwen25_3b', 'qwen25_7b', 'mistral_7b', 'phi35_mini', 'granite33_8b', 'falcon3_7b')
DATASETS = ('hotpotqa', 'fever', 'pubmedqa', 'cuad', 'casehold', 'finqa', 'tatqa')
CONDITIONS = ('clean', 'missing', 'partial', 'noisy', 'stale', 'contradictory')
MODEL_ID = 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli'
REVISION = '6f5cf0a2b59cabb106aca4c287eed12e357e90eb'
BENCH_SHA = 'e36d0ca8a239b4efa5848d30f4a7a217ebf0c3309d508453f44f8a27fd03a0e3'
WEIGHTS = {
    'equal': (0.25, 0.25, 0.25, 0.25),
    'incorrectness_heavy': (0.4, 0.2, 0.2, 0.2),
    'confidence_heavy': (0.2, 0.4, 0.2, 0.2),
    'citation_heavy': (0.2, 0.2, 0.3, 0.3),
}


def hash_file(p: Path):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(p):
    with Path(p).open(encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_csv(p: Path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def eligible(row):
    return (row.get('abstained') is False
            and row.get('answer_usable') is True
            and bool(row.get('answer_text'))
            and isinstance(row.get('valid_citations'), list)
            and len(row['valid_citations']) > 0)


def sample_panel(root, n, seed):
    """Blind (to correctness/SF) sample from cited non-abstaining outputs.

    Two per model x dataset x condition cell where available, then fill
    remaining places uniformly from all remaining eligible rows.
    """
    groups = defaultdict(list)
    eligible_count = Counter()
    for m in MODELS:
        p = root / 'revision_v3/phase4/data' / f'{m}_correctness_final_v3.jsonl'
        if not p.is_file():
            raise FileNotFoundError(p)
        seen = set()
        for r in read_jsonl(p):
            iid = r['instance_id']
            if iid in seen:
                raise ValueError(f'{m}: repeated instance {iid}')
            seen.add(iid)
            if not eligible(r):
                continue
            key = (m, r['dataset'], r['condition'])
            groups[key].append(iid)
            eligible_count[key] += 1
        if len(seen) != 12000:
            raise RuntimeError(f'{m}: expected 12,000 unique outputs, found {len(seen)}')
    rng = random.Random(seed)
    chosen = []
    unused = []
    cells_short = []
    for m in MODELS:
        for d in DATASETS:
            for c in CONDITIONS:
                k = (m,d,c)
                ids = sorted(groups[k])
                rng.shuffle(ids)
                take = min(2, len(ids))
                chosen.extend((m,iid) for iid in ids[:take])
                unused.extend((m,iid) for iid in ids[take:])
                if take < 2:
                    cells_short.append({'model':m,'dataset':d,'condition':c,'eligible':len(ids)})
    if len(chosen) > n:
        raise ValueError(f'requested sample={n} smaller than required cell minimum={len(chosen)}')
    rng.shuffle(unused)
    chosen.extend(unused[:n - len(chosen)])
    if len(chosen) != n or len(set(chosen)) != n:
        raise RuntimeError('Insufficient eligible outputs or duplicate sampling')
    return set(chosen), eligible_count, cells_short


def build_hypothesis(question, answer, tokenizer, limit=168):
    # Not a canonical factual proposition: results remain NLI proxies only.
    raw = f'Question: {question}\nAnswer: {answer}'
    ids = tokenizer.encode(raw, add_special_tokens=False)
    clipped = len(ids) > limit
    return tokenizer.decode(ids[:limit], skip_special_tokens=True), clipped


def evidence_windows(text, tokenizer, window_tokens, max_windows):
    ids = tokenizer.encode(text or '', add_special_tokens=False)
    if not ids:
        return [''], False
    step = max(1, window_tokens - 80)
    starts = list(range(0, len(ids), step))
    starts = starts[:max_windows]
    windows = [tokenizer.decode(ids[x:x+window_tokens], skip_special_tokens=True) for x in starts]
    truncated = (starts[-1] + window_tokens < len(ids)) if starts else True
    return windows, truncated


def numeric(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def check_r1(root):
    b = root / 'revision_v3/data/dangermap_instances_v3_1_12k.jsonl'
    if hash_file(b) != BENCH_SHA:
        raise RuntimeError('Frozen benchmark checksum mismatch')
    r1 = root / 'revision_v3/reviewer_revision/phaseR1/results/r1_manifest.json'
    if not r1.exists():
        raise FileNotFoundError('Run R1 first: '+str(r1))
    manifest = json.loads(r1.read_text(encoding='utf-8'))
    if manifest.get('n_outputs') != 72000:
        raise ValueError('R1 output count mismatch')
    if manifest.get('numeric_ambiguities_reclassified') != 4424:
        raise ValueError('Unexpected R1 numeric adjustment count')
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--sample', type=int, default=600)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--batch-size', type=int, default=16)
    ap.add_argument('--max-docs', type=int, default=4, help='max cited docs scored per output; omissions logged')
    ap.add_argument('--max-windows', type=int, default=2, help='windows per cited document; omitted text logged')
    ap.add_argument('--window-tokens', type=int, default=320)
    ap.add_argument('--device', choices=['auto','cuda','cpu'], default='auto')
    a = ap.parse_args()
    root = Path(a.root)
    r1_manifest = check_r1(root)
    out = root / 'revision_v3/reviewer_revision/phaseR2/results'
    out.mkdir(parents=True, exist_ok=True)
    sample_path = out / 'r2_fixed_panel.json'
    if sample_path.exists():
        panel = json.loads(sample_path.read_text(encoding='utf-8'))
        if panel['seed'] != a.seed or panel['n_requested'] != a.sample:
            raise RuntimeError('Existing frozen sample has different seed/size. Do not overwrite.')
        selected = {tuple(x) for x in panel['selected']}
    else:
        selected, eligible_counts, short_cells = sample_panel(root, a.sample, a.seed)
        panel = {
            'n_requested': a.sample, 'seed': a.seed,
            'sampling': 'two per model/dataset/condition where eligible, remaining uniform without replacement',
            'eligibility': 'answer usable, non-abstaining, >=1 valid cited document ID',
            'selected': [list(x) for x in sorted(selected)],
            'cells_below_two': short_cells,
            'eligible_by_cell': {'|'.join(k):v for k,v in sorted(eligible_counts.items())},
        }
        sample_path.write_text(json.dumps(panel, indent=2), encoding='utf-8')
    print(f'R2 FIXED PANEL: {len(selected)} entries; cell shortfalls={len(panel["cells_below_two"])}', flush=True)
    sample_rows = {}
    for m in MODELS:
        p = root / 'revision_v3/phase4/data' / f'{m}_correctness_final_v3.jsonl'
        for row in read_jsonl(p):
            key = (m,row['instance_id'])
            if key in selected:
                sample_rows[key] = row
    if set(sample_rows) != selected:
        raise RuntimeError('Panel IDs were not all found')
    print(f'Collected {len(sample_rows)} evidence-containing rows', flush=True)

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    device = 'cuda' if (a.device == 'auto' and torch.cuda.is_available()) else ('cpu' if a.device == 'auto' else a.device)
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA requested but unavailable')
    print(f'Loading pinned NLI model {MODEL_ID} @ {REVISION}; device={device}', flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION, local_files_only=True)
    mdl = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ID, revision=REVISION, local_files_only=True,
        torch_dtype=torch.float16 if device=='cuda' else torch.float32).to(device)
    mdl.eval()
    labels = {int(k):str(v).lower() for k,v in mdl.config.id2label.items()}
    entail = [k for k,v in labels.items() if 'entail' in v]
    if len(entail)!=1:
        raise RuntimeError('Unknown NLI labels: '+str(labels))
    entail_id = entail[0]
    pairs, meta = [], {}
    for key in sorted(selected):
        row = sample_rows[key]
        hyp, hyp_clipped = build_hypothesis(row['question'],row['answer_text'],tok)
        cited = row.get('valid_citations',[])
        seen = set()
        ordered = []
        for c in cited:
            if c not in seen:
                ordered.append(c); seen.add(c)
        docs = {str(d['doc_id']):d for d in row['evidence_docs']}
        included = [x for x in ordered if x in docs][:a.max_docs]
        record = {
            'model':key[0],'instance_id':key[1], 'dataset':row['dataset'], 'condition':row['condition'],
            'base_id':row['base_id'], 'n_valid_citations':len(ordered),
            'n_scored_citations':len(included), 'n_citations_omitted':max(0,len(ordered)-len(included)),
            'answer_hypothesis_clipped':hyp_clipped, 'documents_with_omitted_windows':0,
            'doc_scores':defaultdict(list),
        }
        meta[key] = record
        for doc_id in included:
            doc = docs[doc_id]
            windows, clipped = evidence_windows(f"{doc.get('title','')}\n{doc.get('text','')}",tok,a.window_tokens,a.max_windows)
            if clipped:
                record['documents_with_omitted_windows'] += 1
            for window in windows:
                pairs.append((key,doc_id,window,hyp))
    print(f'NLI pairs to score: {len(pairs)}',flush=True)
    t0=time.time()
    for start in range(0,len(pairs),a.batch_size):
        batch=pairs[start:start+a.batch_size]
        premises=[x[2] for x in batch]
        hypotheses=[x[3] for x in batch]
        encoded=tok(premises,hypotheses,return_tensors='pt',padding=True,
                    truncation='only_first',max_length=512)
        encoded={k:v.to(device) for k,v in encoded.items()}
        with torch.inference_mode():
            logits=mdl(**encoded).logits
            probs=torch.softmax(logits.float(),dim=-1)
            p_ent=probs[:,entail_id].cpu().tolist()
            pred=probs.argmax(dim=1).cpu().tolist()
        for (key,doc_id,_,_),p,lab in zip(batch,p_ent,pred):
            meta[key]['doc_scores'][doc_id].append((float(p),int(lab)))
        if start==0 or (start//a.batch_size)%50==0:
            print(f'NLI {min(start+a.batch_size,len(pairs))}/{len(pairs)}',flush=True)
    del mdl
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print(f'NLI inference finished in {(time.time()-t0)/60:.1f} minutes',flush=True)
    # Import R1 columns rather than silently recomputing its frozen numeric overlay.
    r1_vals={}
    r1_csv=root/'revision_v3/reviewer_revision/phaseR1/results/primary_metrics_compact.csv'
    with r1_csv.open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            k=(r['model'],r['instance_id'])
            if k in selected:
                r1_vals[k]=r
    if set(r1_vals)!=selected:
        raise RuntimeError('R1 metric join mismatch')
    rows=[]
    for key in sorted(selected):
        record=meta[key]
        per_doc=[]
        for doc_id, values in record['doc_scores'].items():
            best=max(values,key=lambda v:v[0])
            per_doc.append({'doc_id':doc_id, 'best_entailment_probability':best[0],
                            'best_window_entailment_argmax':int(best[1]==entail_id),
                            'windows_scored':len(values)})
        means=[d['best_entailment_probability'] for d in per_doc]
        frac=[d['best_window_entailment_argmax'] for d in per_doc]
        v=r1_vals[key]
        outrow={k:record[k] for k in (
            'model','instance_id','dataset','condition','base_id','n_valid_citations',
            'n_scored_citations','n_citations_omitted','answer_hypothesis_clipped',
            'documents_with_omitted_windows')}
        outrow.update({
            'nli_proxy_mean_entailment':sum(means)/len(means) if means else None,
            'nli_proxy_max_entailment':max(means) if means else None,
            'nli_proxy_fraction_entailment_argmax':sum(frac)/len(frac) if frac else None,
            'per_document_nli':per_doc,
            'A':numeric(v['A']),'C':numeric(v['C']),'V':numeric(v['V']),
            'B':v['B'],'SF':numeric(v['SF']),
        })
        # Descriptive *sample-only* weight sensitivity; not independently validated risk.
        F=outrow['nli_proxy_mean_entailment']
        if F is not None and all(outrow[z] is not None for z in ('A','C','V')) and v['B']=='False':
            for name,(wi,wc,wv,wu) in WEIGHTS.items():
                outrow[f'D_{name}']=(wi*(1-outrow['A'])+wc*outrow['C']+wv*outrow['V']+wu*outrow['V']*(1-F))
        rows.append(outrow)
    output=out/'r2_sampled_nli_results.jsonl'
    with output.open('w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
    summary=[]
    for m in MODELS:
        sel=[x for x in rows if x['model']==m]
        F=[x['nli_proxy_mean_entailment'] for x in sel if x['nli_proxy_mean_entailment'] is not None]
        summary.append({
            'model':m,'n_selected':len(sel),'n_scored':len(F),
            'mean_nli_entailment_proxy':(sum(F)/len(F) if F else None),
            'outputs_with_incomplete_cited_doc_coverage':sum(x['n_citations_omitted']>0 or x['documents_with_omitted_windows']>0 for x in sel),
            'hypotheses_clipped':sum(x['answer_hypothesis_clipped'] for x in sel),
            **{f'mean_D_{name}': (sum(x[f'D_{name}'] for x in sel if f'D_{name}' in x)/sum(f'D_{name}' in x for x in sel)
                                      if any(f'D_{name}' in x for x in sel) else None) for name in WEIGHTS}
        })
    write_csv(out/'r2_sampled_nli_by_model.csv',summary)
    manifest={
        'version':'R2-sampled-NLI-diagnostic-v1', 'n_sample':a.sample,'seed':a.seed,
        'benchmark_sha256':BENCH_SHA,'r1_numeric_adjustments':r1_manifest['numeric_ambiguities_reclassified'],
        'model_id':MODEL_ID,'model_revision':REVISION,'labels':labels,'device':device,
        'nli_pair_count':len(pairs),'max_cited_docs':a.max_docs,'max_windows_per_citation':a.max_windows,
        'window_token_budget':a.window_tokens,'hypothesis_token_budget':168,
        'pair_token_budget':512,
        'faithfulness_interpretation':'Question-conditioned entailment proxy, not calibrated support probability or human validation.',
        'missing_evidence_coverage':'Omitted cited docs and passage windows are counted explicitly.',
        'danger_interpretation':'Exploratory sample-only weight sensitivity, not independent Danger Score validation.',
        'weight_profiles':WEIGHTS,
        'panel_sha256':hash_file(sample_path), 'r2_results_sha256':hash_file(output)
    }
    (out/'r2_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('R2 COMPLETE — sampled NLI proxy, bounded evidence coverage, weight sensitivity',flush=True)
    for s in summary:
        f=s['mean_nli_entailment_proxy']
        print(f"{s['model']:16s} selected={s['n_selected']:3d} scored={s['n_scored']:3d} "
              f"mean_NLI_proxy={f:.4f}" if f is not None else str(s),flush=True)
    print(f'Outputs: {out}',flush=True)

if __name__=='__main__':
    main()
