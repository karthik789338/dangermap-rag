#!/usr/bin/env python3
"""DangerMap-RAG R1: all CPU-only main reviewer experiments, no regeneration."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

MODELS = ('qwen25_3b','qwen25_7b','mistral_7b','phi35_mini','granite33_8b','falcon3_7b')
CONDITIONS = ('clean','missing','partial','noisy','stale','contradictory')
DATASETS = ('hotpotqa','fever','pubmedqa','cuad','casehold','finqa','tatqa')
BENCH_SHA = 'e36d0ca8a239b4efa5848d30f4a7a217ebf0c3309d508453f44f8a27fd03a0e3'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(2**20), b''): h.update(chunk)
    return h.hexdigest()


def write_csv(path, records):
    if not records: return
    keys = list(dict.fromkeys(k for x in records for k in x))
    with Path(path).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(records)


def numeric_overlay(row, score_helpers):
    """Correct only previously identified ambiguous numeric-score NULLs.
    Conservatively choose a unique value from an explicit final-answer cue or
    last equation RHS; otherwise mark an unanswered scalar question incorrect.
    No gold-conditioned candidate selection; no inferred arithmetic.
    """
    if not (row.get('dataset') in ('finqa','tatqa')
            and row.get('correctness_method') == 'numeric_ambiguous'
            and row.get('automated_correctness') is None
            and row.get('answer_usable')):
        return row.get('automated_correctness'), False, ''
    h = score_helpers
    gold_mentions = h.numeric_mentions(row.get('gold_answer'))
    if not gold_mentions: raise ValueError('numeric_ambiguous but gold has no number')
    ans = str(row.get('answer_text') or '')
    candidates = []
    explicit = h._explicit_numeric_answer_segment(ans)
    if explicit:
        groups = h._equivalent_numeric_groups(h.numeric_mentions(explicit))
        if len(groups) == 1: candidates.append(('explicit_answer', groups[0][0]))
    if not candidates and '=' in ans:
        rhs = ans.rsplit('=', 1)[1]
        groups = h._equivalent_numeric_groups(h.numeric_mentions(rhs))
        if len(groups) == 1: candidates.append(('equation_rhs', groups[0][0]))
    if not candidates:
        groups = h._equivalent_numeric_groups(h.numeric_mentions(ans))
        if len(groups) == 1: candidates.append(('unique_numeric', groups[0][0]))
    if not candidates:
        return 0.0, True, 'ambiguous_numeric_no_scalar'
    how, candidate = candidates[0]
    ok = any(h.mentions_equivalent(candidate, gold) for gold in gold_mentions)
    return float(ok), True, how


def citation_v(row):
    if not row.get('citation_list_usable'): return math.nan
    ids = row.get('citations')
    if not isinstance(ids, list): return math.nan
    if not ids: return 0.0
    allowed = row.get('valid_citations') or []
    # The existing analysis-ready parser has already normalized exact doc_id prefixes.
    return len(allowed) / len(ids)


def decide_sf(a, c, v, abstained, ta=.5, tc=.7, tv=.5):
    # Three-valued logic: a known false component establishes SF=0 even
    # if another component is missing; otherwise missing remains unknown.
    if abstained is True: return 0.0
    if np.isfinite(a) and a >= ta: return 0.0
    if np.isfinite(c) and c < tc: return 0.0
    if np.isfinite(v) and v < tv: return 0.0
    if abstained is None or any(not np.isfinite(x) for x in (a,c,v)):
        return math.nan
    return 1.0


def summarize(vals, **extra):
    vals = np.asarray(vals, dtype=float)
    yes = int(np.nansum(vals)); observed = int(np.isfinite(vals).sum())
    total = int(vals.size); missing = total-observed
    return dict(extra, n=total, n_determinate=observed,
                n_indeterminate=missing, sf_count=yes,
                sf_rate_observed=(yes/observed if observed else None),
                sf_lower_bound=yes/total if total else None,
                sf_upper_bound=(yes+missing)/total if total else None)


def boot_ci(numerator, denominator, draws):
    n = np.sum(numerator[draws],axis=1)
    d = np.sum(denominator[draws],axis=1)
    values = np.divide(n,d,out=np.full(len(d),np.nan),where=(d>0))
    values = values[np.isfinite(values)]
    if not len(values): return (None,None)
    return tuple(float(x) for x in np.quantile(values, [0.025,0.975]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--bootstrap', type=int, default=1000)
    args = ap.parse_args(); root = Path(args.root)
    bench = root/'revision_v3/data/dangermap_instances_v3_1_12k.jsonl'
    if sha256(bench) != BENCH_SHA: raise RuntimeError('Frozen 12K benchmark checksum mismatch')
    src = root/'revision_v3/phase4/data'
    out = root/'revision_v3/reviewer_revision/phaseR1/results'
    out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str((root/'revision_v3/phase4/scripts').resolve()))
    import score_correctness_v3 as h
    for pred, gold, expected in [
        ('257 is not the answer; the answer is 300','257',0),
        ('9857 - 2920 = 6937','6937',1),
        ('increased from 9196 to 49891','40695',0)]:
        sample = dict(dataset='finqa',correctness_method='numeric_ambiguous',
                      automated_correctness=None,answer_usable=True,
                      answer_text=pred,gold_answer=gold)
        got, changed, _ = numeric_overlay(sample,h)
        if not changed or got != expected: raise AssertionError((pred,got,expected))
    benchmark = {}
    with bench.open(encoding='utf-8') as f:
        for line in f:
            b = json.loads(line)
            iid = b['instance_id']
            if iid in benchmark: raise RuntimeError('duplicate benchmark ID: '+iid)
            benchmark[iid]=(b['base_id'],b['dataset'],b['condition'])
    if len(benchmark)!=12000: raise RuntimeError('benchmark rows not 12000')
    bases = sorted(set(b for b,_,_ in benchmark.values()))
    if len(bases)!=2000: raise RuntimeError('benchmark base ID count not 2000')
    bi = {b:i for i,b in enumerate(bases)}
    mi={m:i for i,m in enumerate(MODELS)}
    ci={c:i for i,c in enumerate(CONDITIONS)}
    mat=np.full((6,2000,6),np.nan,dtype=float)
    # lightweight records; no source documents or prompts copied to results
    items=[]; correction=Counter(); methods=Counter(); model_files={}
    for m in MODELS:
        p=src/f'{m}_correctness_final_v3.jsonl'
        if not p.is_file(): raise FileNotFoundError(p)
        model_files[m]=sha256(p)
        seen=set(); counter=Counter()
        with p.open(encoding='utf-8') as f:
            for line in f:
                row=json.loads(line); iid=row['instance_id']
                if iid in seen or iid not in benchmark: raise RuntimeError('duplicate/unknown '+iid)
                seen.add(iid)
                b,d,condition=benchmark[iid]
                if (row['base_id'],row['dataset'],row['condition']) != (b,d,condition):
                    raise RuntimeError(f'metadata mismatch {iid}')
                a,changed,reason=numeric_overlay(row,h)
                if changed:
                    correction[m]+=1; methods[reason]+=1
                a=float(a) if a is not None else math.nan
                conf=row.get('expressed_confidence')
                conf=float(conf) if isinstance(conf,(float,int)) and not isinstance(conf,bool) else math.nan
                v=citation_v(row)
                abst=row.get('abstained')
                abst=abst if isinstance(abst,bool) else None
                sf=decide_sf(a,conf,v,abst)
                mat[mi[m],bi[b],ci[condition]]=sf
                items.append(dict(model=m,instance_id=iid,base_id=b,dataset=d,
                                  condition=condition,A=a,C=conf,V=v,B=abst,
                                  SF=sf,numeric_overlay=changed,
                                  citation_id_invalid=bool(row.get('invalid_citations')),
                                  clean_correct=(np.isfinite(a) and a>=.5)))
                counter[condition]+=1
        if seen!=set(benchmark): raise RuntimeError(f'{m}: missing benchmark IDs')
        if any(counter[c]!=2000 for c in CONDITIONS): raise RuntimeError(f'{m}: condition counts wrong')
        print(f'{m:16s} 12,000 verified; numeric adjusted={correction[m]:4d}',flush=True)
    if len(items)!=72000: raise RuntimeError('expected 72000 rows')
    if sum(correction.values()) != 4424:
        raise RuntimeError(f'Expected 4424 unresolved numeric rows; found {sum(correction.values())}. Stop and inspect scoring versions.')
    base_arr=np.array([x['base_id'] for x in items],dtype=str)
    dataset_arr=np.array([x['dataset'] for x in items],dtype=str)
    model_arr=np.array([x['model'] for x in items],dtype=str)
    cond_arr=np.array([x['condition'] for x in items],dtype=str)
    sf_arr=np.array([x['SF'] for x in items],dtype=float)
    a_arr=np.array([x['A'] for x in items],dtype=float)
    c_arr=np.array([x['C'] for x in items],dtype=float)
    v_arr=np.array([x['V'] for x in items],dtype=float)
    b_arr=np.array([x['B'] for x in items],dtype=object)
    # Primary model, evidence-condition and dataset-condition reports
    main_model=[]; main_condition=[]; main_dataset=[]
    for m in MODELS: main_model.append(summarize(sf_arr[model_arr==m],model=m))
    for m in MODELS:
        for c in CONDITIONS:
            mask=(model_arr==m)&(cond_arr==c)
            main_condition.append(summarize(sf_arr[mask],model=m,condition=c))
            for d in DATASETS:
                sub=mask&(dataset_arr==d)
                main_dataset.append(summarize(sf_arr[sub],model=m,condition=c,dataset=d))
    # Full 27-setting threshold sensitivity + ranking stability (no GPU)
    threshold=[]
    baseline=(sf_arr==1)&np.isfinite(sf_arr)
    groups = {'model': [(m,model_arr==m) for m in MODELS],
              'condition': [(c,cond_arr==c) for c in CONDITIONS],
              'dataset_condition': [(f'{d}|{c}',(dataset_arr==d)&(cond_arr==c))
                                    for d in DATASETS for c in CONDITIONS]}
    def dense_ranks(rows):
        # Higher observed SF = higher risk, missing rates rank after finite rates.
        valid=sorted(set(r['sf_rate_observed'] for r in rows if r['sf_rate_observed'] is not None),reverse=True)
        for r in rows:
            r['risk_rank']=valid.index(r['sf_rate_observed'])+1 if r['sf_rate_observed'] is not None else None
    for ta in (.4,.5,.6):
        for tc in (.6,.7,.8):
            for tv in (.4,.5,.6):
                results=np.array([decide_sf(x['A'],x['C'],x['V'],x['B'],ta,tc,tv)
                                  for x in items],dtype=float)
                positives=(results==1)&np.isfinite(results)
                union=int(np.sum(positives|baseline)); intersection=int(np.sum(positives&baseline))
                global_jaccard=intersection/union if union else None
                for group,labels in groups.items():
                    rows=[]
                    for name,mask in labels:
                        u=int(np.sum((positives|baseline)&mask))
                        inter=int(np.sum((positives&baseline)&mask))
                        r=summarize(results[mask],tau_A=ta,tau_C=tc,tau_V=tv,
                                    group=group,name=name,reference_jaccard=(inter/u if u else None),
                                    overall_reference_jaccard=global_jaccard)
                        rows.append(r)
                    dense_ranks(rows)
                    threshold.extend(rows)
    # Rankings at the reference setting, useful for direct rank comparison.
    reference_ranks={}
    for group, labels in groups.items():
        rows=[summarize(sf_arr[mask],group=group,name=name) for name,mask in labels]
        dense_ranks(rows)
        reference_ranks[group]={r['name']:r['risk_rank'] for r in rows}
    for row in threshold:
        row['reference_risk_rank']=reference_ranks[row['group']][row['name']]
        row['rank_change']=None if row['risk_rank'] is None else row['risk_rank']-row['reference_risk_rank']
    stability=[]
    for group,labels in groups.items():
        for name,_ in labels:
            sub=[r for r in threshold if r['group']==group and r['name']==name]
            changes=[abs(r['rank_change']) for r in sub if r['rank_change'] is not None]
            stability.append(dict(group=group,name=name,settings=len(sub),
                                  unchanged_rank=sum(x==0 for x in changes),
                                  mean_abs_rank_change=float(np.mean(changes)) if changes else None,
                                  max_abs_rank_change=int(max(changes)) if changes else None,
                                  reference_rank=reference_ranks[group][name]))
    # Base-ID bootstrap. Same sampled base IDs used for every model/condition.
    rng=np.random.default_rng(42)
    draws=rng.integers(0,2000,size=(args.bootstrap,2000),dtype=np.int32)
    ci_rows=[]; paired=[]
    for m in MODELS:
        smat=mat[mi[m],:,:]
        nums=np.nansum(smat,axis=1); dens=np.isfinite(smat).sum(axis=1)
        lo,hi=boot_ci(nums,dens,draws)
        ci_rows.append(dict(group='model',model=m,condition='ALL',estimate=float(nums.sum()/dens.sum()),ci_low=lo,ci_high=hi))
        for c in CONDITIONS:
            vals=smat[:,ci[c]]
            obs=np.isfinite(vals)
            lo,hi=boot_ci(np.nan_to_num(vals),obs.astype(int),draws)
            ci_rows.append(dict(group='model_condition',model=m,condition=c,
                                estimate=float(np.nanmean(vals)),ci_low=lo,ci_high=hi))
            if c=='clean': continue
            clean=smat[:,ci['clean']]
            paired_mask=np.isfinite(vals)&np.isfinite(clean)
            delta=np.where(paired_mask,vals-clean,0)
            lo,hi=boot_ci(delta,paired_mask.astype(int),draws)
            n_pairs=int(paired_mask.sum())
            paired.append(dict(comparison='condition_minus_clean',model=m,condition=c,
                               n_paired_bases=n_pairs,estimate=float(delta.sum()/n_pairs) if n_pairs else None,
                               ci_low=lo,ci_high=hi))
    for c in CONDITIONS:
        vals=mat[:,:,ci[c]]
        num=np.nansum(vals,axis=0); den=np.isfinite(vals).sum(axis=0)
        lo,hi=boot_ci(num,den,draws)
        ci_rows.append(dict(group='condition_all_models',model='ALL',condition=c,
                            estimate=float(num.sum()/den.sum()),ci_low=lo,ci_high=hi))
    ref=mat[mi['qwen25_7b']]
    for m in MODELS:
        if m=='qwen25_7b': continue
        v1=mat[mi[m]]
        mask=np.isfinite(v1)&np.isfinite(ref)
        delta=np.where(mask,v1-ref,0)
        nums=delta.sum(axis=1); dens=mask.sum(axis=1)
        lo,hi=boot_ci(nums,dens,draws)
        paired.append(dict(comparison='model_minus_qwen25_7b',model=m,condition='ALL',
                           n_paired_bases=int(np.any(mask,axis=1).sum()),
                           n_paired_outputs=int(mask.sum()),estimate=float(nums.sum()/dens.sum()),
                           ci_low=lo,ci_high=hi))
    # Clean-only failure decomposition, keeping abstention and missingness separate.
    clean_rows=[]
    for m in MODELS:
        for d in DATASETS:
            r=[x for x in items if x['model']==m and x['dataset']==d and x['condition']=='clean']
            clean_rows.append(dict(model=m,dataset=d,n=len(r),
                wrong_answer=sum(bool(np.isfinite(x['A']) and x['A']<.5) for x in r),
                correctness_missing=sum(not np.isfinite(x['A']) for x in r),
                abstained=sum(x['B'] is True for x in r),
                confident_nonabstain=sum(x['B'] is False and np.isfinite(x['C']) and x['C']>=.7 for x in r),
                zero_citation_v=sum(np.isfinite(x['V']) and x['V']==0 for x in r),
                invalid_citation_id=sum(x['citation_id_invalid'] for x in r),
                sf_certain=sum(x['SF']==1 for x in r),
                sf_indeterminate=sum(not np.isfinite(x['SF']) for x in r)))
    # Aggregate metadata and outputs
    for name,rows in [('sf_by_model.csv',main_model),('sf_by_model_condition.csv',main_condition),
                      ('sf_by_model_dataset_condition.csv',main_dataset),('threshold_27_settings.csv',threshold),
                      ('threshold_ranking_stability.csv',stability),('clustered_bootstrap_ci.csv',ci_rows),('paired_condition_model_comparisons.csv',paired),
                      ('clean_evidence_decomposition.csv',clean_rows)]: write_csv(out/name,rows)
    manifest=dict(benchmark_sha256=BENCH_SHA,models_file_sha256=model_files,
                  numeric_ambiguities_reclassified=sum(correction.values()),
                  numeric_adjustments_by_model=dict(correction),
                  numeric_adjustment_methods=dict(methods),
                  n_models=len(MODELS),n_outputs=len(items),n_bases=2000,n_conditions=len(CONDITIONS),
                  threshold_configurations=27,bootstrap_replicates=args.bootstrap,
                  seed=42,citation_V_definition='valid identifier citations / all supplied citations; empty list 0; unparseable list missing',
                  missing_policy='three-valued SF; report observed rate and full-denominator upper/lower bounds',
                  citation_F_status='not computed in R1; Danger Score and CUSF reserved for R2')
    (out/'r1_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    with (out/'primary_metrics_compact.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=('model','base_id','dataset','condition','instance_id','A','C','V','B','SF','numeric_overlay'))
        w.writeheader()
        for x in items: w.writerow({k:x[k] for k in w.fieldnames})
    with (out/'SHA256SUMS.txt').open('w',encoding='utf-8') as f:
        for p in sorted(out.glob('*')):
            if p.name!='SHA256SUMS.txt': f.write(f'{sha256(p)}  {p.name}\n')
    print('\nR1 COMPLETE — primary reviewer outputs, 27-setting sensitivity, 1,000 cluster bootstraps')
    for r in main_model:
        print(f"{r['model']:16s} SF={r['sf_rate_observed']:.4f} observed={r['n_determinate']:5d} unknown={r['n_indeterminate']:4d}")
    print(f'Outputs: {out}')

if __name__=='__main__': main()
