from src.services.items.base import register_item
from src.services.items.skin_pack import ItemSkinPack


def init_base_items():
    register_item(ItemSkinPack())
