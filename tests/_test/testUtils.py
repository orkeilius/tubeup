import glob
import os
import shutil
from typing import Union

from tubeup import __version__

current_path = os.path.dirname(os.path.realpath(__file__))

SCANNER = 'TubeUp Video Stream Mirroring Application {}'.format(__version__)


def get_testfile_path(name) -> Union[str, bytes]:
    return os.path.join(current_path, 'test_files', name)


def mocked_ydl_progress_hook(d) -> None:
    pass


def mock_upload_response_by_videobasename(m, ia_id, videobasename) -> None:
    files_to_upload = glob.glob(videobasename + '*')

    for file_path in files_to_upload:
        filename = os.path.basename(file_path)
        m.put('https://s3.us.archive.org/%s/%s' % (ia_id, filename),
              content=b'',
              headers={'content-type': 'text/plain'})


def copy_testfiles_to_tubeup_rootdir() -> None:
    # Copy testfiles to rootdir path of TubeUp.
    # This method was created because after the uploading done by
    # internetarchive library, it deletes the files that has been uploaded.
    testfiles_dir = os.path.join(current_path, 'test_files',
                                 'files_for_upload_and_download_tests')
    temp_dir = os.path.join(current_path, 'test_rootdir', 'downloads')

    os.makedirs(temp_dir, exist_ok=True)
    for filepath in os.listdir(testfiles_dir):
        shutil.copy(
            os.path.join(testfiles_dir, filepath),
            os.path.join(temp_dir,
                         filepath))

def get_testfile_path(name) -> Union[str, bytes]:
    current_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_path, 'test_files', name)

