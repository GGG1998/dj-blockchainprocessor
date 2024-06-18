import celery
import os


from pytest_docker_tools import build, container, fxtr
from pytest_celery import CeleryWorkerContainer, defaults

from typing import Any

class DjangoWorkerContainer(CeleryWorkerContainer):
    @property
    def client(self) -> Any:
        return self

    @classmethod
    def version(cls) -> str:
        return celery.__version__

    @classmethod
    def log_level(cls) -> str:
        return "INFO"

    @classmethod
    def worker_name(cls) -> str:
        return "django_tests_worker"

    @classmethod
    def worker_queue(cls) -> str:
        return "celery"

worker_image = build(
    path=".",
    dockerfile="Dockerfile",
    tag="django_celery_test_worker",
    buildargs=DjangoWorkerContainer.buildargs(),
)

default_worker_container = container(
    image="{worker_image.id}",
    ports=fxtr("default_worker_ports"),
    environment=fxtr("default_worker_env"),
    network="{default_pytest_celery_network.name}",
    volumes={
        "{default_worker_volume.name}": defaults.DEFAULT_WORKER_VOLUME,
        os.path.abspath(os.getcwd()): {
            "bind": "/src",
            "mode": "rw",
        },
    },
    wrapper_class=DjangoWorkerContainer,
    timeout=defaults.DEFAULT_WORKER_CONTAINER_TIMEOUT,
)