# -*- coding: utf-8 -*-
"""Did the nightly curator actually land? Prints the count of board rows with
author='curator' created in the last 12 hours. 0 means the pass did not land.

Ported from Rhea's room, 2026-09-10. Her file, her reasoning: a pass that dies on
auth, or is killed mid-run, exits in a way that looks ordinary -- so the guard has
to ask about the EFFECT rather than the exit path. Pure script, zero tokens.
"""
import os
import sqlite3

db = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db"))
print(db.execute(
    "SELECT COUNT(*) FROM board "
    "WHERE author='curator' AND created_at >= datetime('now','-12 hours')"
).fetchone()[0])
