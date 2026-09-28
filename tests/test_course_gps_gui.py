import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import Zuvio
from Zuvio import ZuvioBot


class FakeVar:
    def __init__(self, value=''):
        self.value = value
        self.destroyed = False

    def get(self):
        if self.destroyed:
            raise Zuvio.tk.TclError('application has been destroyed')
        return self.value

    def set(self, value):
        self.value = value


@unittest.skipUnless(Zuvio.GUI_AVAILABLE, 'tkinter / customtkinter 未安裝')
class CourseGpsGuiTests(unittest.TestCase):
    """以假的 self 呼叫 ZuvioGUI 方法，不需要實際開啟視窗。"""

    def setUp(self):
        fd, self.config_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({'user': 'u', 'pass': 'p', 'course_gps': {}}, f)

        bot = ZuvioBot()
        bot.config_file = self.config_path
        bot.course_gps = {}
        self.gui = SimpleNamespace(bot=bot, course_gps_vars={})
        self.gui.on_course_gps_changed = (
            lambda course_id: Zuvio.ZuvioGUI.on_course_gps_changed(self.gui, course_id)
        )

    def tearDown(self):
        os.remove(self.config_path)

    def saved_course_gps(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('course_gps')

    def test_flush_saves_pending_edit(self):
        self.gui.course_gps_vars = {'course-1': FakeVar('24.5, 120.5')}

        Zuvio.ZuvioGUI.flush_course_gps_edits(self.gui)

        self.assertEqual(self.gui.bot.course_gps, {'course-1': '24.5, 120.5'})
        self.assertEqual(self.saved_course_gps(), {'course-1': '24.5, 120.5'})

    def test_flush_before_courses_loaded_does_nothing(self):
        del self.gui.course_gps_vars

        Zuvio.ZuvioGUI.flush_course_gps_edits(self.gui)

        self.assertEqual(self.saved_course_gps(), {})

    def test_unchanged_value_does_not_rewrite_config(self):
        self.gui.bot.course_gps = {'course-1': '24.5, 120.5'}
        self.gui.course_gps_vars = {'course-1': FakeVar('24.5, 120.5')}

        with patch('builtins.open') as mock_open:
            Zuvio.ZuvioGUI.on_course_gps_changed(self.gui, 'course-1')

        mock_open.assert_not_called()

    def test_invalid_pending_edit_is_reverted_not_saved(self):
        self.gui.course_gps_vars = {'course-1': FakeVar('bad value')}

        with patch.object(Zuvio.messagebox, 'showerror') as showerror:
            Zuvio.ZuvioGUI.flush_course_gps_edits(self.gui)

        showerror.assert_called_once()
        self.assertEqual(self.gui.course_gps_vars['course-1'].value, '')
        self.assertEqual(self.saved_course_gps(), {})

    def test_destroyed_widget_is_ignored(self):
        var = FakeVar('24.5, 120.5')
        var.destroyed = True
        self.gui.course_gps_vars = {'course-1': var}

        Zuvio.ZuvioGUI.on_course_gps_changed(self.gui, 'course-1')
        Zuvio.ZuvioGUI.on_course_gps_changed(self.gui, 'missing-course')

        self.assertEqual(self.saved_course_gps(), {})


if __name__ == '__main__':
    unittest.main()
