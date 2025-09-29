import pandas as pd
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def normalize_url(u: str) -> str:
    u = (u or "").strip()
    p = urlparse(u)
    qs = urlencode(sorted(parse_qsl(p.query, keep_blank_values=True)))
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path or "/", "", qs, ""))

def load_urls_from_csv(path: str) -> list[str]:
    df = pd.read_csv(path)
    col = None
    for c in df.columns:
        if c.lower() in ("url", "address"):
            col = c; break
    if col is None:
        raise ValueError("CSV 需包含 'url' 或 'address' 列。")
    return [normalize_url(x) for x in df[col].dropna().tolist()]

def export_results_csv(df, path: str):
    df.to_csv(path, index=False, encoding="utf-8-sig")
