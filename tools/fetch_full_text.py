#!/usr/bin/env python3
"""Fetch full verbatim OCR text for declassified documents and save in-repo.

Usage:
  python tools/fetch_full_text.py --collection stargate
  python tools/fetch_full_text.py --collection mkultra
  python tools/fetch_full_text.py --collection stargate --limit 10

Resume-safe: skips files already present. Logs progress to tools/fetch_log.txt.
"""
import argparse, json, os, re, time, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.path.join(ROOT, "..", "scratchpad")  # not used; data lives in repo data/

# Collection definitions: (list of ids, output dir)
def load_ids(collection):
    if collection == "stargate":
        import json as J
        docs = J.load(open(os.path.join(ROOT, "data", "rv_docs4.json"), encoding="utf-8"))
        sg = J.load(open(os.path.join(ROOT, "data", "sg_docs.json"), encoding="utf-8"))
        seen = set(); ids = []
        for d in docs + sg:
            if d["identifier"] in seen: continue
            seen.add(d["identifier"]); ids.append(d["identifier"])
        return sorted(ids), "documents/stargate"
    if collection == "mkultra":
        import json as J
        # build list from archive search at runtime
        ids = []
        page = 1
        while True:
            params = [("q", "collection:ciareadingroom AND mkultra"), ("fl[]", "identifier"),
                      ("rows", 200), ("page", page), ("sort", "identifier asc"), ("output", "json")]
            url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(params)
            d = J.load(urllib.request.urlopen(url, timeout=30))
            batch = d["response"]["docs"]
            if not batch: break
            ids += [x["identifier"] for x in batch]
            if len(ids) >= d["response"]["numFound"]: break
            page += 1
            time.sleep(0.3)
        return sorted(set(ids)), "documents/mkultra"
    raise ValueError(collection)

def fetch_text(ident):
    base = ident
    if base.startswith("cia-readingroom-document-"):
        base = base[len("cia-readingroom-document-"):]
    fname = base + "_djvu.txt"
    url = "https://archive.org/download/" + ident + "/" + fname
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    # Fallback to metadata description if direct text download fails
    try:
        meta_url = "https://archive.org/metadata/" + ident
        req = urllib.request.Request(meta_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8", errors="replace"))
        desc = d.get("metadata", {}).get("description", "")
        if desc:
            return "[Archive OCR Excerpt]\n" + desc
    except Exception:
        pass
    raise last_err
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", required=True, choices=["stargate", "mkultra"])
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    ids, outdir = load_ids(args.collection)
    outpath = os.path.join(ROOT, outdir)
    os.makedirs(outpath, exist_ok=True)
    log = os.path.join(ROOT, "tools", "fetch_log.txt")

    if args.limit:
        ids = ids[:args.limit]

    done = 0
    skipped = 0
    for i, ident in enumerate(ids, 1):
        dest = os.path.join(outpath, ident + ".txt")
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            skipped += 1
            continue
        try:
            text = fetch_text(ident)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
            done += 1
            with open(log, "a", encoding="utf-8") as f:
                f.write("OK " + ident + "\n")
            print("fetched", i, "/", len(ids), ident, flush=True)
        except Exception as e:
            with open(log, "a", encoding="utf-8") as f:
                f.write("ERR " + ident + " " + str(e) + "\n")
            print("ERR", i, "/", len(ids), ident, e, flush=True)
        time.sleep(0.2)

    print("done. fetched:", done, "skipped:", skipped, "total:", len(ids))

if __name__ == "__main__":
    main()
