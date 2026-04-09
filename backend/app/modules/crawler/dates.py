from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

_VN = ZoneInfo("Asia/Ho_Chi_Minh")


def today_vn() -> date:
    """Ngày theo múi giờ Việt Nam (anchor cho skip/cập nhật 'hôm nay')."""
    return datetime.now(_VN).date()
