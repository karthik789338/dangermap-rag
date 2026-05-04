import argparse
from datasets import load_dataset


DATASET_ATTEMPTS = {
    "hotpotqa": [
        ("hotpotqa/hotpot_qa", "distractor"),
        ("hotpot_qa", "distractor"),
    ],
    "fever": [
        ("fever/fever", "v1.0"),
        ("fever", "v1.0"),
        ("fever", None),
    ],
    "pubmedqa": [
        ("qiaojin/PubMedQA", "pqa_labeled"),
        ("bigbio/pubmed_qa", "pubmed_qa_labeled_source"),
    ],
    "cuad": [
        ("dvgodoy/CUAD_v1_Contract_Understanding_clause_classification", None),
        ("theatticusproject/cuad", None),
    ],
    "casehold": [
        ("coastalcph/lex_glue", "case_hold"),
    ],
    "finqa": [
        ("dreamerdeo/finqa", None),
        ("ibm-research/finqa", None),
    ],
    "tatqa": [
        ("next-tat/TAT-QA", None),
        ("tatqa", None),
    ],
}


def try_load_dataset(name, config, cache_dir):
    if config is None:
        return load_dataset(name, cache_dir=cache_dir)
    return load_dataset(name, config, cache_dir=cache_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache_dir", default="data/cache")
    args = parser.parse_args()

    print("=" * 80)
    print("Downloading/caching datasets")
    print("=" * 80)

    for logical_name, attempts in DATASET_ATTEMPTS.items():
        print("\n" + "=" * 80)
        print(f"Dataset group: {logical_name}")
        print("=" * 80)

        loaded = False

        for hf_name, config in attempts:
            print(f"Trying: {hf_name} | config={config}")
            try:
                ds = try_load_dataset(hf_name, config, args.cache_dir)
                print("SUCCESS")
                print(ds)
                loaded = True
                break
            except Exception as e:
                print("FAILED:", repr(e))

        if not loaded:
            print(f"WARNING: Could not load dataset group: {logical_name}")

    print("\nFinished dataset caching step.")


if __name__ == "__main__":
    main()
