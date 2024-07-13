import re
from dataclasses import dataclass

from nonebot.adapters.onebot.v11 import Message

from src.models import *

from .db import *
from .keywords import *
from .old_version import CheckEnvironment, Command, at, databaseIO, text
from .tools import requireAdmin


@requireAdmin
@databaseIO()
@dataclass
class CatchAddSkin(Command):
    commandPattern: str = f"^:: ?{KEYWORD_CREATE} ?{KEYWORD_SKIN} "
    argsPattern: str = "(\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_CREATE_SKIN_WRONG_FORMAT")])

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        award = await getAwardByName(env.session, result.group(3))

        if award is None:
            return self.notExists(env, result.group(3))

        skin = await getSkinByName(env.session, result.group(4))

        if skin is not None:
            return Message([at(env.sender), text("MSG_SKIN_ALREADY_EXISTS")])

        skin = Skin(name=result.group(4), award=award)

        env.session.add(skin)

        return Message([at(env.sender), text("MSG_SKIN_ADDED_SUCCESSFUL")])


@requireAdmin
@databaseIO()
@dataclass
class AddAltName(Command):
    commandPattern: str = (
        f"^:: ?{KEYWORD_CREATE}({KEYWORD_AWARDS}|{KEYWORD_LEVEL}|{KEYWORD_SKIN}) ?{KEYWORD_ALTNAME} (\\S+) (\\S+)"
    )
    argsPattern: str = ""

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        ty = result.group(2)
        name = result.group(7)
        alt = result.group(8)

        if re.match(KEYWORD_AWARDS, ty):
            award = await getAwardByName(env.session, name)
            if award is None:
                return self.notExists(env, name)

            if await createAwardAltName(env.session, award, alt):
                return Message([at(env.sender), text("MSG_ADD_ALTNAME_OK")])
            return Message([at(env.sender), text("MSG_ALTNAME_EXISTS")])

        if re.match(KEYWORD_SKIN, ty):
            skin = await getSkinByName(env.session, name)
            if skin is None:
                return self.notExists(env, name)

            if await createSkinAltName(env.session, skin, alt):
                return Message([at(env.sender), text("MSG_ADD_ALTNAME_OK")])
            return Message([at(env.sender), text("MSG_ALTNAME_EXISTS")])

        return Message([at(env.sender), text("MSG_ADD_ALTNAME_WRONG_TYPE")])


@requireAdmin
@databaseIO()
@dataclass
class RemoveAltName(Command):
    commandPattern: str = (
        f"^:: ?{KEYWORD_REMOVE}({KEYWORD_AWARDS}|{KEYWORD_LEVEL}|{KEYWORD_SKIN}) ?{KEYWORD_ALTNAME} (\\S+)"
    )
    argsPattern: str = ""

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        ty = result.group(2)
        alt = result.group(7)

        if re.match(KEYWORD_AWARDS, ty):
            obj = await getAwardAltNameObject(env.session, alt)
        elif re.match(KEYWORD_SKIN, ty):
            obj = await getSkinAltNameObject(env.session, alt)
        else:
            obj = None

        if obj is None:
            return Message([at(env.sender), text("MSG_ALTNAME_NOT_EXISTS")])

        await deleteObj(env.session, obj)
        return Message([at(env.sender), text("MSG_REMOVE_ALTNAME_OK")])
