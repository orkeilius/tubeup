import os
import shutil
import unittest

from tubeup.Helper.DirPath import DirPath, DOWNLOAD_DIR_NAME

current_path = os.path.dirname(os.path.realpath(__file__))


class DirPathTest(unittest.TestCase):

    def test_set_dir_path(self):
        root_path = os.path.join(
            current_path, '.directory_for_tubeup_set_dir_path_test')
        dir_paths_dict = dict(root=root_path,
                              downloads=os.path.join(root_path,
                                                     DOWNLOAD_DIR_NAME))

        dir_path = DirPath(root_path)
        self.assertEqual(dir_path.downloads, dir_paths_dict["downloads"])
        self.assertEqual(dir_path.root, dir_paths_dict["root"])

        # Make sure that other directories are created as well
        self.assertTrue(os.path.exists(dir_paths_dict['downloads']))

        # Clean the test directory
        shutil.rmtree(root_path, ignore_errors=True)
