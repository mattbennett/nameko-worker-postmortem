import pytest

import pdb
from mock import patch
from nameko.containers import ServiceContainer


def pytest_addoption(parser):

    parser.addoption(
        "--worker-postmortem", "--worker-pdb",
        action="store_true",
        dest="worker_postmortem",
        default=False,
        help="Drop into PDB post mortem if a Nameko worker throws an unexpected exception",
    )


@pytest.yield_fixture(autouse=True)
def pdb_worker_exceptions(request):

    unpatched = ServiceContainer._worker_result

    def attach_pdb(self, worker_ctx, result, exc_info):
        if exc_info:
            exc = exc_info[1]
            if not isinstance(exc, worker_ctx.entrypoint.expected_exceptions):
                pdb.post_mortem(exc_info[2])
        return unpatched(self, worker_ctx, result, exc_info)

    if request.config.option.worker_postmortem:
        with patch.object(ServiceContainer, "_worker_result", new=attach_pdb):
            yield
    else:
        yield
