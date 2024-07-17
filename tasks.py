from robocorp.tasks import task

from libraries.extractor import Extractor

@task
def news():
    extract = Extractor()
    extract.run()


