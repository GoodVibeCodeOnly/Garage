# -*- coding: utf-8 -*-
"""Did the nightly curator actually land? Prints the count of board rows with
author='curator' created in the last 12 hours. 0 means the pass did not land.
Called by curate.ps1's post-run verify (added 2026-08-11 after the invisible
Aug 3 OAuth death). Pure script, zero tokens."""
import os
import sqlite3

db = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db"))
print(db.execute(
    "SELECT COUNT(*) FROM board "
    "WHERE author='curator' AND created_at >= datetime('now','-12 hours')"
).fetchone()[0])
