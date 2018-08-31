from mock import patch
import pytest


pytest_plugins = "pytester"


@pytest.fixture
def conftest(testdir):
    testdir.makeconftest(
        """
        import pytest
        from nameko.web.handlers import http

        @pytest.fixture(autouse=True)
        def service(container_factory, web_config):

            class BadRequest(Exception):
                pass

            class ServerError(Exception):
                pass

            class Service:
                name = "service"

                @http("GET", "/resource", expected_exceptions=BadRequest)
                def resource(self, request):
                    param = request.args.get('param')
                    if param == "good":
                        return 200, "OK"
                    if param == "bad":
                        raise BadRequest()
                    else:
                        raise ServerError()

            container = container_factory(Service, web_config)
            container.start()
        """
    )


@pytest.fixture
def patch_pdb():
    with patch('nameko_worker_postmortem.pdb') as patched:
        yield patched


def test_no_exception(testdir, conftest, patch_pdb):

    testdir.makepyfile("""
        def test_no_exception(web_session):
            res = web_session.get("/resource?param=good")
            assert res.status_code == 200
    """)
    result = testdir.runpytest()
    assert result.ret == 0

    assert not patch_pdb.post_mortem.called


def test_expected_exception(testdir, conftest, patch_pdb):

    testdir.makepyfile("""
        def test_expected_exception(web_session):
            res = web_session.get("/resource?param=bad")
            assert res.status_code == 400
    """)
    result = testdir.runpytest()
    assert result.ret == 0

    assert not patch_pdb.post_mortem.called


def test_unexpected_exception_plugin_disabled(testdir, conftest, patch_pdb):

    testdir.makepyfile("""
        def test_expected_exception(web_session):
            res = web_session.get("/resource?param=verybad")
            assert res.status_code == 500
    """)
    result = testdir.runpytest()
    assert result.ret == 0

    assert not patch_pdb.post_mortem.called


def test_unexpected_exception_plugin_enabled(testdir, conftest, patch_pdb):

    testdir.makepyfile("""
        def test_expected_exception(web_session):
            res = web_session.get("/resource?param=verybad")
            assert res.status_code == 500
    """)
    result = testdir.runpytest("-s", "--worker-postmortem")
    assert result.ret == 0

    assert patch_pdb.post_mortem.called


# manual testing:
# def test_bare_unexpected_exception(web_session, container_factory, web_config):

#     from nameko.web.handlers import http

#     class BadRequest(Exception):
#         pass

#     class ServerError(Exception):
#         pass

#     class Service:
#         name = "service"

#         @http("GET", "/resource", expected_exceptions=BadRequest)
#         def resource(self, request):
#             param = request.args.get('param')
#             if param == "good":
#                 return 200, "OK"
#             if param == "bad":
#                 raise BadRequest()
#             else:
#                 raise ServerError()

#     container = container_factory(Service, web_config)
#     container.start()

#     res = web_session.get("/resource?param=verybad")
#     assert res.status_code == 500
