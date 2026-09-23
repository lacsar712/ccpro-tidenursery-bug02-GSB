"""塘口状态机：所有合法跳转集中在此处判定。

状态语义：
- stocked（在养）：可与 quarantine（隔离）互转，也可进 dry（干塘）。
- quarantine（隔离）：可与 stocked（在养）互转，也可进 dry（干塘）。
- dry（干塘）：只能回到 stocked（在养）。

任何合法路径的增删都应只改这一张表，禁止在路由里另写判定。
"""

# 旧状态 -> 允许进入的新状态集合
ALLOWED_TRANSITIONS = {
    "stocked": {"stocked", "quarantine", "dry"},
    "quarantine": {"quarantine", "stocked", "dry"},
    "dry": {"dry", "stocked"},
}

# 中文状态名，用于 409 提示
STATUS_LABELS = {
    "stocked": "在养",
    "quarantine": "隔离",
    "dry": "干塘",
}


def can_transit(old: str, new: str) -> bool:
    """old -> new 是否为合法跳转；未知状态一律不允许。"""
    return new in ALLOWED_TRANSITIONS.get(old, set())


def transit_reason(old: str, new: str) -> str:
    """非法跳转的中文说明（仅在 can_transit 为 False 时调用）。"""
    old_label = STATUS_LABELS.get(old, old)
    new_label = STATUS_LABELS.get(new, new)
    return f"塘口状态不可由「{old_label}」直接改为「{new_label}」"
