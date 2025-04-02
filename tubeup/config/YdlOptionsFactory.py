from logging import Logger
import os

from tubeup.Helper.DirPath import DirPath


class YdlOptionsFactory:

    @staticmethod
    def generate_ydl_options(dir_path: DirPath,
                             logger: Logger,
                             ydl_progress_hook: callable,
                             cookie_file: str = None,
                             proxy_url: str = None,
                             ydl_username: str = None,
                             ydl_password: str = None,
                             use_download_archive: bool = False,
                             ydl_output_template: str = '%(id)s.%(ext)s',
                             verbose: bool = False) -> dict:
        """
        Generate a dictionary that contains options that will be used
        by yt-dlp.

        :param dir_path:              The dictionary that contains tubeUp data

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
            'outtmpl': os.path.join(dir_path.downloads,
                                    ydl_output_template),
            'restrictfilenames': True,
            'quiet': not verbose,
            'verbose': verbose,
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
            'fixup': 'detect_or_warn',  # Slightly more verbosity for debugging
                                        # problems
            'nooverwrites': True,  # Don't touch what's already been
                                   # downloaded speeds things
            'consoletitle': True,   # Download percentage in console title
            'prefer_ffmpeg': True,  # `ffmpeg` is better than `avconv`,
                                    # let's prefer it's use
            # Warns on out of date youtube-dl script, helps debugging for
            # youtube-dl devs
            'call_home': False,
            'logger': logger,
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
            ydl_opts['download_archive'] = os.path.join(dir_path.root,
                                                        '.ytdlarchive')

        return ydl_opts
