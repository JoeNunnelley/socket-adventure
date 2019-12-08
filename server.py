"""
A simple message server / client using socket
"""
import socket


class Server():
    """
    An adventure game socket server

    An instance's methods share the following variables:

    * self.socket: a "bound" server socket, as produced by socket.bind()
    * self.client_connection: a "connection" socket as produced by
      socket.accept()
    * self.input_buffer: a string that has been read from the connected client
      and has yet to be acted upon.
    * self.output_buffer: a string that should be sent to the connected client;
      for testing purposes this string should NOT end in a newline character.
      When writing to the output_buffer, DON'T concatenate: just overwrite.
    * self.done: A boolean, False until the client is ready to disconnect
    * self.room: one of 0, 1, 2, 3. This signifies which "room" the client is
      in, according to the following map:

                                     3                      N
                                     |                      ^
                                 1 - 0 - 2                  |

    When a client connects, they are greeted with a welcome message. And then
    they can move through the connected rooms. For example, on connection:

    OK! Welcome to Realms of Venture! This room has brown wall paper!  (S)
    move north                                                         (C)
    OK! This room has white wallpaper.                                 (S)
    say Hello? Is anyone here?                                         (C)
    OK! You say, "Hello? Is anyone here?"                              (S)
    move south                                                         (C)
    OK! This room has brown wall paper!                                (S)
    move west                                                          (C)
    OK! This room has a green floor!                                   (S)
    quit                                                               (C)
    OK! Goodbye!                                                       (S)

    Note that we've annotated server and client messages with *(S)* and *(C)*,
    but these won't actually appear in server/client communication. Also,
    you'll be free to develop any room descriptions you like: the only
    requirement is that each room have a unique description.
    """
    game_name = "Realms of Venture"

    def __init__(self, port=50000):
        """ Initialize the server """
        self.input_buffer = ""
        self.output_buffer = ""
        self.done = False
        self.socket = None
        self.client_connection = None
        self.port = port
        self.room = 0

    def connect(self):
        """ Connect to the socket """
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        address = ('127.0.0.1', self.port)
        self.socket.bind(address)
        self.socket.listen(1)

        print("Starting Server")
        self.client_connection, address = self.socket.accept()

    @staticmethod
    def room_description(room_number):
        """
        For any room_number in 0, 1, 2, 3, return a string that "describes"
        that room.

        Ex: `self.room_number(1)` yields "Brown wallpaper covers the walls,
        bathing the room in warm light reflected from the half-drawn curtains."

        :param room_number: int
        :return: str
        """
        return {
            0: "Happy rabbits hop contentedly in the center of the room"
               " whose walls are a verdant green with large windows"
               " looking out into a garden patio.",
            1: "A dark pit of despair swirls red and black embers in"
               " the center of a room painted with the dripping sorrow"
               " of a thousand unfortunate souls.",
            2: "Arthur Dent stands forlornly in the room in his pajamas"
               " and bunny slippers holding a towel for some reason as"
               " a large, low rumble of construction machinery is rapidly"
               " becoming louder",
            3: "The communal room of Seitch Tabr stretches out before you"
               " high walls of lazgun carved caves. Stilgar approaches"
               " and hands you your thumper and worm hooks."
            }[room_number]

    def greet(self):
        """
        Welcome a client to the game.

        Puts a welcome message and the description of the client's current room
        into the output buffer.

        :return: None
        """
        self.output_buffer = "Welcome to {}!\n {}".format(
            self.game_name,
            self.room_description(self.room)
        )

    def get_input(self):
        """
        Retrieve input from the client_connection. All messages from the client
        should end in a newline character: '\n'.

        This is a BLOCKING call. It should not return until there is some input
        from the client to receive.

        :return: None
        """
        print('Awaiting input...')
        data_chunk = 16

        try:
            self.input_buffer = ''
            while "\n" not in self.input_buffer:
                self.input_buffer += \
                    self.client_connection.recv(data_chunk).decode()

        except KeyboardInterrupt:
            print('quitting server')
            exit(1)

    def move(self, argument):
        """
        Moves the client from one room to another.

        Examines the argument, which should be one of:

        * "north"
        * "south"
        * "east"
        * "west"

        "Moves" the client into a new room by adjusting self.room to reflect
        the number of the room that the client has moved into.

        Puts the room description (see `self.room_description`) for the new
        room into "self.output_buffer".

        :param argument: str
        :return: None
        """
        available_moves = {
            0: ['west', 'east', 'north'],
            1: ['east'],
            2: ['west'],
            3: ['south']
        }

        argument = argument.lower().strip('\n')
        print("move requested: {}".format(argument))

        if self.room == 0 and argument in available_moves[self.room]:
            print('in room 0')
            if argument == 'west':
                print('moving {}'.format(argument))
                self.room = 1
            elif argument == 'east':
                print('moving {}'.format(argument))
                self.room = 2
            elif argument == 'north':
                print('moving {}'.format(argument))
                self.room = 3
            elif argument == 'south':
                print('moving {}'.format(argument))
            else:
                print('unexpected direction {}. staying in room {}'
                      .format(argument, self.room))

            self.output_buffer = self.room_description(self.room)
        elif self.room in (1, 2, 3) and argument in available_moves[self.room]:
            print('in room {}'.format(self.room))
            print('moving to {}'.format(argument))
            self.room = 0
            self.output_buffer = self.room_description(self.room)
        else:
            self.output_buffer = "Oops! You can't go that way"

    def say(self, argument):
        """
        Lets the client speak by putting their utterance into the output
        buffer.

        For example:
        `self.say("Is there anybody here?")`
        would put
        `You say, "Is there anybody here?"`
        into the output buffer.

        :param argument: str
        :return: None
        """
        print('Say message recieved')
        self.output_buffer = "\nYou say, \"{}\"".format(argument.strip('\n'))

    def invalid_command(self, message):
        """ Deal with an unexpected command type """
        print('Invalid command recieved')
        self.output_buffer = "\nError: {}".format(message.strip('\n'))

    def quit(self, message='Exit requested by user'):
        """
        Quits the client from the server.

        Turns `self.done` to True and puts "Goodbye!" onto the output buffer.

        Ignore the argument.

        :param argument: str
        :return: None
        """
        print('Goodbye! : {}'.format(message))
        self.output_buffer = "\nGoodbye!"
        self.done = True

    def route(self):
        """
        Examines `self.input_buffer` to perform the correct action (move, quit,
        or say) on behalf of the client.

        For example, if the input buffer contains "say Is anybody here?" then
        `route` should invoke `self.say("Is anybody here?")`. If the input
        buffer contains "move north", then `route` should invoke
        `self.move("north")`.

        :return: None
        """
        command, message = ['', '']

        if "quit" in self.input_buffer:
            command, message = ["quit", 'Requested by user']
        elif "say" in self.input_buffer:
            command, message = self.input_buffer.split(' ', 1)
        elif "move" in self.input_buffer:
            command, message = self.input_buffer.split(' ', 2)
        else:
            command, message = ['error', 'you input an invalid command']

        {
            "move": self.move,
            "say": self.say,
            "quit": self.quit,
            "error": self.invalid_command
        }[command](message)

    def push_output(self):
        """
        Sends the contents of the output buffer to the client.

        This method should prepend "OK! " to the output and append "\n" before
        sending it.

        :return: None
        """
        self.output_buffer = "\nOK! {}\n".format(self.output_buffer
                                                 .strip('\n'))
        self.client_connection.sendall(self.output_buffer.encode('utf-8'))

    def serve(self):
        """ Start the server listening """
        self.connect()
        self.greet()
        self.push_output()

        while not self.done:
            self.get_input()
            self.route()
            self.push_output()

        self.client_connection.close()
        self.socket.close()
