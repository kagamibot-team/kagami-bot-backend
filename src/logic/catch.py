from src.base.exceptions import NoAwardException
from src.common.dataclasses import Pick, Picks
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork


async def pickAwards(uow: UnitOfWork, uid: int, count: int) -> Picks:
    """
    在内存中进行一次抓小哥，结果先不会保存到数据库中。
    调用该函数前，请**一定要**先验证 `count` 是否在合适范围内。

    Args:
        uow (UnitOfWork): 工作单元
        uid (int): 用户在数据库中的 ID
        count (int): 抓小哥的次数

    Returns:
        Picks: 抓小哥结果的记录
    """

    up_pool_posibility = {1: 0.1, 2: 0.2, 3: 0.4, 4: 0.5, 5: 0.6}

    picks = Picks(awards={}, money=0, uid=uid)
    assert count >= 0

    picked: list[int] = []

    pack_id = await uow.user_pack.get_using(uid)
    aids_set = await uow.awards.get_all_awards_in_pack(pack_id)
    aids = await uow.awards.group_by_level(aids_set)

    levels = [uow.levels.get_by_id(i) for i in aids]
    weights = [level.weight for level in levels]

    if len(levels) == 0:
        raise NoAwardException()

    # 开始抓小哥
    for _ in range(count):
        # 对是小哥进行特判
        if await uow.user_flag.have(uid, "是"):
            await uow.user_flag.remove(uid, "是")
            shi = await uow.awards.get_aid("是小哥")
            if shi is None:
                pass
            else:
                picked.append(shi)
                continue

        level = get_random().choices(levels, weights)[0]
        limited_aids = aids[level.lid]

        using_up = await uow.up_pool.get_using(uid)
        if using_up is not None:
            if get_random().random() < up_pool_posibility[level.lid]:
                _aids = await uow.up_pool.get_aids(using_up)
                if len(_aids) > 0:
                    _grouped = await uow.awards.group_by_level(_aids)
                    limited_aids = _grouped[level.lid]

        aid = get_random().choice(list(limited_aids))
        picked.append(aid)

    met_35 = False

    for aid in picked:
        if aid not in picks.awards:
            picks.awards[aid] = Pick(
                beforeStats=await uow.inventories.get_stats(uid, aid),
                delta=0,
                level=await uow.awards.get_lid(aid),
            )

        picks.awards[aid].delta += 1
        picks.money += uow.levels.get_by_id(picks.awards[aid].level).awarding

        if picks.awards[aid].beforeStats == 0:
            picks.money += 20
        elif aid == 35 and not met_35:
            # 处理百变小哥
            met_35 = True
            sids = await uow.skins.get_all_sids_of_one_award(35)
            sids = [
                sid
                for sid in sids
                if not await uow.skin_inventory.do_user_have(uid, sid)
            ]
            if len(sids) > 0:
                sid = get_random().choice(sids)
                await uow.skin_inventory.give(uid, sid)
    return picks
