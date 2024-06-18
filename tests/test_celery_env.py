
from tests.conftest import default_worker_container

import pytest


def test_setup_celery(default_worker_container):
    assert default_worker_container == "running"
        