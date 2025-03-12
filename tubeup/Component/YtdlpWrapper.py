import os
import re
import sys
from logging import getLogger
from typing import Optional, Union

import internetarchive
from logging import Logger
from tubeup.config.Ydl_options_factory import Ydl_options_factory

from tubeup.Helper import DirPath
from yt_dlp import YoutubeDL

from tubeup.utils import get_itemname


class YtdlpWrapper:

    def __init__(self, dir_path: DirPath,
                 cookie_file: str = None,
                 proxy_url: str = None,
                 ydl_username: str = None,
                 ydl_password: str = None,
                 use_download_archive: bool = False,
                 ignore_existing_item: bool = False,
                 verbose: bool = False,
                 ):
        self.logger: Logger = getLogger(__name__)
        self.dir_path: DirPath = dir_path
        self.ignore_existing_item: bool = ignore_existing_item
        self.verbose: bool = verbose

        self.ydl_opts = Ydl_options_factory.generate_ydl_options(self.dir_path, self.logger, self.ydl_progress_hook,
                                                                 cookie_file, proxy_url,
                                                                 ydl_username, ydl_password,
                                                                 use_download_archive)

        self.ydl = YoutubeDL(self.ydl_opts)

    def download(self, video_infos: list[any],
                 ) -> set[str]:
        """
        Download file from an urls.

        :param urls:                  A list of urls that will be downloaded with
                                      youtubedl.
        :param cookie_file:           A cookie file for YoutubeDL.
        :param proxy_url:             A proxy url for YoutubeDL.
        :param ydl_username:          Username that will be used to download the
                                      resources with youtube_dl.
        :param ydl_password:          Password of the related username, will be used
                                      to download the resources with youtube_dl.
        :param use_download_archive:  Record the video url to the download archive.
                                      This will download only videos not listed in
                                      the archive file. Record the IDs of all
                                      downloaded videos in it.
        :param ignore_existing_item:  Ignores the check for existing items on archive.org.
        :return:                      Set of videos basename that has been downloaded.
        """

        basenames: set[str] = set()
        for video_info in video_infos:

            basename: Optional[str] = self.ydl_progress_each(video_info)

            if basename is not None:
                basenames.add(basename)

        self.logger.debug(
            'Basenames obtained from url : %s'
            % basenames)

        return basenames

    def get_video_info(self, urls: list[str]) -> list[any]:
        video_infos: list[str] = []
        for url in urls:
            # with YoutubeDL(self.) as ydl:
            info_dict = self.ydl.extract_info(url)
            if info_dict.get('_type', 'video') == 'playlist':
                video_infos.extend(info_dict['entries'])
            else:
                video_infos.append(info_dict)
        return video_infos

    def ydl_progress_each(self, entry) -> Optional[str]:
        if not entry:
            self.logger.warning('Video "%s" is not available. Skipping.' % entry['url'])
            return None
        if self.ydl.in_download_archive(entry):
            return None
        if not self.check_if_ia_item_exists(entry):
            self.ydl.extract_info(entry['webpage_url'])
            return self.create_basename_from_ydl_video(entry)
        else:
            self.ydl.record_download_archive(entry)
            return None

    def check_if_ia_item_exists(self, info_dict) -> bool:
        itemname = get_itemname(info_dict)
        item = internetarchive.get_item(itemname)
        if item.exists and self.verbose:
            print("\n:: Item already exists. Not downloading.")
            print('Title: %s' % info_dict['title'])
            print('Video URL: %s\n' % info_dict['webpage_url'])
            return True
        return False

    def create_basename_from_ydl_video(self, info_dict) -> Union[str, set[str]]:
        """
        Create basenames from YoutubeDL vidéo info_dict.
        :param info_dict:  A ydl info_dict that will be used to create
                           the basenames.
        :return:           A set that contains basenames that created from
                           the `info_dict`.
        """

        info_type = info_dict.get('_type', 'video')
        if info_type == 'playlist':
            list = set()
            for entry in info_dict['entries']:
                list.add(self.create_basename_from_ydl_video(entry))
            return list

        self.logger.debug('Creating basenames from ydl info dict')

        filename = self.ydl.prepare_filename(info_dict)
        filename_without_ext = os.path.splitext(filename)[0]
        file_basename = re.sub(r'(\.f\d+)', '', filename_without_ext)
        return file_basename

    def ydl_progress_hook(self, d):
        if d['status'] == 'downloading' and self.verbose:
            if d.get('_total_bytes_str') is not None:
                msg_template = ('%(_percent_str)s of %(_total_bytes_str)s '
                                'at %(_speed_str)s ETA %(_eta_str)s')
            elif d.get('_total_bytes_estimate_str') is not None:
                msg_template = ('%(_percent_str)s of '
                                '~%(_total_bytes_estimate_str)s at '
                                '%(_speed_str)s ETA %(_eta_str)s')
            elif d.get('_downloaded_bytes_str') is not None:
                if d.get('_elapsed_str'):
                    msg_template = ('%(_downloaded_bytes_str)s at '
                                    '%(_speed_str)s (%(_elapsed_str)s)')
                else:
                    msg_template = ('%(_downloaded_bytes_str)s '
                                    'at %(_speed_str)s')
            else:
                msg_template = ('%(_percent_str)s % at '
                                '%(_speed_str)s ETA %(_eta_str)s')

            process_msg = '\r[download] ' + (msg_template % d) + '\033[K'
            sys.stdout.write(process_msg)
            sys.stdout.flush()

        if d['status'] == 'finished':
            msg = '\nDownloaded %s' % d['filename']

            self.logger.debug(d)
            self.logger.info(msg)
            if self.verbose:
                print(msg)

        if d['status'] == 'error':
            # TODO: Complete the error message
            msg = 'Error when downloading the video'

            self.logger.error(msg)
            if self.verbose:
                print(msg)
