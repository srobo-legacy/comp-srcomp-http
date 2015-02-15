Endpoints
=========

/
-

Get an object containing the URLs for the various parts of the competition
interface.

.. code-block:: json

    {
        "arenas": "...",
        "teams": "...",
        "corners": "...",
        "config": "...",
        "state": "...",
        "matches": "..."
    }

/arenas
-------

Get an object containing all arenas.

.. code-block:: json

    {
        "arenas": {
            "...": "..."
        }
    }

The arena objects returned are in the same format as those described below.

/arenas/ ``name``
-----------------

Get information about an arena.

.. code-block:: json

    {
        "name": "...",
        "display_name": "...",
        "get": "..."
    }

/teams
------

Get an object containing all teams.

.. code-block:: json

    {
        "teams": {
            "...": "..."
        }
    }

The team objects returned are in the same format as those described below.

/teams/ ``tla``
---------------

Get information about a team.

.. code-block:: json

    {
        "name": "...",
        "get": "...",
        "tla": "...",
        "scores": {
            "league": "...",
            "knockout": "..."
        }
    }

/corners
--------

Get an object containing all corners.

.. code-block:: json

    {
        "corners": {
            "...": "..."
        }
    }

The corner objects returned are in the same format as those described below.

/corners/ ``number``
--------------------

Get information about a corner.

.. code-block:: json

    {
        "number": "...",
        "get": "...",
        "colour": "..."
    }

/state
------

Get the latest commit that the competition is working with.

.. code-block:: json

    {
        "state": "..."
    }

/config
-------

Get general information about the configuration of the competition and the host.

.. code-block:: json

    {
        "match_slots": {
            "pre": "...",
            "match": "...",
            "post": "...",
            "total": "..."
        }
    }

/matches
--------

Get a load of matches.

You can specify which matches are returned with various queries.

``type``
    The type of match.

``arena``
    The arena the match is in.

``num``
    The number of the match.

``game_start_time``
    The start time of the game.

``game_end_time``
    The end time of the game.

``slot_start_time``
    The start time of the timeslot allocated to the game.

``slot_end_time``
    The end time of the timeslot allocated to the game.

Each parameter can be taken in the form of: ``<start>..<end>``, ``..<end>``,
``<start>..`` and ``<value>``.

/periods
--------

Get a list of match periods. A match period is a block of time during which
a collection of matches (of the same type) occur. For example, the first
morning of the first day of the competition might have one period, and the
Knockouts might be another.


.. code-block:: json

    {
        "periods": [
            {
              "description": "A description of the period for humans",
              "end_time": "...",
              "matches": {
                "first_num": "...",
                "last_num": "..."
              },
              "max_end_time": "...",
              "start_time": "..."
            }
        ]
    }

The ``matches`` field will only be present if there are matches there are
matches in this period.
