from src.base.local_storage import Action, LocalStorageManager, XBRecord
from src.imports import *


@root.listen(PrePickMessageEvent)
async def _(evt: PrePickMessageEvent):
    """
    记录喜报
    """

    if evt.group_id is None:
        # 并不是在群里抓的，就不记录喜报了
        return

    data: list[str] = []
    for aid, pick in evt.picks.awards.items():
        if pick.level in (4, 5):
            disp = evt.displays[aid]
            new_hint = "（新）" if disp.pick.beforeStats == 0 else ""
            data.append(f"{disp.name} ×{disp.pick.delta}{new_hint}")

    if len(data) > 0:
        LocalStorageManager.instance().data.add_xb(
            evt.group_id,
            await get_qqid_by_uid(evt.session, evt.uid),
            XBRecord(time=now_datetime(), action=Action.catched, data="，".join(data)),
        )
        LocalStorageManager.instance().save()
