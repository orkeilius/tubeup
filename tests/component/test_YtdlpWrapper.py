import os
import unittest
from unittest.mock import patch

from yt_dlp import YoutubeDL

from build.lib.tubeup.Helper.DirPath import DirPath
from tests.FakeDlp.FakeYDL import FakeYDL
from tests._testUtils import copy_testfiles_to_tubeup_rootdir, current_path
from tests.constants import info_dict_playlist, info_dict_video
from tubeup.Component.YtdlpWrapper import YtdlpWrapper


@patch("tubeup.Component.YtdlpWrapper.YoutubeDL", FakeYDL)
class test_YtdlpWrapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        copy_testfiles_to_tubeup_rootdir()

    @classmethod
    @patch("tubeup.Component.YtdlpWrapper.YoutubeDL", FakeYDL)
    def setUp(cls) -> None:
        dir_path = DirPath(os.path.join(current_path, 'test_tubeup_rootdir'))
        cls.ydp: YtdlpWrapper = YtdlpWrapper(dir_path, ignore_existing_item=True)

    def test_get_resource_basenames(self) -> None:
        result = self.ydp.download(self.ydp.get_video_info(['https://www.youtube.com/watch?v=KdsN9YhkDrY'])
                                   )

        expected_result = {os.path.join(
            current_path, 'test_tubeup_rootdir', 'downloads',
            'KdsN9YhkDrY')}

        self.assertEqual(expected_result, result)

    def test_create_basenames_from_ydl_info_dict_video(self) -> None:
        self.ydp.ydl = YoutubeDL()
        result = self.ydp.create_basename_from_ydl_video(info_dict_video)

        expected_result = ('Video and Blog Competition 2017 - Bank Indonesia & '
                           'NET TV #BIGoesToCampus [hlG3LeFaQwU]')

        self.assertEqual(expected_result, result)

    def test_create_basenames_from_ydl_info_dict_playlist(self) -> None:
        self.ydp.ydl = YoutubeDL()
        result = self.ydp.create_basename_from_ydl_video(info_dict_playlist)

        expected_result = {'Live Streaming Rafid Aslam [7gjgkH5iPaE]', 'Live Streaming Rafid Aslam [q92kxPm-pqM]',
                           'Cara Membuat Laptop Menjadi Hotspot WiFi Dengan CMD [YjFwMSDNphM]',
                           '[CSO] Defeat Boss in Dead End With Thanatos 7 [EEm6MwXLse0]',
                           'Cara Bermain Minecraft Multiplayer Dengan LAN [g2vTZ2ka-tM]',
                           'Live Streaming Rafid Aslam [AXhuSS5_9YU]',
                           'Cara Membuat Disk Baru di Komputer [KDOygJnK7Sw]',
                           'Cara Mendownload Lewat Torrent [cC-9RghkvXs]'}

        self.assertEqual(expected_result, result)
