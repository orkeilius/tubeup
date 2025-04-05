import os
import sys
import re
import glob
import time
import json
import logging
import internetarchive

from internetarchive.config import parse_config_file
from yt_dlp import YoutubeDL

from tubeup.Helper.MetadataConverter import MetadataConverter

from .utils import (get_itemname, check_is_file_empty,
                    EMPTY_ANNOTATION_FILE)
from logging import getLogger

from tubeup.config.Ydl_options_factory import *


DOWNLOAD_DIR_NAME = 'downloads'


class TubeUp(object):

    def __init__(self,
                 verbose=False,
                 dir_path='~/.tubeup',
                 ia_config_path=None,
                 output_template=None):
        """
        `tubeup` is a tool to archive YouTube by downloading the videos and
        uploading it back to the archive.org.

        :param verbose:         A boolean, True means all loggings will be
                                printed out to stdout.
        :param dir_path:        A path to directory that will be used for
                                saving the downloaded resources. Default to
                               '~/.tubeup'.
        :param ia_config_path:  Path to an internetarchive config file, will
                                be used in uploading the file.
        :param output_template: A template string that will be used to
                                generate the output filenames.
        """
        self.dir_path :DirPath = DirPath(dir_path)
        self.verbose = verbose
        self.ia_config_path = ia_config_path
        self.logger = getLogger(__name__)
        if output_template is None:
            self.output_template = '%(id)s.%(ext)s'
        else:
            self.output_template = output_template

        # Just print errors in quiet mode
        if not self.verbose:
            self.logger.setLevel(logging.ERROR)




    def get_resource_basenames(self, urls,
                               cookie_file=None, proxy_url=None,
                               ydl_username=None, ydl_password=None,
                               use_download_archive=False,
                               ignore_existing_item=False):
        """
        Get resource basenames from an url.

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
        downloaded_files_basename = set()

        def check_if_ia_item_exists(infodict):
            itemname = get_itemname(infodict)
            item = internetarchive.get_item(itemname)
            if item.exists and self.verbose:
                print("\n:: Item already exists. Not downloading.")
                print('Title: %s' % infodict['title'])
                print('Video URL: %s\n' % infodict['webpage_url'])
                return True
            return False

        def ydl_progress_each(entry):
            if not entry:
                self.logger.warning('Video "%s" is not available. Skipping.' % url)
                return
            if ydl.in_download_archive(entry):
                return
            if not check_if_ia_item_exists(entry):
                ydl.extract_info(entry['webpage_url'])
                downloaded_files_basename.update(self.create_basenames_from_ydl_info_dict(ydl, entry))
            else:
                ydl.record_download_archive(entry)

        def ydl_progress_hook(d):
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

        ydl_opts = Ydl_options_factory.generate_ydl_options(self.dir_path,self.logger,ydl_progress_hook,
                                             cookie_file, proxy_url,
                                             ydl_username, ydl_password,
                                             use_download_archive)

        with YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                if not ignore_existing_item:
                    # Get the info dict of the url
                    info_dict = ydl.extract_info(url, download=False)

                    if info_dict.get('_type', 'video') == 'playlist':
                        for entry in info_dict['entries']:
                            ydl_progress_each(entry)
                    else:
                        ydl_progress_each(info_dict)
                else:
                    info_dict = ydl.extract_info(url)
                    downloaded_files_basename.update(self.create_basenames_from_ydl_info_dict(ydl, info_dict))

        self.logger.debug(
            'Basenames obtained from url (%s): %s'
            % (url, downloaded_files_basename))

        return downloaded_files_basename

    def create_basenames_from_ydl_info_dict(self, ydl, info_dict):
        """
        Create basenames from YoutubeDL info_dict.

        :param ydl:        A `youtube_dl.YoutubeDL` instance.
        :param info_dict:  A ydl info_dict that will be used to create
                           the basenames.
        :return:           A set that contains basenames that created from
                           the `info_dict`.
        """
        info_type = info_dict.get('_type', 'video')
        self.logger.debug('Creating basenames from ydl info dict with type %s'
                          % info_type)

        filenames = set()

        if info_type == 'playlist':
            # Iterate and get the filenames through the playlist
            for video in info_dict['entries']:
                filenames.add(ydl.prepare_filename(video))
        else:
            filenames.add(ydl.prepare_filename(info_dict))

        basenames = set()

        for filename in filenames:
            filename_without_ext = os.path.splitext(filename)[0]
            file_basename = re.sub(r'(\.f\d+)', '', filename_without_ext)
            basenames.add(file_basename)

        return basenames

    def generate_ydl_options(self,
                             ydl_progress_hook,
                             cookie_file=None,
                             proxy_url=None,
                             ydl_username=None,
                             ydl_password=None,
                             use_download_archive=False,
                             ydl_output_template=None):
        """
        Generate a dictionary that contains options that will be used
        by yt-dlp.

        :param ydl_progress_hook:     A function that will be called during the
                                      download process by youtube_dl.
        :param proxy_url:             A proxy url for YoutubeDL.
        :param ydl_username:          Username that will be used to download the
                                      resources with youtube_dl.
        :param ydl_password:          Password of the related username, will be
                                      used to download the resources with
                                      youtube_dl.
        :param use_download_archive:  Record the video url to the download archive.
                                      This will download only videos not listed in
                                      the archive file. Record the IDs of all
                                      downloaded videos in it.
        :return:                      A dictionary that contains options that will
                                      be used by youtube_dl.
        """
        ydl_opts = {
            'outtmpl': os.path.join(self.dir_path.downloads,
                                    self.output_template),
            'restrictfilenames': True,
            'quiet': not self.verbose,
            'verbose': self.verbose,
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
            'ignoreerrors': True,  # Geo-blocked,
                                   # copyrighted/private/deleted
                                   # will be printed to STDOUT and channel
                                   # ripping will  continue uninterupted,
                                   # use with verbose off
            'fixup': 'warn',  # Slightly more verbosity for debugging
                              # problems
            'nooverwrites': True,  # Don't touch what's already been
                                   # downloaded speeds things
            'consoletitle': True,   # Download percentage in console title
            'prefer_ffmpeg': True,  # `ffmpeg` is better than `avconv`,
                                    # let's prefer it's use
            # Warns on out of date youtube-dl script, helps debugging for
            # youtube-dl devs
            'call_home': False,
            'logger': self.logger,
            'progress_hooks': [ydl_progress_hook]
        }

        if cookie_file is not None:
            ydl_opts['cookiefile'] = cookie_file

        if proxy_url is not None:
            ydl_opts['proxy'] = proxy_url

        if ydl_username is not None:
            ydl_opts['username'] = ydl_username

        if ydl_password is not None:
            ydl_opts['password'] = ydl_password

        if use_download_archive:
            ydl_opts['download_archive'] = os.path.join(self.dir_path.root,
                                                        '.ytdlarchive')

        return ydl_opts

    def upload_ia(self, videobasename, custom_meta=None):
        """
        Upload video to archive.org.

        :param videobasename:  A video base name.
        :param custom_meta:    A custom meta, will be used by internetarchive
                               library when uploading to archive.org.
        :return:               A tuple containing item name and metadata used
                               when uploading to archive.org and whether the item
                               already exists.
        """
        json_metadata_filepath = videobasename + '.info.json'
        with open(json_metadata_filepath, 'r', encoding='utf-8') as f:
            vid_meta = json.load(f)

        # Exit if video download did not complete, don't upload .part files to IA
        for ext in ['*.part', '*.f303.*', '*.f302.*', '*.ytdl', '*.f251.*', '*.248.*', '*.f247.*', '*.temp']:
            if glob.glob(videobasename + ext):
                msg = 'Video download incomplete, please re-run or delete video stubs in downloads folder, exiting...'
                raise Exception(msg)

        itemname = get_itemname(vid_meta)
        metadata = MetadataConverter.create_archive_org_metadata_from_youtubedl_meta(vid_meta)

        # Delete empty description file
        description_file_path = videobasename + '.description'
        if (os.path.exists(description_file_path) and
            (('description' in vid_meta and
             vid_meta['description'] == '') or
                check_is_file_empty(description_file_path))):
            os.remove(description_file_path)

        # Delete empty annotations.xml file so it isn't uploaded
        annotations_file_path = videobasename + '.annotations.xml'
        if (os.path.exists(annotations_file_path) and
            (('annotations' in vid_meta and
             vid_meta['annotations'] in {'', EMPTY_ANNOTATION_FILE}) or
                check_is_file_empty(annotations_file_path))):
            os.remove(annotations_file_path)

        # Upload all files with videobase name: e.g. video.mp4,
        # video.info.json, video.srt, etc.
        files_to_upload = glob.glob(videobasename + '*')

        # Upload the item to the Internet Archive
        item = internetarchive.get_item(itemname)

        if custom_meta:
            metadata.update(custom_meta)

        # Parse internetarchive configuration file.
        parsed_ia_s3_config = parse_config_file(self.ia_config_path)[2]['s3']
        s3_access_key = parsed_ia_s3_config['access']
        s3_secret_key = parsed_ia_s3_config['secret']

        if None in {s3_access_key, s3_secret_key}:
            msg = ('`internetarchive` configuration file is not configured'
                   ' properly.')

            self.logger.error(msg)
            if self.verbose:
                print(msg)
            raise Exception(msg)

        item.upload(files_to_upload, metadata=metadata, retries=9001,
                    request_kwargs=dict(timeout=(9001, 9001)), delete=True,
                    verbose=self.verbose, access_key=s3_access_key,
                    secret_key=s3_secret_key)

        return itemname, metadata

    def archive_urls(self, urls, custom_meta=None,
                     cookie_file=None, proxy=None,
                     ydl_username=None, ydl_password=None,
                     use_download_archive=False,
                     ignore_existing_item=False):
        """
        Download and upload videos from youtube_dl supported sites to
        archive.org

        :param urls:                  List of url that will be downloaded and uploaded
                                      to archive.org
        :param custom_meta:           A custom metadata that will be used when
                                      uploading the file with archive.org.
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
        :return:                      Tuple containing identifier and metadata of the
                                      file that has been uploaded to archive.org.
        """
        downloaded_file_basenames = self.get_resource_basenames(
            urls, cookie_file, proxy, ydl_username, ydl_password, use_download_archive,
            ignore_existing_item)
        for basename in downloaded_file_basenames:
            identifier, meta = self.upload_ia(basename, custom_meta)
            yield identifier, meta
