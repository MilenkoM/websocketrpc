websocketrpc
============

This is a small RPC (Remote Procedure Call) module, which uses WebSockets as transport layer.

It depends on:

  * Python_
  * Tornado_
  * tinyrpc_


.. _Python: http://www.python.org/
.. _Tornado: http://tornadoweb.org/
.. _tinyrpc: https://tinyrpc.readthedocs.org/en/latest/


Installation
------------

.. code-block:: sh

   pip install websocketrpc


Usage
-----

Have a look at tests/server.py and tests/client.py to see how it works.

Running Tests
-------------

.. code-block:: sh
    
    cd websocketrpc/tests; python -m unittest discover
