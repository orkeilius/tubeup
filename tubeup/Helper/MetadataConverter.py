from datetime import datetime
import time
import re
from urllib.parse import urlparse

from tubeup import __version__


class MetadataConverter(object):

    @staticmethod
    def create_archive_org_metadata_from_youtubedl_meta(vid_meta) -> dict:
        """
        Create archive.org metadata from youtubedl-generated metadata.

        :param vid_meta: A dict containing youtubedl-generated metadata.
        :return:         A dict containing metadata to be used by
                         internetarchive library.
        """

        videourl = vid_meta['webpage_url']
        creator = MetadataConverter.determine_creator(vid_meta)
        collection = MetadataConverter.determine_collection_type(videourl)
        mediatype = ('audio' if collection == 'opensource_audio' else 'movies')
        title = '%s' % (vid_meta['title'])
        upload_date = MetadataConverter.determine_upload_date(vid_meta)
        upload_year = upload_date[:4]
        subject = MetadataConverter.determine_subject(vid_meta)
        description = MetadataConverter.determine_description(vid_meta)
        licenseurl = MetadataConverter.determine_licenseurl(vid_meta)

        metadata = dict(
            originalurl=videourl,
            mediatype=mediatype,
            creator=creator,
            collection=collection,
            title=title,
            description=description,
            date=upload_date,
            year=upload_year,
            subject=subject,
            licenseurl=licenseurl,

            # Set 'scanner' metadata pair to allow tracking of TubeUp
            # powered uploads, per request from archive.org
            scanner='TubeUp Video Stream Mirroring Application {}'.format(__version__))

        # add channel url if it exists
        if 'uploader_url' in vid_meta:
            metadata["channel"] = vid_meta["uploader_url"]
        elif 'channel_url' in vid_meta:
            metadata["channel"] = vid_meta["channel_url"]

        return metadata

    @staticmethod
    def determine_creator(vid_meta: dict) -> str:
        """
        Determine creator for an url

        :param vid_meta:
        :return: creator name or 'tubeup.py' if not found
        """
        # Some video services don't tell you the uploader,
        # use our program's name in that case.
        try:
            if vid_meta['extractor_key'] == 'TwitchClips' and 'creator' in vid_meta and vid_meta['creator']:
                return vid_meta['creator']
            elif 'uploader' in vid_meta and vid_meta['uploader']:
                return vid_meta['uploader']
            elif 'uploader_url' in vid_meta and vid_meta['uploader_url']:
                return vid_meta['uploader_url']
        except TypeError:  # apparently uploader is null as well
            pass

        return 'tubeup.py'

    @staticmethod
    def determine_collection_type(url: str) -> str:
        """
        Determine collection type for an url.

        :param url:  URL that the collection type will be determined.
        :return:     String, name of a collection.
        """
        if urlparse(url).netloc == 'soundcloud.com':
            return 'opensource_audio'
        return 'opensource_movies'

    @staticmethod
    def determine_description(vid_meta: dict) -> str:
        """
        Determine description for an url

        :param vid_meta:
        :return: description text or empty string if not found
        """
        # if there is no description don't upload the empty .description file
        description_text = vid_meta.get('description', '')
        if description_text is None:
            description_text = ''
        # archive.org does not display raw newlines
        description = re.sub('\r?\n', '<br>', description_text)
        return description

    @staticmethod
    def determine_upload_date(vid_meta: dict) -> str:
        """
        Determine upload date for an url

        :param vid_meta:
        :return: upload date or current date if not found
        """
        try:  # some videos don't give an upload date
            d = datetime.strptime(vid_meta['upload_date'], '%Y%m%d')
            upload_date = d.isoformat().split('T')[0]
        except (KeyError, TypeError):
            # Use current date and time as default values
            upload_date = time.strftime("%Y-%m-%d")
        return upload_date

    @staticmethod
    def determine_licenseurl(vid_meta) -> str:
        """
        Determine licenseurl for an url

        :param vid_meta:
        :return: licenseurl or empty string if not found
        """
        licenses = {
            "Creative Commons Attribution license (reuse allowed)": "https://creativecommons.org/licenses/by/3.0/",
            "Attribution-NonCommercial-ShareAlike": "https://creativecommons.org/licenses/by-nc-sa/2.0/",
            "Attribution-NonCommercial": "https://creativecommons.org/licenses/by-nc/2.0/",
            "Attribution-NonCommercial-NoDerivs": "https://creativecommons.org/licenses/by-nc-nd/2.0/",
            "Attribution": "https://creativecommons.org/licenses/by/2.0/",
            "Attribution-ShareAlike": "https://creativecommons.org/licenses/by-sa/2.0/",
            "Attribution-NoDerivs": "https://creativecommons.org/licenses/by-nd/2.0/"
        }

        if 'license' in vid_meta and vid_meta['license']:
            return licenses.get(vid_meta['license'])

        return ''

    @staticmethod
    def determine_subject(vid_meta: dict) -> str:
        """
        Determine subject for an url

        :param vid_meta:
        :return: subject text or empty string if not found
        """
        # load up tags into an IA compatible semicolon-separated string
        # example: Youtube;video;
        tags_string = '%s;video;' % vid_meta['extractor_key']

        if 'categories' in vid_meta:
            # add categories as tags as well, if they exist
            try:
                for category in vid_meta['categories']:
                    tags_string += '%s;' % category
            except Exception:
                print("No categories found.")

        if 'tags' in vid_meta:  # some video services don't have tags
            try:
                if 'tags' in vid_meta is None:
                    tags_string += '%s;' % vid_meta['id']
                    tags_string += '%s;' % 'video'
                else:
                    for tag in vid_meta['tags']:
                        tags_string += '%s;' % tag
            except Exception:
                print("Unable to process tags successfully.")

        # IA's subject field has a 255 bytes length limit, so we need to truncate tags_string
        while len(tags_string.encode('utf-8')) > 255:
            tags_list = tags_string.split(';')
            tags_list.pop()
            tags_string = ';'.join(tags_list)

        return tags_string
