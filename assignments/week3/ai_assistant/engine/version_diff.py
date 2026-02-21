import sqlite3
from packaging import version

DB_PATH = "data/upgrade.db"

def get_changes_between(tool, current_version, target_version):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tool, version, category, description FROM changes WHERE tool=?", (tool,))
    rows = c.fetchall()
    conn.close()

    filtered = []

    current_v = version.parse(current_version)
    target_v = version.parse(target_version)

    for row in rows:
        row_version = version.parse(row[1])
        if current_v < row_version <= target_v:
            filtered.append({
                "tool": row[0],
                "version": row[1],
                "category": row[2],
                "description": row[3]
            })

    return filtered
