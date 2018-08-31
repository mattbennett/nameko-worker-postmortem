# nameko-worker-postmortem

Have you ever been frustrated with the behaviour of a Nameko service in pytest using the ``--pdb`` flag?

If your Nameko service throws a worker exception, ``--pdb`` won't interrupt with a breakpoint until the exception is serialised back to the caller of the entrypoint.

`nameko-worker-postmortem` is a pytest plugin that inserts the tracepoint earlier, so you can see a more useful stack trace.

### Example

Here's an example test that will fail:

```python
# test.py

from nameko.web.handlers import http

class BadRequest(Exception):
    pass

class Service:
    name = "service"

    @http("GET", "/resource")
    def resource(self, request):
        param = request.args.get('param')
        if param == "good":
            return 200, "OK"
        raise BadRequest()


def test_service(container_factory, web_config, web_session):
    container = container_factory(Service, web_config)
    container.start()

    res = web_session.get('/resource?param=bad')
    assert res.status_code == 200
```

#### With `--pdb`


Using the `--pdb` flag, the breakpoint is set where the assertion fails, which isn't very helpful if you want to see the exception that the worker raised instead:

```pycon
$ py.test test.py
============================= test session starts ==============================
platform darwin -- Python 3.4.6, pytest-3.7.4, py-1.6.0, pluggy-0.7.1
rootdir: /private/tmp, inifile:
plugins: nameko-2.11.0, nameko-worker-postmortem-0.0.1
collected 1 item

test.py F
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> captured log >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
containers.py              399 ERROR    error handling worker <WorkerContext [service.resource] at 0x1104a77f0>:
Traceback (most recent call last):
  File "/Users/mattbennett/.virtualenvs/tmp-302905cac73c0a2/lib/python3.4/site-packages/nameko/containers.py", line 391, in _run_worker
    result = method(*worker_ctx.args, **worker_ctx.kwargs)
  File "/private/tmp/test.py", line 14, in resource
    raise BadRequest()
test.BadRequest
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> traceback >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

container_factory = <function container_factory.<locals>.make_container at 0x11022f620>
web_config = {'WEB_SERVER_ADDRESS': '127.0.0.1:55934'}
web_session = <nameko.testing.pytest.web_session.<locals>.WebSession object at 0x11047ac18>

    def test_service(container_factory, web_config, web_session):
        container = container_factory(Service, web_config)
        container.start()

        res = web_session.get('/resource?param=bad')
>       assert res.status_code == 200
E       assert 500 == 200
E        +  where 500 = <Response [500]>.status_code

test.py:22: AssertionError
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> entering PDB >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
[11] > /private/tmp/test.py(22)test_service()
-> assert res.status_code == 200
   6 frames hidden (try 'help hidden_frames')
> /private/tmp/test.py(22)

  17     def test_service(container_factory, web_config, web_session):
  18         container = container_factory(Service, web_config)
  19         container.start()
  20
  21         res = web_session.get('/resource?param=bad')
  22  ->     assert res.status_code == 200
```

#### With `--worker-postmortem`

Replacing `--pdb` with `--worker-postmortem` (or `--worker-pdb`) the breakpoint is inserted at where the worker exception is raised instead.

Note that `-s` must also be passed to disable output capturing.

```
$ py.test test.py --worker-postmortem -s
============================= test session starts ==============================
platform darwin -- Python 3.4.6, pytest-3.7.4, py-1.6.0, pluggy-0.7.1
rootdir: /private/tmp, inifile:
plugins: nameko-2.11.0, nameko-worker-postmortem-0.0.1
collected 1 item

test.py [1] > /private/tmp/test.py(14)resource()
-> raise BadRequest()
> /private/tmp/test.py(14)

   9         @http("GET", "/resource")
  10         def resource(self, request):
  11             param = request.args.get('param')
  12             if param == "good":
  13                 return 200, "OK"
  14  ->         raise BadRequest()
(Pdb++)
```

### TODO

* Fix coverage collection
* Add pre-commit hooks
* Automatically disable capturing so you don't have to specify `-s` every time
* Attempt to make navigation `up` and `down` the stack trace work as they would with a `pdb.set_trace()` (at the moment, `up` doesn't take you up the stack but into the `nameko-worker-postmortem` code that inserts the breakpoint.)
