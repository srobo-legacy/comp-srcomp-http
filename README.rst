SR Comp HTTP
============

|Build Status| |Docs Status|

A HTTP interface around `SRComp <https://github.com/PeterJCLaw/srcomp/wiki/SRComp>`__,
the fifth round of `Student Robotics <http://srobo.org>`__ competition
software.

This repository provides a JSON API to accessing information about the
state of the competition. It is a lightweight
`Flask <http://flask.pocoo.org/>`__ application wrapping the
`SRComp <https://github.com/PeterJCLaw/srcomp>`__ python
APIs to the competition state.

Usage
-----

Run with ``./run $COMPSTATE``.

Test with ``./run-tests``.

Developers may wish to use the `SRComp
Dev <https://github.com/PeterJCLaw/srcomp-dev>`__ repo
to setup a dev instance.

State Caching
~~~~~~~~~~~~~

Since loading a given state repo takes a non-trivial amount of time,
this is cached within the Flask application. Updates to the state repo
are not tracked directly, and must be signalled by running the
``./update`` script provided.

Requirements
------------

-  PyYAML
-  Flask
-  python-dateutil
-  simplejson
-  nose (for testing)
-  mock (for testing)

Don't forget to also check the requirements for SRComp!

.. |Build Status| image:: https://travis-ci.org/PeterJCLaw/srcomp-http.png?branch=master
   :target: https://travis-ci.org/PeterJCLaw/srcomp-http

.. |Docs Status| image:: https://readthedocs.org/projects/srcomp-http/badge/?version=latest
   :target: http://srcomp-http.readthedocs.org/
