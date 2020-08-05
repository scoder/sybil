from py.path import local

from sybil import Sybil


class MockFile(object):
    def __init__(self, path, parent, sybil):
        self.path = path


class TestCollectFile(object):

    def test_filenames(self, tmp_path):
        pytest_collect_file = Sybil(parsers=[], filenames=['test.rst']).pytest(MockFile)
        path = (tmp_path / 'test.rst')
        path.write_text(u'')
        local_path = local(path)
        assert pytest_collect_file(None, local_path).path == local_path

    def test_fnmatch_pattern(self, tmp_path):
        pytest_collect_file = Sybil(parsers=[], pattern='**/*.rst').pytest(MockFile)
        path = (tmp_path / 'test.rst')
        path.write_text(u'')
        local_path = local(path)
        assert pytest_collect_file(None, local_path).path == local_path
