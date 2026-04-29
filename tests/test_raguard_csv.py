from pathlib import Path
from dnh_router.data import load_raguard_csvs


def test_load_raguard_csvs_joins_claim_documents():
    root = Path("runs/test-fixtures/raguard-csv")
    root.mkdir(parents=True, exist_ok=True)
    claims = root / "claims.csv"
    docs = root / "documents.csv"
    claims.write_text(
        "Claim ID,Claim,Verdict,Original Verdict,Document IDs,Document Labels\n"
        '1,"A claim",True,True,"[10]","[supporting]"\n',
        encoding="utf-8",
    )
    docs.write_text(
        "Document ID,Claim ID,Title,Full Text,Document Label,Link\n"
        '10,1,"Title","Evidence text",supporting,https://example.com\n',
        encoding="utf-8",
    )
    records = load_raguard_csvs(str(claims), str(docs))
    assert len(records) == 1
    assert records[0]["gold"] == "true"
    assert records[0]["context"][0]["text"] == "Evidence text"
