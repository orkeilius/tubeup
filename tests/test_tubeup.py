import unittest
from unittest.mock import patch

import requests_mock
import logging

from tests.FakeDlp.FakeYDL import FakeYDL
from tests._testUtils import *

from tubeup.TubeUp import TubeUp

@patch("tubeup.Component.YtdlpWrapper.YoutubeDL", FakeYDL)
class TubeUpTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tu = TubeUp()
        self.maxDiff = 999999999
        copy_testfiles_to_tubeup_rootdir()


    def test_tubeup_attribute_logger_when_quiet_mode(self):
        # self.tu is already `TubeUp` instance with quiet mode, so we don't
        # create a new instance here.
        self.assertIsInstance(self.tu.logger, logging.Logger)
        self.assertEqual(self.tu.logger.level, logging.ERROR)

    def test_tubeup_attribute_logger_when_verbose_mode(self):
        tu = TubeUp(verbose=True)
        self.assertIsInstance(tu.logger, logging.Logger)

    def test_archive_urls(self):
        tu = TubeUp(dir_path=os.path.join(current_path,
                                          'test_tubeup_rootdir'),
                    ia_config_path=get_testfile_path('ia_config_for_test.ini'))

        videobasename = os.path.join(
            current_path, 'test_tubeup_rootdir', 'downloads',
            'KdsN9YhkDrY')

        copy_testfiles_to_tubeup_rootdir()

        with requests_mock.Mocker() as m:
            # Mock the request to s3.us.archive.org, so it will responds
            # a custom json. `internetarchive` library sends GET request to
            # that url to check that we don't violate the upload limit.
            m.get('https://s3.us.archive.org',
                  content=b'{"over_limit": 0}',
                  headers={'content-type': 'application/json'})

            m.get('https://archive.org/metadata/youtube-KdsN9YhkDrY',
                  content=b'{}',
                  headers={'content-type': 'application/json'})



            # Mock the PUT requests for internetarchive urls that defined
            # in mock_upload_response_by_videobasename(), so this test
            # doesn't perform upload to the real archive.org server.
            mock_upload_response_by_videobasename(
                m, 'youtube-KdsN9YhkDrY', videobasename)

            result = list(tu.archive_urls(
                ['https://www.youtube.com/watch?v=KdsN9YhkDrY']))

            expected_result = [(
                'youtube-KdsN9YhkDrY',
                {'mediatype': 'movies',
                 'creator': 'RelaxingWorld',
                 'channel': 'http://www.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg',
                 'collection': 'opensource_movies',
                 'title': 'Epic Ramadan - Video Background HD1080p',
                 'description': ('If you enjoy my work, please consider Subscribe to my NEW '
                                 'channel for more videos: <br>'
                                 'https://www.youtube.com/MusicForRelaxation?sub_confirmation=1 <br>'
                                 '▷ If you use this video, please put credits to my channel '
                                 'in description: <br>'
                                 'Source from RelaxingWorld: https://goo.gl/HsW75m<br>'
                                 '<br>'
                                 '▷ Also, do not forget to Subscribe to my channel. Thanks!'),
                 'date': '2016-06-25',
                 'year': '2016',
                 'subject': ('Youtube;video;Film & Animation;Video Background;'
                             'Footage;Animation;Cinema;Royalty Free Videos;'
                             'Stock Video Footage;Video Backdrops;'
                             'Amazing Nature;youtube;HD;1080p;Creative Commons Videos;'
                             'relaxing music;Ramadan;'),
                 'originalurl': 'https://www.youtube.com/watch?v=KdsN9YhkDrY',
                 'licenseurl': '',
                 'scanner': SCANNER})]

            self.assertEqual(expected_result, result)
