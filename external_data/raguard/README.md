# RAGuard Local CSV Mirror

Codex Cloud may receive `httpx.ProxyError: 403 Forbidden` when downloading from Hugging Face.
If that happens, manually download these public RAGuard files from Hugging Face and place them here:

- `claims.csv`
- `documents.csv`

Source page:

<https://huggingface.co/datasets/UCSC-IRKM/RAGuard/tree/main>

After both files are present, this command automatically reads the local CSV mirror:

```bash
python scripts/download_data.py --config configs/raguard.yaml --output data/raguard.jsonl
```

Do not rename the files.
