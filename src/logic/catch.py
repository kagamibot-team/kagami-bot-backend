from src.base.exceptions import NoAwardException
from src.common.dataclasses import Pick, Picks
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.services.pool import PoolService


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

    pool_service = PoolService(uow)
    picked: list[int] = []
    aids_set = await pool_service.get_aids(uid)
    aids = await uow.awards.group_by_level(aids_set)

    picks = Picks(
        awards={},
        money=0,
        uid=uid,
        pid=await pool_service.get_current_pack(uid),
    )
    assert count >= 0

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

        if get_random().random() < up_pool_posibility[level.lid]:
            _aids = await pool_service.get_up_aids(uid)
            _grouped = await uow.awards.group_by_level(_aids)
            _limited = _grouped.get(level.lid, set())
            if len(_limited) > 0:
                limited_aids = _grouped[level.lid]

        aid = get_random().choice(list(limited_aids))
        picked.append(aid)

    new_calculated: set[int] = set()

    for aid in picked:
        if aid not in picks.awards:
            picks.awards[aid] = Pick(
                beforeStats=await uow.inventories.get_stats(uid, aid),
                delta=0,
                level=await uow.awards.get_lid(aid),
            )

        picks.awards[aid].delta += 1
        picks.money += uow.levels.get_by_id(picks.awards[aid].level).awarding

        if picks.awards[aid].beforeStats == 0 and aid not in new_calculated:
            picks.money += 20
            new_calculated.add(aid)
        elif aid == 35:
            # 处理百变小哥
            await handle_baibianxiaoge(uow, uid)
    return picks


async def handle_baibianxiaoge(uow: UnitOfWork, uid: int) -> int | None:
    sids = await uow.skins.get_all_sids_of_one_award(35)
    sids = [sid for sid in sids if not await uow.skin_inventory.do_user_have(uid, sid)]
    if len(sids) > 0:
        sid = get_random().choice(sids)
        await uow.skin_inventory.give(uid, sid)
        await uow.skin_inventory.use(uid, 35, sid)
        return sid
