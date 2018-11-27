from pathlib import Path as P
from collections import Iterable

from main import calc_md5_for_dir


def construct_test_files(base_dir, contents, suffix=None):
    P(base_dir).mkdir(parents=True, exist_ok=True)
    suffix = '' if suffix is None else '.%s' % suffix
    if not isinstance(contents, Iterable):
        contents = [contents]
    for content in contents:
        with open(P(base_dir) / (content + suffix), 'w') as f:
            f.write(content)


def test_calc_md5_for_dir():
    suffix = 'txt'
    construct_test_files('/tmp/a', ['123456', '123'], suffix=suffix)
    construct_test_files('/tmp/a/b', ['aaa'], suffix=suffix)
    assert calc_md5_for_dir('/tmp/a', suffix) == {'47bce5c74f589f4867dbd57e9ca9f808': '/tmp/a/b/aaa.txt',
                                                  'e10adc3949ba59abbe56e057f20f883e': '/tmp/a/123456.txt',
                                                  '202cb962ac59075b964b07152d234b70': '/tmp/a/123.txt'}
