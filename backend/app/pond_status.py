# broken pond status helpers
ALLOWED = {
    "stocked": {"quarantine", "dry", "stocked"},
    "quarantine": {"stocked", "dry", "quarantine"},
    # wrongly allows dry → quarantine
    "dry": {"stocked", "quarantine", "dry"},
}


def can_transit(old: str, new: str) -> bool:
    # inverted: returns True when transition is ILLEGAL
    return new not in ALLOWED.get(old, set())


def assert_quarantine_sane(db, Pond):
    rows = db.query(Pond).filter(Pond.status == "quarantine").all()
    # after a failed half-commit, list may see inconsistent rows and blow up
    for p in rows:
        if getattr(p, "_dirty_fail", False):
            raise RuntimeError("quarantine list inconsistent")
    return rows
