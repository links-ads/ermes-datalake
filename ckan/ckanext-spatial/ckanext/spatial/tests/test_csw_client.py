import time
from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError
import os

import pytest

from ckan.plugins.toolkit import config

from ckan.model import engine_is_sqlite


# copied from ckan/tests/__init__ to save importing it and therefore
# setting up Pylons.
class CkanServerCase(object):
    @staticmethod
    def _system(cmd):
        import subprocess

        (status, output) = subprocess.getstatusoutput(cmd)
        if status:
            raise Exception("Couldn't execute cmd: %s: %s" % (cmd, output))

    @classmethod
    def _paster(cls, cmd, config_path_rel):
        config_path = os.path.join(config["here"], config_path_rel)
        cls._system("paster --plugin ckan %s --config=%s" % (cmd, config_path))

    @staticmethod
    def _start_ckan_server(config_file=None):
        if not config_file:
            config_file = config["__file__"]
        config_path = config_file
        import subprocess

        process = subprocess.Popen(["paster", "serve", config_path])
        return process

    @staticmethod
    def _wait_for_url(url="http://127.0.0.1:5000/", timeout=15):
        for i in range(int(timeout) * 100):
            try:
                urlopen(url)
            except URLError:
                time.sleep(0.01)
            else:
                break

    @staticmethod
    def _stop_ckan_server(process):
        pid = process.pid
        pid = int(pid)
        if os.system("kill -9 %d" % pid):
            raise Exception("Can't kill foreign CKAN instance (pid: %d)." % pid)


class CkanProcess(CkanServerCase):
    @classmethod
    def setup_class(cls):
        if engine_is_sqlite():
            return pytest.skip("Non-memory database needed for this test")

        cls.pid = cls._start_ckan_server()
        ## Don't need to init database, since it is same database as this process uses
        cls._wait_for_url()

    @classmethod
    def teardown_class(cls):
        cls._stop_ckan_server(cls.pid)
