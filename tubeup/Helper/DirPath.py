import os

DOWNLOAD_DIR_NAME = 'downloads'


class DirPath:

    def __init__(self, dir_path: str) -> None:
        """
        Set a directory to be the saving directory for resources that have
        been downloaded.

        :param dir_path:  Path to a directory that will be used to save the
                          videos, if it not created yet, the directory
                          will be created.
        """
        extended_usr_dir_path = os.path.expanduser(dir_path)

        # Create the directories.
        os.makedirs(
            os.path.join(extended_usr_dir_path, DOWNLOAD_DIR_NAME),
            exist_ok=True)

        self._root = extended_usr_dir_path
        self._downloads = os.path.join(extended_usr_dir_path, DOWNLOAD_DIR_NAME)

    @property
    def root(self) -> str:
        return self._root

    @property
    def downloads(self) -> str:
        return self._downloads
