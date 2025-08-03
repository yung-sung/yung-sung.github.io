#!/usr/bin/env python3
import argparse, json, pathlib, re, subprocess, sys, tempfile, time

TD_RE = re.compile(r'<td\s+class="gsc_rsb_std">\s*([\d,]+)\s*</td>', re.I)

def fetch_with_wget(user_id: str) -> str:
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmp_path = tmp.name
    tmp.close()

    cmd = [
        "wget", "-q", "-O", tmp_path,
        "--timeout=30", "--tries=3",
        "--header", "User-Agent: Mozilla/5.0",
        "--header", "Accept-Language: en-US,en;q=0.9",
        url,
    ]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise RuntimeError("wget failed")
    return tmp_path

def parse_total_citations(html_text: str) -> int:
    m = TD_RE.search(html_text)
    if not m:
        raise RuntimeError("Could not find <td class='gsc_rsb_std'>…</td> in HTML.")
    return int(m.group(1).replace(",", ""))

def main():
    ap = argparse.ArgumentParser(description="Get Google Scholar total citations.")
    ap.add_argument("--file", help="Path to locally saved Scholar HTML (e.g., page.html)")
    ap.add_argument("--user", help="Google Scholar user id (e.g., 3ar1DOwAAAAJ) to fetch via wget")
    ap.add_argument("--out-json", default="scholar.json", help="Output JSON path")
    ap.add_argument("--out-txt", default="scholar_citations.txt", help="Output TXT path")
    args = ap.parse_args()

    if not args.file and not args.user:
        ap.error("Provide --file OR --user")

    # Get HTML
    html_path = args.file or fetch_with_wget(args.user)
    html = pathlib.Path(html_path).read_text(encoding="utf-8", errors="ignore")

    # Parse
    total = parse_total_citations(html)

    # Write outputs
    pathlib.Path(args.out_txt).write_text(f"{total}\n", encoding="utf-8")
    rec = {
        "citations": total,
        "updated_by": "local-scrape",
        "source": ("local file" if args.file else f"https://scholar.google.com/citations?user={args.user}&hl=en"),
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    pathlib.Path(args.out_json).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")

    print(f"Citations: {total}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)