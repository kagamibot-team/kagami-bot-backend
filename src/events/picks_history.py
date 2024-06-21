import time
from src.imports import *


@root.listen(PrePickMessageEvent)
async def _(evt: PrePickMessageEvent):
    if evt.group_id is None:
        return

    tag = await get_or_create_tag(evt.session, "记录", "喜报")
    query = select(LevelTagRelation.level_id).filter(LevelTagRelation.tag_id == tag)
    levels = (await evt.session.execute(query)).scalars().all()

    flag = False
    _event_picks: dict[int, PickDisplay] = {}

    for aid, pick in evt.picks.awards.items():
        if pick.level in levels:
            _event_picks[aid] = evt.displays[aid]
            flag = True

    if flag:
        catch_histroy_list.add_record(
            evt.group_id,
            CatchHistory(
                time.time(),
                _event_picks,
                evt.uid,
                int(await get_qqid_by_uid(evt.session, evt.uid)),
            ),
        )
