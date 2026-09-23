"""塘口状态机：所有合法状态流转的唯一判定入口。

状态：
- stocked（在养）
- quarantine（隔离）
- dry（干塘）

合法流转：
- stocked ↔ quarantine（在养与隔离可互转）
- stocked / quarantine → dry（非干塘可进干塘）
- dry → stocked（干塘只能回到在养，不能直接转隔离）
"""

STOCKED = "stocked"
QUARANTINE = "quarantine"
DRY = "dry"

# 现状态 -> 允许变更到的目标状态集合
ALLOWED_TRANSITIONS = {
    STOCKED: {QUARANTINE, DRY},
    QUARANTINE: {STOCKED, DRY},
    DRY: {STOCKED},
}


def can_transit(old: str, new: str) -> bool:
    """是否允许把塘口状态从 old 改为 new。

    严格判定：状态未发生变化不算一次合法流转。并发场景下行锁把请求
    串行化后，后到的请求会读到前一个事务已提交的新状态，此时必须判
    冲突，才能保证同一次并发推进至多一个请求成功。
    """
    if old == new:
        return False
    return new in ALLOWED_TRANSITIONS.get(old, set())


def same_status_message(current: str) -> str:
    """目标状态与当前状态一致时的中文说明，用作 409 响应的 detail。"""
    names = {STOCKED: "在养", QUARANTINE: "隔离", DRY: "干塘"}
    return f"塘口已处于{names.get(current, current)}状态，状态未变更"


def illegal_transition_message(old: str, new: str) -> str:
    """非法流转的中文说明，用作 409 响应的 detail。"""
    if old == DRY and new == QUARANTINE:
        return "干塘不能直接转隔离，须先恢复为在养（dry → stocked → quarantine）"
    names = {STOCKED: "在养", QUARANTINE: "隔离", DRY: "干塘"}
    return f"状态不可跳转：{names.get(old, old)} → {names.get(new, new)}"
