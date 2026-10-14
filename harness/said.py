"""Re-extract what a worker SAID, separating its own words from file contents.

The first version of this extraction read only `text` blocks. It missed the
`thinking` blocks entirely -- eleven of them in one run -- and a keyword grep over
the raw stream then counted hits inside tool_results, i.e. inside the brief's own
text, as if the worker had written them. Both errors point the same way: a count
over a transcript must say which speaker it counted.

  python said.py <run_name>        -> runs/<name>/SAID.md rewritten, labelled
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent


def extract(name):
    p = HERE / "runs" / name / "stream.jsonl"
    if not p.exists():   # a cell stopped at the room check has no stream; skip it, don't crash
        print("%s: no stream.jsonl (room check stopped the run?)" % name)
        return ""
    parts, own = [], []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        msg = ev.get("message") or {}
        role = msg.get("role")
        for b in (msg.get("content") or []):
            if not isinstance(b, dict):
                continue
            t = b.get("type")
            if t == "thinking" and role == "assistant":
                parts.append(("THINKING", b.get("thinking") or ""))
                own.append(b.get("thinking") or "")
            elif t == "text" and role == "assistant":
                parts.append(("SAID", b["text"]))
                own.append(b["text"])
            elif t == "tool_use":
                parts.append(("TOOL " + str(b.get("name")),
                              json.dumps(b.get("input"), ensure_ascii=False)[:1500]))
    out = []
    for kind, body in parts:
        out.append("### %s\n\n%s" % (kind, body.strip()))
    (HERE / "runs" / name / "SAID.md").write_text("\n\n".join(out), encoding="utf-8")
    (HERE / "runs" / name / "OWN_WORDS.txt").write_text("\n\n".join(own), encoding="utf-8")
    return "\n".join(own)


if __name__ == "__main__":
    names = sys.argv[1:] or [p.parent.name for p in (HERE / "runs").glob("*/stream.jsonl")]
    KW = ["truncat", "cut off", "cut-off", "incomplete", "recall of did", "mid-sentence",
          "corrupt", "4 KB", "4KB", "4096", "end of central directory", "fragment",
          "rotat", "delet", "evict", "oldest", "escalat", "Inbox", "argv", "quotation",
          "double quote", "stdin"]
    for n in sorted(names):
        own = extract(n)
        low = own.lower()
        print("=" * 72)
        print(n, " (worker-authored chars: %d)" % len(own))
        for kw in KW:
            c = low.count(kw.lower())
            if c:
                print("   %-26s %d" % (kw, c))
