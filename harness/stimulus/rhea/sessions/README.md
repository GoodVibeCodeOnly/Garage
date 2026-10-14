# Invented sessions for the capture cells (designs 01, 04)

**Every line in these files is invented.** None of it comes from the house's transcript
archive, and nothing in it is a fact about Damon or anyone else. They're written in the
extractor's format (`# Session` header, `=== DAMON` / `=== RHEA` turns) because the capture
brief's triage step greps for that format.

The builder copies `s*.txt` into a sandbox's `transcripts/sessions/` under dated names and
fills the `{{...}}` tokens. This README isn't copied, so the label lives here and in the
build JSON, never inside a sandbox.

| file | what it is for |
|---|---|
| `s1_automation.txt` | a curator's own pass: a task header and tool talk. The brief says mark it, don't sweep |
| `s2_resumed.txt` | already in the ledger as swept to line `{{S2_SEEN}}`; only the tail is due, and the tail has the decision |
| `s3_gift.txt` | a name given, a running joke. The board already carries this beat, so dedupe has something to find |
| `s4_quiet.txt` | a long ordinary conversation with one flat, passing, unelaborated mention of his own life |
| `s5_fork.txt` | written by the builder: an exact prefix of `s4`, cut mid-reply (the resumption-chain shape) |
