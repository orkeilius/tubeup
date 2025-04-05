import logging
import os
import unittest

from tubeup.Helper.DirPath import DirPath

from tubeup.config.Ydl_options_factory import Ydl_options_factory

dir_path = DirPath("~/.tubeup'")


def mocked_ydl_progress_hook(d):
    pass


class Ydl_options_factoryTest(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_generate_ydl_options_with_download_archive(self):
        result = Ydl_options_factory.generate_ydl_options(dir_path, self.logger,
                                                          mocked_ydl_progress_hook,
                                                          use_download_archive=True)

        expected_result = {
            'outtmpl': os.path.join(
                dir_path.downloads, '%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
            'quiet': True,
            'download_archive': os.path.join(dir_path.root,
                                             '.ytdlarchive'),
            'progress_with_newline': True,
            'forcetitle': True,
            'continuedl': True,
            'retries': 9001,
            'fragment_retries': 9001,
            'forcejson': False,
            'writeinfojson': True,
            'writedescription': True,
            'writethumbnail': True,
            'writeannotations': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [mocked_ydl_progress_hook]}
        print(expected_result)
        self.assertEqual(result, expected_result)

    def test_generate_ydl_options(self):
        result = Ydl_options_factory.generate_ydl_options(dir_path, self.logger, mocked_ydl_progress_hook)
        expected_result = {
            'outtmpl': os.path.join(
                dir_path.downloads, '%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
            'quiet': True,
            'progress_with_newline': True,
            'forcetitle': True,
            'continuedl': True,
            'retries': 9001,
            'fragment_retries': 9001,
            'forcejson': False,
            'writeinfojson': True,
            'writedescription': True,
            'writethumbnail': True,
            'writeannotations': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [mocked_ydl_progress_hook]}
        self.assertEqual(result, expected_result)

    def test_generate_ydl_options_with_proxy(self):
        result = Ydl_options_factory.generate_ydl_options(dir_path, self.logger,
                                                          mocked_ydl_progress_hook,
                                                          proxy_url='http://proxytest.com:8080')
        expected_result = {
            'outtmpl': os.path.join(
                dir_path.downloads, '%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
            'quiet': True,
            'progress_with_newline': True,
            'forcetitle': True,
            'continuedl': True,
            'retries': 9001,
            'fragment_retries': 9001,
            'forcejson': False,
            'writeinfojson': True,
            'writedescription': True,
            'writethumbnail': True,
            'writeannotations': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [mocked_ydl_progress_hook],
            'proxy': 'http://proxytest.com:8080'}
        self.assertEqual(result, expected_result)

    def test_generate_ydl_options_with_ydl_account(self):
        result = Ydl_options_factory.generate_ydl_options(dir_path, self.logger,
                                                          mocked_ydl_progress_hook, ydl_username='testUsername',
                                                          ydl_password='testPassword')
        expected_result = {
            'outtmpl': os.path.join(
                dir_path.downloads, '%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': False,
            'quiet': True,
            'progress_with_newline': True,
            'forcetitle': True,
            'continuedl': True,
            'retries': 9001,
            'fragment_retries': 9001,
            'forcejson': False,
            'writeinfojson': True,
            'writedescription': True,
            'writethumbnail': True,
            'writeannotations': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [mocked_ydl_progress_hook],
            'username': 'testUsername',
            'password': 'testPassword'}
        self.assertEqual(result, expected_result)

    def test_generate_ydl_options_with_verbose_mode(self):
        result = Ydl_options_factory.generate_ydl_options(dir_path, self.logger,
                                                          mocked_ydl_progress_hook, ydl_username='testUsername',
                                                          ydl_password='testPassword', verbose=True)
        expected_result = {
            'outtmpl': os.path.join(
                dir_path.downloads, '%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'verbose': True,
            'quiet': False,
            'progress_with_newline': True,
            'forcetitle': True,
            'continuedl': True,
            'retries': 9001,
            'fragment_retries': 9001,
            'forcejson': False,
            'writeinfojson': True,
            'writedescription': True,
            'writethumbnail': True,
            'writeannotations': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'ignoreerrors': True,
            'fixup': 'warn',
            'nooverwrites': True,
            'consoletitle': True,
            'prefer_ffmpeg': True,
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [mocked_ydl_progress_hook],
            'username': 'testUsername',
            'password': 'testPassword'}
        self.assertEqual(result, expected_result)
