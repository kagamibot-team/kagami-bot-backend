import time

from src.imports import *


@root.listen(PrePickMessageEvent)
async def _(evt: PrePickMessageEvent):
    if evt.group_id is None:
        return

    flag = False
    _event_picks: dict[int, PickDisplay] = {}

    for aid, pick in evt.picks.awards.items():
        if pick.level in (4, 5):
            _event_picks[aid] = evt.displays[aid]
            flag = True

    if flag:
        catch_history_list.add_record(
            evt.group_id,
            CatchHistory(
                caught_time=time.time(),
                displays=_event_picks,
                uid=evt.uid,
                qqid=int(await get_qqid_by_uid(evt.session, evt.uid)),
            ),
        )
