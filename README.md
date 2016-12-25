# Evolution

This is an implementation of Evolution, built during Matthias Felleisen's Spring 2016 software development class.

The full rules and specifications of the game can be found here: http://www.ccs.neu.edu/home/matthias/4500-s16/index.html.

In the interests of preserving our final project, the code has not been modified since it was turned in.


## Running the game with remote players

To start the server, run the following command from the current directory:

    ./main

This opens up the a socket and port, and waits for players to connect.
<br/>
<br/>
To start a remote player, run the following command from the current directory:

    ./remote-main $host $port

This tries to create a remote player and connect it to the given $host and $port.


## Simulating the game with non-remote players

To simulate the game with the default (non-remote) player implementation, run
the following command from the current directory:

    ./static-main $num-players

where $num-players is an integer in [3, 8] and represents the number of players you would like to simulate the game with.


## Running tests:

Run the following command from the current directory:

    ./run-tests


## How to start reading:

The best place to begin reading this code is main. That gives a high
level overview of how data enters the system, is processed, and is exported.
Then the reader should continue to evolution/server/dealer.py, which
contains the bulk of the logic for simulating the game.

- run-tests - Executable used to run the test suite
- main - Executable used to simulate a game of Evolution
- remote-main - Executable to start a silly player in Evolution
- \_\_init__.py - Make the direcotry a python module
- evolution/__init__.py - Make the directory a python module
<br/>
<br/>
- evolution/core/\_\_init__.py - Make the directory a Python module
- evolution/core/card.py - Base card data representation
- evolution/core/connection.py - Base TCP socket functionality
- evolution/core/player.py - Base player data representation
- evolution/core/species.py - Base species data representation
- evolution/core/trait.py - Base trait data representation
- evolution/core/utils.py - Utility functions used throughout Evolution
<br/>
<br/>
- evolution/core/tests/test_trait.py - Test Trait data definition
- evolution/core/tests/test_utils.py - Test utility functions
<br/>
<br/>
- evolution/client/\_\_init__.py - Make the directory a Python module
- evolution/client/action.py - Action data representation for the external player
- evolution/client/data.py - Internal data representations for the external player
- evolution/client/dealer_proxy.py - Serialization / Deserialization for the external player
- evolution/client/feeding.py - Feeding data representation for the external player
- evolution/client/strategy.py - How the external player makes decisions
<br/>
<br/>
- evolution/client/tests/\_\_init__.py - Make directory a Python module
- evolution/client/tests/test_card.py - Test the Card data representation
- evolution/client/tests/test_species.py - Test the Species data representation
- evolution/client/tests/test_strategy.py - Test behavior of external player strategy
- evolution/client/tests/test_turn.py - Test internal representation of Turn
<br/>
<br/>
- evolution/server/\_\_init__.py - Make directory a Python module
- evolution/server/action.py - Player action result types and methods
- evolution/server/card.py - The internal Card data representation
- evolution/server/dealer.py - The internal Dealer data representation
- evolution/server/exception.py - Special exception types used in the game
- evolution/server/feeding.py - Feeding result types and methods
- evolution/server/player.py - The internal Player data representation
- evolution/server/player_proxy.py - Handles serialization/deserialization for the player
- evolution/server/species.py - The internal Species data representation
<br/>
<br/>
- evolution/server/tests/test-fest-10/* - Test fest tests for project 10
- evolution/server/tests/test-fest-11/* - Test fest tests for project 11
- evolution/server/tests/\_\_init__.py - Make directory a Python module
- evolution/server/tests/mock.py - Mocks used in testing
- evolution/server/tests/test_action.py - Test Action data representation
- evolution/server/tests/test_card.py - Test Card data representation
- evolution/server/tests/test_dealer.py - Test game dealer implementation
- evolution/server/tests/test_fest.py - Runs past test fests.
- evolution/server/tests/test_player.py - Test the internal player representation
- evolution/server/tests/test_species.py - Test species implementation