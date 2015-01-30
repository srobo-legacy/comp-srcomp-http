SR Comp HTTP
============

|Build Status|

A HTTP interface around `SRComp <http://srobo.org/trac/wiki/SRComp>`__,
the fifth round of `Student Robotics <http://srobo.org>`__ competition
software.

This repository provides a JSON API to accessing information about the
state of the competition. It is a lightweight
`Flask <http://flask.pocoo.org/>`__ application wrapping the
`SRComp <https://www.studentrobotics.org/cgit/comp/srcomp.git>`__ python
APIs to the competition state.

Usage
-----

Run with ``./app.py``.

Test with ``./run-tests``.

Developers almost certainly don't want to use this repo directly, and
are instead encouraged to use the `SRComp
Dev <https://www.studentrobotics.org/cgit/comp/srcomp-dev.git>`__ repo
instead. That repo includes (and then serves) most of the clients of the
API, which makes side-by-side development much easier.

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
