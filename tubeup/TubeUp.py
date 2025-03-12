import logging

from tubeup.Helper.DirPath import DirPath

from tubeup.Component.IAUploader import IAUploader
from logging import getLogger

from tubeup.Component.YtdlpWrapper import YtdlpWrapper


class TubeUp(object):

    def __init__(self,
                 verbose=False,
                 dir_path='~/.tubeup',
                 ia_config_path=None,
                 output_template='%(id)s.%(ext)s'):
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
        self.dir_path: DirPath = DirPath(dir_path)
        self.verbose = verbose
        self.ia_config_path = ia_config_path
        self.logger: logging.Logger = getLogger(__name__)
        self.output_template = output_template

        # Just print errors in quiet mode
        if not self.verbose:
            self.logger.setLevel(logging.ERROR)

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
        ydp = YtdlpWrapper(self.dir_path, cookie_file, proxy, ydl_username, ydl_password, use_download_archive,
                           ignore_existing_item, self.verbose)
        downloaded_file_basenames = ydp.download(ydp.get_video_info(urls))
        uploader = IAUploader(self.ia_config_path, self.verbose)
        for basename in downloaded_file_basenames:
            identifier, meta = uploader.upload_ia(basename, custom_meta)
            yield identifier, meta
