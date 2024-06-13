from nonebot_plugin_orm import AsyncSession, async_scoped_session


Session = async_scoped_session | AsyncSession
