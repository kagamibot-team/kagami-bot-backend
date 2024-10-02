from unittest import TestCase

from src.common.dialogue import get_dialog, handle_single_line_dialogue
from src.ui.types.common import DialogueMessage


class TestDialogue(TestCase):
    def test_handle(self):
        self.assertEqual(
            handle_single_line_dialogue("小明 开心：你说的对"),
            DialogueMessage(
                speaker="小明",
                face="开心",
                text="你说的对",
                scene=None,
            ),
        )
        self.assertEqual(
            handle_single_line_dialogue("小明 开心:你说的对"),
            None,
        )
        self.assertEqual(
            handle_single_line_dialogue("开心小明：你说的对"),
            None,
        )
        self.assertEqual(
            handle_single_line_dialogue("开心 ：你说的对"),
            None,
        )
        self.assertEqual(
            handle_single_line_dialogue(" 啊啊啊：你说的对"),
            None,
        )
        self.assertEqual(
            handle_single_line_dialogue("小明 开心：你说的对：：："),
            DialogueMessage(
                speaker="小明",
                face="开心",
                text="你说的对：：：",
                scene=None,
            ),
        )
        self.assertEqual(
            handle_single_line_dialogue("测试场景|小明 开心：你说的对！！"),
            DialogueMessage(
                speaker="小明",
                face="开心",
                text="你说的对！！",
                scene=set(["测试场景"]),
            ),
        )
        self.assertEqual(
            handle_single_line_dialogue("测试场景A,测试场景B|小明 开心：你说的对"),
            DialogueMessage(
                speaker="小明",
                face="开心",
                text="你说的对",
                scene=set(["测试场景A", "测试场景B"]),
            ),
        )

    def test_get_dialog_list(self):
        A = DialogueMessage(speaker="小明", face="开心", text="内容")
        B = DialogueMessage(
            speaker="小明", face="开心", text="内容", scene=set(["scene_a"])
        )
        C = DialogueMessage(
            speaker="小明", face="开心", text="内容", scene=set(["scene_a", "scene_b"])
        )
        D = DialogueMessage(
            speaker="小明",
            face="开心",
            text="内容",
            scene=set(["scene_b", "scene_c"]),
        )

        self.assertListEqual([A], get_dialog([A]))
        self.assertListEqual([A, B], get_dialog([A, B]))
        self.assertListEqual([A, B], get_dialog([A, B, D], set(["scene_a"])))
