# Paper Workspace

`main.tex` is a results-aware skeleton for the final short paper.

Tables should be generated from run artifacts:

```bash
python scripts/make_tables.py --metrics runs/<run-id>/metrics/router.json --output paper/tables/router_frontier.tex
```

Do not manually invent results. If an experiment did not complete, leave an explicit placeholder.
