import shutil
import os
from pathlib import Path as P
from collections import Iterable

import pytest

from main import calc_file_md5_in_dir, get_file_paths, get_file_md5sum


def construct_test_files(base_dir, contents, suffix=None):
    P(base_dir).mkdir(parents=True, exist_ok=True)
    suffix = '' if suffix is None else '.%s' % suffix
    if not isinstance(contents, Iterable):
        contents = [contents]
    for content in contents:
        with open(P(base_dir) / (content + suffix), 'w') as f:
            f.write(content)


@pytest.fixture(scope='module')
def files_in_tmp():
    construct_test_files('/tmp/a', ['123456', '123'], suffix='txt')
    construct_test_files('/tmp/a', ['123456', '123'], suffix='xml')
    construct_test_files('/tmp/a/b', ['aaa'], suffix='txt')
    yield
    shutil.rmtree('/tmp/a')


@pytest.fixture(scope='module')
def files_in_cur_folder():
    construct_test_files('test_folder_a', ['123456', '123'], suffix='txt')
    construct_test_files('test_folder_a', ['123456', '123'], suffix='xml')
    construct_test_files('test_folder_a/test_folder_b', ['aaa'], suffix='txt')
    yield
    shutil.rmtree('test_folder_a')


@pytest.fixture(scope='module')
def file_and_symlink():
    construct_test_files('/tmp/sym/a', ['123456'], suffix='txt')
    os.symlink('/tmp/sym/a', '/tmp/sym/b')
    yield
    shutil.rmtree('/tmp/sym')


def test_calc_md5_for_dir(files_in_tmp):
    assert calc_file_md5_in_dir('/tmp/a', 'txt') == {'47bce5c74f589f4867dbd57e9ca9f808': '/tmp/a/b/aaa.txt',
                                                 'e10adc3949ba59abbe56e057f20f883e': '/tmp/a/123456.txt',
                                                 '202cb962ac59075b964b07152d234b70': '/tmp/a/123.txt'}


def test_get_file_paths(files_in_tmp):
    assert set(get_file_paths('/tmp/a', 'txt')) == {'/tmp/a/123456.txt', '/tmp/a/123.txt', '/tmp/a/b/aaa.txt'}


def test_get_file_paths_given_relpath_root_dir(files_in_cur_folder):
    assert set(get_file_paths('test_folder_a', 'txt')) == {'test_folder_a/123456.txt', 'test_folder_a/123.txt',
                                                           'test_folder_a/test_folder_b/aaa.txt'}
    assert set(get_file_paths('./test_folder_a', 'txt')) == {'./test_folder_a/123456.txt', './test_folder_a/123.txt',
                                                             './test_folder_a/test_folder_b/aaa.txt'}


def test_get_file_md5sum(files_in_tmp):
    assert get_file_md5sum('/tmp/a/b/aaa.txt') == '47bce5c74f589f4867dbd57e9ca9f808'


def test_get_file_md5sum_relpath(files_in_cur_folder):
    assert get_file_md5sum('test_folder_a/test_folder_b/aaa.txt') == '47bce5c74f589f4867dbd57e9ca9f808'
    assert get_file_md5sum('./test_folder_a/test_folder_b/aaa.txt') == '47bce5c74f589f4867dbd57e9ca9f808'


def test_calc_md5_for_symlinks(file_and_symlink):
    calculated_md5 = calc_file_md5_in_dir('/tmp/sym', 'txt', follow_symlinks=True)
    assert calculated_md5 == {'e10adc3949ba59abbe56e057f20f883e': '/tmp/sym/b/123456.txt'}
