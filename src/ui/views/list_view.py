from loguru import logger
from pydantic import BaseModel

from src.models.level import Level

from .award import StorageDisplay
from .user import UserData


def _try_int(value: str | int) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


class ListView(BaseModel):
    """
    在界面中排列的小哥图鉴
    """

    awards: list[StorageDisplay | None]
    "小哥的图鉴，如果留空则为未知"


class TitleView(BaseModel):
    """
    标题
    """

    title: str
    "标题"

    color: str = "#FFFFFF"
    "标题颜色"

    size: int = 20
    "标题大小"


class ListViewDocument(BaseModel):
    """
    整个小哥图鉴，例如库存，使用的渲染界面
    """

    docs: list[ListView | str | int | TitleView]
    "图鉴列表，如果是字符串则为标题，如果是整数则为空行"

    columns: int = 8
    "每行显示多少个图鉴"

    @property
    def inner_width(self):
        return 216 * self.columns

    @property
    def width(self):
        return self.inner_width + 60


class UserStorageView(BaseModel):
    user: UserData | None
    "玩家数据"

    awards: list[tuple[Level, list[StorageDisplay | None]]] = []
    "一个玩家所有的小哥"

    limited_level: Level | None = None

    @property
    def prog_title(self) -> str:
        "进度标题"
        if self.limited_level is None:
            return f"{self.user_name}抓小哥进度：{self.progress:.2%}"
        return f"{self.user_name}{self.limited_level.display_name}进度："

    @property
    def storage_title(self) -> str:
        "进度标题"
        if self.limited_level is None:
            return f"{self.user_name}库存"
        return f"{self.user_name}{self.limited_level.display_name}库存"

    @property
    def user_name(self) -> str:
        "玩家名字"

        return self.user.name + " 的" if self.user is not None else ""

    @property
    def progress(self) -> float:
        "进度"
        param: int = 10  # 榆木华定义的常数
        denominator: float = 0
        progress: float = 0

        for level, awards in self.awards:
            if level.weight == 0:
                continue
            numerator: float = 1 / (level.weight ** (1 / param))
            logger.info(
                f"{level.display_name}: {level.weight} ^ {1 / param} = " f"{numerator}"
            )
            denominator += numerator
            progress += numerator * (
                len([a for a in awards if a is not None]) / len(awards)
            )

        return progress / denominator if denominator != 0 else 0

    def progress_docs(
        self, show_progress: bool = True, show_all: bool = True
    ) -> list[ListView | TitleView]:
        "图鉴列表"
        ls: list[ListView | TitleView] = []
        for level, awards in self.awards:
            if level.lid == 0 and self.user is not None:
                awards = [a for a in awards if a is not None and a.stats != 0]
                if len(awards) == 0:
                    continue
            title = f"{level.display_name}"
            if show_progress and level.lid != 0:
                title += f"：{len([a for a in awards if a is not None])}/{len(awards)}"
            if not show_all:
                awards: list[StorageDisplay | None] = [
                    award for award in awards if award is not None
                ]

            ls.append(TitleView(title=title, size=80, color=level.color))
            ls.append(ListView(awards=awards))
        return ls

    @property
    def storage_document(self) -> ListViewDocument:
        "库存视图"
        docs: list[ListView | str | int | TitleView] = [
            TitleView(title=self.storage_title, size=80)
        ]
        awards: list[StorageDisplay | None] = []
        for _, awds in self.awards:
            awards += sorted(
                [i for i in awds if i is not None and i.storage > 0],
                key=lambda x: (-x.storage, x.info.aid, x.info.sorting),
            )
        docs.append(ListView(awards=awards))
        return ListViewDocument(docs=docs)

    @property
    def prog_document(self) -> ListViewDocument:
        "抓小哥进度视图"
        docs: list[ListView | str | int | TitleView] = [
            TitleView(title=self.prog_title, size=80)
        ]
        docs.extend(self.progress_docs(show_progress=True, show_all=True))
        return ListViewDocument(docs=docs)
