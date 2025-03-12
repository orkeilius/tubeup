import json

from yt_dlp import YoutubeDL

from tests._test.testUtils import get_testfile_path


# helper from yt_dlp
# https://github.com/yt-dlp/yt-dlp/blob/05c8023a27dd37c49163c0498bf98e3e3c1cb4b9/test/helper.py#L61
class FakeYDL(YoutubeDL):
    def __init__(self, params, override=None) -> None:
        # Different instances of the downloader can't share the same dictionary
        # some test set the "sublang" parameter, which would break the md5 checks.
        super().__init__(params, auto_init=False)
        self.result = []
        self.extract_info_data = json.load(open(get_testfile_path("FakeDlp_mock/extract_info_data.json")))

    def to_screen(self, s, *args, **kwargs) -> None:
        print(s)

    def trouble(self, s, *args, **kwargs) -> None:
        raise Exception(s)

    def download(self, x) -> None:
        self.result.append(x)

    def extract_info(self, url, download=True) -> dict:
        print("mocked extract info of : ", url)
        return self.extract_info_data[url]
