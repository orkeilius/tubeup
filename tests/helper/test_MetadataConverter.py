import time
import json
import os
import unittest

from tubeup import __version__
from tubeup.Helper.MetadataConverter import MetadataConverter

SCANNER = 'TubeUp Video Stream Mirroring Application {}'.format(__version__)


def get_testfile_path(name):
    current_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_path, '../test_tubeup_files', name)


class MetadataConverterTest(unittest.TestCase):
    def test_determine_collection_type(self):
        soundcloud_colltype = MetadataConverter.determine_collection_type('https://soundcloud.com/testurl')
        self.assertEqual(soundcloud_colltype, 'opensource_audio')

        another_colltype = MetadataConverter.determine_collection_type('https://www.youtube.com/watch?v=testVideo')
        self.assertEqual(another_colltype, 'opensource_movies')

    def test_create_archive_org_metadata_from_youtubedl_meta(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.info.json')
        ) as f:
            vid_meta = json.load(f)

        result = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        expected_result = {
            'mediatype': 'movies',
            'channel': 'http://www.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg',
            'creator': 'Video Background',
            'collection': 'opensource_movies',
            'title': 'Mountain 3 - Video Background HD 1080p',
            'description': ('Mountain 3 - Video Background HD 1080p<br>'
                            'If you use this video please put credits to my '
                            'channel in description:<br>https://www.youtube.com'
                            '/channel/UCWpsozCMdAnfI16rZHQ9XDg<br>© Don\'t '
                            'forget to SUBSCRIBE, LIKE, COMMENT and RATE. '
                            'Hope you all enjoy!'),
            'date': '2015-01-05',
            'year': '2015',
            'subject': ('Youtube;video;Entertainment;Video Background;Footage;'
                        'Animation;Cinema;stock video footage;Royalty '
                        'free videos;Creative Commons videos;free movies '
                        'online;youtube;HD;1080p;Amazing Nature;Mountain;'),
            'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
            'licenseurl': 'https://creativecommons.org/licenses/by/3.0/',
            'scanner': SCANNER}

        self.assertEqual(expected_result, result)

    def test_create_archive_org_metadata_from_youtubedl_meta_description_text_null(self):
        with open(get_testfile_path(
                'description_text_null.json')
        ) as f:
            vid_meta = json.load(f)

        result = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        expected_description = ('')

        self.assertEqual(expected_description, result.get('description'))

    def test_create_archive_org_metadata_from_youtubedl_meta_no_uploader(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.info_no_'
                'uploader.json')
        ) as f:
            vid_meta = json.load(f)

        result = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        expected_result = {
            'mediatype': 'movies',
            'channel': 'http://www.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg',
            'creator': 'http://www.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg',
            'collection': 'opensource_movies',
            'title': 'Mountain 3 - Video Background HD 1080p',
            'description': ('Mountain 3 - Video Background HD 1080p<br>'
                            'If you use this video please put credits to my '
                            'channel in description:<br>https://www.youtube.com'
                            '/channel/UCWpsozCMdAnfI16rZHQ9XDg<br>© Don\'t '
                            'forget to SUBSCRIBE, LIKE, COMMENT and RATE. '
                            'Hope you all enjoy!'),
            'date': '2015-01-05',
            'year': '2015',
            'subject': ('Youtube;video;Entertainment;Video Background;Footage;'
                        'Animation;Cinema;stock video footage;Royalty '
                        'free videos;Creative Commons videos;free movies '
                        'online;youtube;HD;1080p;Amazing Nature;Mountain;'),
            'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
            'licenseurl': 'https://creativecommons.org/licenses/by/3.0/',
            'scanner': SCANNER}

        self.assertEqual(expected_result, result)

    def test_create_archive_org_metadata_from_youtubedl_meta_no_date(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.'
                'info_no_date.json')
        ) as f:
            vid_meta = json.load(f)

        result = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        upload_date = time.strftime("%Y-%m-%d")
        upload_year = time.strftime("%Y")

        expected_result = {
            'mediatype': 'movies',
            'channel': 'http://www.youtube.com/channel/UCWpsozCMdAnfI16rZHQ9XDg',
            'creator': 'Video Background',
            'collection': 'opensource_movies',
            'title': 'Mountain 3 - Video Background HD 1080p',
            'description': ('Mountain 3 - Video Background HD 1080p<br>'
                            'If you use this video please put credits to my '
                            'channel in description:<br>https://www.youtube.com'
                            '/channel/UCWpsozCMdAnfI16rZHQ9XDg<br>© Don\'t '
                            'forget to SUBSCRIBE, LIKE, COMMENT and RATE. '
                            'Hope you all enjoy!'),
            'date': upload_date,
            'year': upload_year,
            'subject': ('Youtube;video;Entertainment;Video Background;Footage;'
                        'Animation;Cinema;stock video footage;Royalty '
                        'free videos;Creative Commons videos;free movies '
                        'online;youtube;HD;1080p;Amazing Nature;Mountain;'),
            'originalurl': 'https://www.youtube.com/watch?v=6iRV8liah8A',
            'licenseurl': 'https://creativecommons.org/licenses/by/3.0/',
            'scanner': SCANNER}

        self.assertEqual(expected_result, result)

    def test_create_archive_org_metadata_from_youtubedl_meta_twitch_clips(self):
        with open(get_testfile_path(
                'EA_Play_2016_Live_from_the_Novo_Theatre-42850523.info.json')
        ) as f:
            vid_meta = json.load(f)

        result = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(
            vid_meta
        )

        expected_result = {
            'mediatype': 'movies',
            'creator': 'EA',
            'collection': 'opensource_movies',
            'title': 'EA Play 2016 Live from the Novo Theatre',
            'description': (''),
            'date': '2016-06-12',
            'year': '2016',
            'subject': 'TwitchClips;video;',
            'originalurl': 'https://clips.twitch.tv/FaintLightGullWholeWheat',
            'licenseurl': '',
            'scanner': SCANNER}

        self.assertEqual(expected_result, result)

    def test_create_archive_org_metadata_from_youtubedl_meta_mass_of_tags(self):
        with open(get_testfile_path(
                'Mountain_3_-_Video_Background_HD_1080p-6iRV8liah8A.info.json')
        ) as f:
            vid_meta = json.load(f)

        vid_meta['tags'] = [f't{i}' for i in range(0, 300)]

        result = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(vid_meta)

        self.assertLessEqual(len(result['subject'].encode(encoding='utf-8')),
                             255, msg='tags_string not truncated to <= 255 bytes')
