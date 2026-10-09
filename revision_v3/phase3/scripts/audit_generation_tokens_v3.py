import json
from pathlib import Path

from transformers import (
    AutoTokenizer,
    GenerationConfig,
)


MANIFEST = Path(
    "revision_v3/phase3/contracts/"
    "model_revisions_v3.json"
)

models = json.loads(
    MANIFEST.read_text(
        encoding="utf-8"
    )
)["models"]


print("=" * 92)
print(
    "DANGERMAP-RAG MODEL-NATIVE "
    "GENERATION TOKEN AUDIT"
)
print("=" * 92)


for m in models:

    print()
    print("=" * 92)
    print(m["short_name"])
    print(m["model_id"])
    print(m["revision"])
    print("=" * 92)

    tok = AutoTokenizer.from_pretrained(
        m["model_id"],
        revision=m["revision"],
        trust_remote_code=False,
    )

    try:
        gen = (
            GenerationConfig
            .from_pretrained(
                m["model_id"],
                revision=m["revision"],
            )
        )

        gen_eos = (
            gen.eos_token_id
        )

        gen_pad = (
            gen.pad_token_id
        )

    except Exception as exc:
        gen_eos = (
            "UNAVAILABLE:"
            + repr(exc)
        )

        gen_pad = None

    print(
        "tokenizer eos token:",
        repr(
            tok.eos_token
        ),
    )

    print(
        "tokenizer eos id   :",
        tok.eos_token_id,
    )

    print(
        "tokenizer pad id   :",
        tok.pad_token_id,
    )

    print(
        "generation eos id  :",
        gen_eos,
    )

    print(
        "generation pad id  :",
        gen_pad,
    )

    print(
        "special tokens     :",
        tok.special_tokens_map,
    )

    example = [
        {
            "role": "system",
            "content": "system",
        },
        {
            "role": "user",
            "content": "user",
        },
    ]

    rendered = (
        tok.apply_chat_template(
            example,
            tokenize=False,
            add_generation_prompt=True,
        )
    )

    print(
        "chat-template tail :",
        repr(
            rendered[-250:]
        ),
    )


print()
print("=" * 92)
print(
    "GENERATION TOKEN AUDIT: COMPLETE"
)
print("=" * 92)
