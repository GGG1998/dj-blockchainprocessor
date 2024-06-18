## Nice to read
https://www.vintasoftware.com/blog/celery-overview-archtecture-and-how-it-works
https://www.vintasoftware.com/blog/celery-wild-tips-and-tricks-run-async-tasks-real-world
[Celery and asyncio - stackoverflow struggling](https://stackoverflow.com/a/43325237/5872362)
[Celery and asyncio - response on it gevent](https://docs.celeryq.dev/en/stable/userguide/concurrency/index.html)
[Celery and gevent - example](https://github.com/celery/celery/blob/main/examples/eventlet/webcrawler.py)
[Celery asyncio open debate](https://github.com/celery/celery/issues/6552)
https://adamj.eu/tech/2020/02/03/common-celery-issues-on-django-projects/

**Summary**: Celery can't deal with asyncio, even though we wrap our code AsyncToSync then it doesn't get the intended benefits of using async. There is no simple way to transfer a socket from one process to an other. Better is write independent microservice