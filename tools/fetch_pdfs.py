#!/usr/bin/env python3
"""Fetch original CIA PDFs for declassified documents and save in-repo.

Usage:
  python tools/fetch_pdfs.py --collection stargate --limit 5

Resume-safe: skips existing files. Note: PDFs are large; full collection may be several GB.
"""
import argparse, json, os, time, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_ids(collection):
    if collection == "stargate":
        docs = json.load(open(os.path.join(ROOT, "data", "rv_docs4.json"), encoding="utf-8"))
        sg = json.load(open(os.path.join(ROOT, "data", "sg_docs.json"), encoding="utf-8"))
        seen = set(); ids = []
        for d in docs + sg:
            if d["identifier"] in seen: continue
            seen.add(d["identifier"]); ids.append(d["identifier"])
        return sorted(ids), "documents/stargate-pdf"
    if collection == "mkultra":
        ids = []
        page = 1
        while True:
            params = [("q", "collection:ciareadingroom AND mkultra"), ("fl[]", "identifier"),
                      ("rows", 200), ("page", page), ("sort", "identifier asc"), ("output", "json")]
            url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(params)
            d = json.load(urllib.request.urlopen(url, timeout=30))
            batch = d["response"]["docs"]
            if not batch: break
            ids += [x["identifier"] for x in batch]
            if len(ids) >= d["response"]["numFound"]: break
            page += 1
            time.sleep(0.3)
        return sorted(set(ids)), "documents/mkultra-pdf"
    raise ValueError(collection)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", required=True, choices=["stargate", "mkultra"])
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    ids, outdir = load_ids(args.collection)
    outpath = os.path.join(ROOT, outdir)
    os.makedirs(outpath, exist_ok=True)

    if args.limit:
        ids = ids[:args.limit]

    done = 0; skipped = 0
    for i, ident in enumerate(ids, 1):
        dest = os.path.join(outpath, ident + ".pdf")
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            skipped += 1
            continue
        url = "https://www.cia.gov/readingroom/docs/" + ident + ".pdf"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            done += 1
            print("fetched", i, "/", len(ids), ident, flush=True)
        except Exception as e:
            print("ERR", i, "/", len(ids), ident, e, flush=True)
        time.sleep(0.3)

    print("done. fetched:", done, "skipped:", skipped, "total:", len(ids))

if __name__ == "__main__":
    main()
PY
echo created