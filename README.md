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
Then the reader should continue to src/server/dealer.py, which
contains the bulk of the logic for simulating the game.

- run-tests - Executable used to run the test suite
- main - Executable used to simulate a game of Evolution
- remote-main - Executable to start a silly player in Evolution
- \_\_init__.py - Make the direcotry a python module
<br/>
<br/>
- src/\_\_init__.py - Make the directory a python module
- src/core/\_\_init__.py - Make the directory a Python module
- src/core/card.py - Base card data representation
- src/core/connection.py - Base TCP socket functionality
- src/core/player.py - Base player data representation
- src/core/species.py - Base species data representation
- src/core/trait.py - Base trait data representation
- src/core/utils.py - Utility functions used throughout Evolution
<br/>
<br/>
- src/core/tests/test_trait.py - Test Trait data definition
- src/core/tests/test_utils.py - Test utility functions
<br/>
<br/>
- src/client/\_\_init__.py - Make the directory a Python module
- src/client/action.py - Action data representation for the external player
- src/client/data.py - Internal data representations for the external player
- src/client/dealer_proxy.py - Serialization / Deserialization for the external player
- src/client/feeding.py - Feeding data representation for the external player
- src/client/strategy.py - How the external player makes decisions
<br/>
<br/>
- src/client/tests/\_\_init__.py - Make directory a Python module
- src/client/tests/test_card.py - Test the Card data representation
- src/client/tests/test_species.py - Test the Species data representation
- src/client/tests/test_strategy.py - Test behavior of external player strategy
- src/client/tests/test_turn.py - Test internal representation of Turn
<br/>
<br/>
- src/server/\_\_init__.py - Make directory a Python module
- src/server/action.py - Player action result types and methods
- src/server/card.py - The internal Card data representation
- src/server/dealer.py - The internal Dealer data representation
- src/server/exception.py - Special exception types used in the game
- src/server/feeding.py - Feeding result types and methods
- src/server/player.py - The internal Player data representation
- src/server/player_proxy.py - Handles serialization/deserialization for the player
- src/server/species.py - The internal Species data representation
<br/>
<br/>
- src/server/tests/test-fest-10/* - Test fest tests for project 10
- src/server/tests/test-fest-11/* - Test fest tests for project 11
- src/server/tests/\_\_init__.py - Make directory a Python module
- src/server/tests/mock.py - Mocks used in testing
- src/server/tests/test_action.py - Test Action data representation
- src/server/tests/test_card.py - Test Card data representation
- src/server/tests/test_dealer.py - Test game dealer implementation
- src/server/tests/test_fest.py - Runs past test fests.
- src/server/tests/test_player.py - Test the internal player representation
- src/server/tests/test_species.py - Test species implementation
