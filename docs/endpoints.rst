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
        "colour": "...",
        "get": "..."
    }

If present, the ``colour`` key contains the colour of the arena in HTML
hash format (eg: ``#00ff00``).

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
        "league_pos": "...",
        "location": {
          "get": "...",
          "name": "..."
        },
        "scores": {
            "league": "...",
            "knockout": "..."
        }
    }

/teams/ ``tla`` /image
----------------------

Get the team image.

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

/current
--------

Get information about parts of the competition state which change with
the current time.

.. code-block:: json

    {
        "delay": "...",
        "matches": "...",
        "time": "..."
    }

The ``delay`` value is the amount of delay in seconds currently active.
Note that this value is only useful during match periods (it will otherwise
be ``0``).

The ``matches`` key is a list of the matches which are currently being
played, as measured by the current time falling between the start and end
of their slot. They are presented in the same format as the `/matches`_
endpoint uses.

The ``time`` key is the current time on the server.

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

/locations
----------

Get information about the locations within the venue.

.. code-block:: json

    {
        "locations": {
            "..." : "..."
        }
    }

The location objects returned are in the same format as those described below.

/locations/``name``
-------------------

Get information about a named location within the venue.

.. code-block:: json

    {
        "locations": {
            "..." : {
                "display_name": "...",
                "get": "...",
                "teams": [ "..." ],
                "shepherds": {
                    "name": "...",
                    "colour": "..."
                }
            }
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

You can also limit the number of matches returned by passing a value to the
``limit`` query parameter. This can be both a postive and negative integer.
Positive limits start from the first match and work forwards, whilst negative
limits start from the last match and work backwards.

.. code-block:: json

    {
        "last_scored": ...,
        "matches": [
            {
                "arena": "...",
                "display_name": "Match ...",
                "num": ...,
                "scores": {
                    "game": {
                        "...": ...,
                        "...": ...,
                        "...": ...,
                        "...": ...
                    },
                    "league": {
                        "...": ...,
                        "...": ...,
                        "...": ...,
                        "...": ...
                    },
                    "normalised": {
                        "...": ...,
                        "...": ...,
                        "...": ...,
                        "...": ...
                    },
                    "ranking": {
                        "...": ...,
                        "...": ...,
                        "...": ...,
                        "...": ...
                    }
                },
                "teams": [
                    "...", "...", "...", "..."
                ],
                "times": {
                    "game": {
                        "end": "...",
                        "start": "..."
                    },
                    "slot": {
                        "end": "...",
                        "start": "..."
                    },
                    "staging": {
                        "end": "...",
                        "start": "...",
                        "opens": "...",
                        "closes": "...",
                        "signal_teams": "...",
                        "signal_shepherds": "..."
                    }
                },
                "type": "..."
            }
        ]
    }

``last_scored`` contains the same value as in the following endpoint.
Any dates are in ISO 8601 format.

Only one of the ``league`` or ``normalised`` sub-keys of ``scores`` will be
present, though they contain the same data. ``league`` will be present for
league matches while ``normalised`` will be present for knockout matches.

Notably, teams which are disqualified or no-show from a match will have a
normalised (league) score of zero but will still have a position value.

The staging deadline is available in ``times.staging.end`` while the
``times.staging.start`` value is when shepherds should start looking for teams
although this isn't a strict value.

/matches/last_scored
--------------------

.. code-block:: json

    {
        "last_scored": ...
    }

``last_scored`` contains the highest match number which has a score assigned,
but may be ``null`` if no scores have yet been entered.

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
              "type": "...",
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

/knockout
---------

Get a list of rounds which make up the knockouts. Each round is expressed
as a list of matches which make up that round. Matches are expressed using
the same format as the `/matches`_ endpoint.

/tiebreaker
-----------

Get the tiebreaker match, or raise a 404 error if one does not exist. The match
is expressed in the same format as the `/matches`_ endpoint.

.. code-block:: json

    {
        "tiebreaker": ...
    }
