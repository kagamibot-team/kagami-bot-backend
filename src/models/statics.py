from dataclasses import dataclass


@dataclass
class _CatchLevel:
    search_names: list[str]
    display_name: str
    weight: float
    color: str
    awarding: int
    sorting_priority: int = 0


@dataclass
class CatchLevel(_CatchLevel):
    """
    抓小哥中小哥的等级
    """

    id: int = -1


class LevelRepository:
    """
    管理小哥等级数据的数据管理器，在生产环境中应保持只读
    """

    _LEVELS: dict[int, _CatchLevel] = {}

    def _register(
        self,
        id: int,
        search_names: list[str],
        display_name: str,
        weight: float,
        color: str,
        awarding: int,
        sorting_priority: int = 0,
    ):
        self._LEVELS[id] = _CatchLevel(
            search_names=search_names,
            display_name=display_name,
            weight=weight,
            color=color,
            awarding=awarding,
            sorting_priority=sorting_priority,
        )

    def clear(self):
        self._LEVELS = {}

    def register_basics(self):
        self._register(1, ["一星", "一", "1"], "★", 65, "#C6C1BF", 2)
        self._register(2, ["二星", "二", "2"], "★★", 24.5, "#C0E8AE", 5)
        self._register(3, ["三星", "三", "3"], "★★★", 8, "#BDDAF5", 10)
        self._register(4, ["四星", "四", "4"], "★★★★", 2.0, "#D4BCE3", 40)
        self._register(5, ["五星", "五", "5"], "★★★★★", 0.5, "#F1DD95", 120)
        self._register(0, ["零星", "零", "0"], "☆", 0, "#9e9d95", 0, -1)

    @property
    def levels(self):
        return {
            lid: CatchLevel(**(level.__dict__), id=lid)
            for lid, level in self._LEVELS.items()
        }

    @property
    def sorted(self):
        return sorted(
            self.levels.values(), key=lambda l: (-l.sorting_priority, l.weight)
        )
    
    @property
    def sorted_index(self):
        return {v.id: i for i, v in enumerate(self.sorted)}

    @property
    def name_index(self):
        return {
            **{level.display_name: level for level in self.sorted},
            **{name: level for level in self.sorted for name in level.search_names},
        }

    def get_by_name(self, name: str):
        return self.name_index.get(name)


# 目前暂时以单例模式运作
level_repo = LevelRepository()
"小哥等级的单例"

level_repo.register_basics()


__all__ = ["LevelRepository", "level_repo"]
