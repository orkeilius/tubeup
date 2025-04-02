import glob
import json
import os
from logging import Logger, getLogger

import internetarchive
from internetarchive.config import parse_config_file

from tubeup.Helper.MetadataConverter import MetadataConverter
from tubeup.utils import EMPTY_ANNOTATION_FILE, check_is_file_empty, get_itemname


class IAUploader:

    def __init__(self, ia_config_path: str, verbose: bool = False) -> None:
        self.logger: Logger = getLogger(__name__)
        self.verbose: bool = verbose
        self.ia_config_path: str = ia_config_path

    def upload_ia(self, videobasename, custom_meta=None) -> tuple[str, dict]:
        """
        Upload video to archive.org.

        :param videobasename:  A video base name.
        :param custom_meta:    A custom meta, will be used by internetarchive
                               library when uploading to archive.org.
        :return:               A tuple containing item name and metadata used
                               when uploading to archive.org and whether the item
                               already exists.
        """
        json_metadata_filepath: str = videobasename + '.info.json'
        with open(json_metadata_filepath, 'r', encoding='utf-8') as f:
            vid_meta = json.load(f)

        # Exit if video download did not complete, don't upload .part files to IA
        for ext in ['*.part', '*.f302.*', '*.f302.*', '*.ytdl', '*.f251.*', '*.248.*', '*.f247.*', '*.temp']:
            if glob.glob(videobasename + ext):
                msg = 'Video download incomplete, please re-run or delete video stubs in downloads folder, exiting...'
                raise IOError(msg)

        item_name = get_itemname(vid_meta)
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

        # Upload all files with videobase name: e.g. video.mp3,
        # video.info.json, video.srt, etc.
        files_to_upload = glob.glob(videobasename + '*')

        # Upload the item to the Internet Archive
        item = internetarchive.get_item(item_name)

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
            raise ValueError(msg)

        item.upload(files_to_upload, metadata=metadata, retries=9000,
                    request_kwargs=dict(timeout=9000), delete=True,
                    verbose=self.verbose, access_key=s3_access_key,
                    secret_key=s3_secret_key)

        return item_name, metadata
