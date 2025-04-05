import os
import unittest

import requests_mock

from tests._testUtils import mock_upload_response_by_videobasename, copy_testfiles_to_tubeup_rootdir, SCANNER, \
    current_path, get_testfile_path
from tubeup.Component.IAUploader import IAUploader


class IAUploaderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        copy_testfiles_to_tubeup_rootdir()

    def test_upload_ia(self):
        uploader = IAUploader(get_testfile_path('ia_config_for_test.ini'), True)

        videobasename = os.path.join(
            current_path, 'test_tubeup_rootdir', 'downloads',
            'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A')

        with requests_mock.Mocker() as m:
            # Mock the request to s3.us.archive.org, so it will responds
            # a custom json. `internetarchive` library sends GET request to
            # that url to check that we don't violate the upload limit.
            m.get('https://s3.us.archive.org',
                  content=b'{"over_limit": 0}',
                  headers={'content-type': 'application/json'})

            m.get('https://archive.org/metadata/youtube-6iRV8liah8A',
                  content=b'{}',
                  headers={'content-type': 'application/json'})

            # Mock the PUT requests for internetarchive urls that defined
            # in mock_upload_response_by_videobasename(), so this test
            # doesn't perform upload to the real archive.org server.
            mock_upload_response_by_videobasename(
                m, 'youtube-6iRV8liah8A', videobasename)

            result = uploader.upload_ia(videobasename)

            expected_result = (
                'youtube-6iRV8liah8A',
                {'mediatype': 'movies',
                 'channel': 'http://www.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg',
                 'creator': 'Video Background',
                 'collection': 'opensource_movies',
                 'title': 'Mountain 3 - Video Background HD 1080p',
                 'description': ('Mountain 3 - Video Background HD 1080p<br>If '
                                 'you use this video please put credits to my'
                                 ' channel in description:<br>https://www.youtub'
                                 'e.com/channel/UCWpsozCMdAnfI16rZHQ9XDg<br>© D'
                                 'on\'t forget to SUBSCRIBE, LIKE, COMMENT an'
                                 'd RATE. Hope you all enjoy!'),
                 'date': '2015-01-05',
                 'year': '2015',
                 'subject': ('Youtube;video;Entertainment;Video Background;'
                             'Footage;Animation;Cinema;stock video footage;'
                             'Royalty free videos;Creative Commons videos;'
                             'free movies online;youtube;HD;1080p;Amazing '
                             'Nature;Mountain;'),
                 'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
                 'licenseurl': 'https://creativecommons.org/licenses/by/3.0/',
                 'scanner': SCANNER})

            self.assertEqual(expected_result, result)
