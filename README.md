#SR Comp HTTP

[![Build Status](https://travis-ci.org/PeterJCLaw/srcomp-http.png?branch=master)](https://travis-ci.org/PeterJCLaw/srcomp-http)

A HTTP interface around [SRComp](http://srobo.org/trac/wiki/SRComp), the
fifth round of [Student Robotics](http://srobo.org) competition software.

This repository provides a JSON API to accessing information about the
state of the competition. It is a lightweight [Flask](http://flask.pocoo.org/)
application wrapping the [SRComp](https://www.studentrobotics.org/cgit/comp/srcomp.git)
python APIs to the competition state.

## Usage

Run with `./app.py`.

Test with `./run-tests`.

Developers almost certainly don't want to use this repo directly, and are
instead encouraged to use the [SRComp Dev](https://www.studentrobotics.org/cgit/comp/srcomp-dev.git)
repo instead. That repo includes (and then serves) most of the clients of
the API, which makes side-by-side development much easier.

## Requirements

* PyYAML
* Flask
* python-dateutil
* simplejson
* nose (for testing)

Don't forget to also check the requirements for SRComp!
