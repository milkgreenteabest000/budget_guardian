"""信任分數與裁決模組。

把「怎麼算分」(`trust_score`) 與「怎麼裁決」(`decision`) 放在同一個子套件，
與 `runtime`／`core.infra`／整合層分離，方便維護與日後獨立部署。
"""

from .decision import (
    ALLOW,
    ANNOUNCE,
    DENY,
    REQUIRE_APPROVAL,
    ALLOW_SCORE_THRESHOLD,
    ANNOUNCE_SCORE_THRESHOLD,
    REQUIRE_APPROVAL_SCORE_THRESHOLD,
    make_decision,
)
from .trust_score import (
    BEHAVIOR_WEIGHT,
    IDENTITY_WEIGHT,
    REPUTATION_WEIGHT,
    USER_POLICY_WEIGHT,
    evaluate_trust_score,
    is_blacklisted,
)

__all__ = [
    "ALLOW",
    "ANNOUNCE",
    "DENY",
    "REQUIRE_APPROVAL",
    "ALLOW_SCORE_THRESHOLD",
    "ANNOUNCE_SCORE_THRESHOLD",
    "REQUIRE_APPROVAL_SCORE_THRESHOLD",
    "BEHAVIOR_WEIGHT",
    "IDENTITY_WEIGHT",
    "REPUTATION_WEIGHT",
    "USER_POLICY_WEIGHT",
    "evaluate_trust_score",
    "is_blacklisted",
    "make_decision",
]
