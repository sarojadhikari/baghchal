# -*- coding: utf-8 -*-
"""
Game class taken from
http://code.google.com/p/monkey-web/source/browse/trunk/monkey.py?r=23
"""
from google.appengine.ext import db

class Game(db.Model):
    """The data structure for an m,n,k,p,q-game.
    """
    state = db.StringProperty(default = 'waiting',
                              choices = ('waiting', 'playing', 'aborted',
                                         'draw', 'win'))
    players = db.ListProperty(item_type = db.Key)
    player_names = db.StringListProperty()
    current_player = db.IntegerProperty()
    turn = db.IntegerProperty(default = -1)
    data = db.StringListProperty()
    rule_set = db.ReferenceProperty(reference_class = RuleSet,
                                    required = True,
                                    collection_name = 'games')
    added = db.DateTimeProperty(auto_now_add = True)
    last_update = db.DateTimeProperty(auto_now_add = True)

    def add_player(self, player):
        """Adds a player to the game and starts the game if it has enough
        players.
        """
        if player.key() in self.players:
            raise JoinError('Player is already in game.')
        if len(self.players) >= self.rule_set.num_players:
            raise JoinError('Game is full.')
        if self.state != 'waiting':
            raise JoinError('Game is not accepting new players.')
       
        self.players.append(player.key())

        # Start the game when it has enough players.
        if len(self.players) == self.rule_set.num_players:
            random.shuffle(self.players)
            self.state = 'playing'
            self.turn = 0
            self.current_player = 1

        self.update_player_names()
        self.put(True)


    def abort(self):
        """Aborts a game if it is in play or removes it if it's waiting for more
        players.
        """
        if self.state == 'waiting':
            self.delete()
        elif self.state == 'playing':
            self.state = 'aborted'
            self.turn = -1
            self.put(True)
        else:
            raise AbortError('Cannot abort a game that has already been '
                             'completed.')

    def handle_cpu(self):
        """If the current player is a CPU player, makes a move.
        """
        if self.state != 'playing': return

        player = db.get(self.players[self.current_player - 1])
        if player.user == users.User('cpu@baghchal'):
            cpu = CpuPlayer(player)
            cpu.move(self)
   
    def move(self, player, x, y):
        """Puts a tile at the specified coordinates and makes sure all game
        rules are followed.
        """
        pkey = player.key()
        if pkey not in self.players: raise MoveError('Player not in game.')

        if self.state != 'playing': raise MoveError('Game not in play.')

        whose_turn = self.current_player
        player_turn = self.players.index(pkey) + 1
        if whose_turn != player_turn: raise MoveError('Not player\'s turn.')

        rs = self.rule_set
        np = rs.num_players
        m, n, k, p, q = rs.m, rs.n, rs.k, rs.p, rs.q

        board = self.unpack_board()
        if (x < 0 or x >= m or
            y < 0 or y >= n or
            board[x][y]): raise MoveError('Invalid tile position.')

        board[x][y] = whose_turn

        # Next turn.
        self.turn += 1

        # There's a win according to the rule set.
        if rs.is_win(board, player_turn, x, y):
            self.state = 'win'

            player.wins += 1
            player.put()
            for pkey in self.players:
                if pkey == player.key(): continue
                p = db.get(pkey)
                p.losses += 1
                p.put()

            self.rule_set.num_games += 1
            self.rule_set.put()
        # Board has been filled; draw.
        elif not util.contains(board, 0):
            self.state = 'draw'

            for pkey in self.players:
                p = db.get(pkey)
                p.draws += 1
                p.put()

            self.rule_set.num_games += 1
            self.rule_set.put()
        else:
            self.current_player = rs.whose_turn(self.turn)

        self.put(True)

    def pack_board(self):
        """Packs a list of lists into a list of strings, where each character
        represents a value in a sub-list.
        """
        if not hasattr(self, '_board'): return
        self.data = [string.join([str(self._board[x][y])
                                  for y in xrange(self.rule_set.n)], '')
                     for x in xrange(self.rule_set.m)]

    def put(self, update_time = False):
        """Does some additional processing before the entity is stored to the
        data store.
        """
        if self.is_saved():
            self.pack_board()
        else:
            # Set up a data structure that can store an m by n table
	    # change this to work for pieces in baghchal
            self.data = ['0' * self.rule_set.m
                         for i in xrange(self.rule_set.n)]

        if update_time: self.last_update = datetime.utcnow()
        db.Model.put(self)

    def remove_player(self, player):
        """Removes a player from the game or deletes the game if removing the
        player would make the game empty from players.
        """
        if player.key() not in self.players:
            raise LeaveError('Player is not in game.')

        if self.state == 'waiting':
            self.players.remove(player.key())

            # Determine the number of non-CPU players.
            humans = len(self.players)
            for pkey in self.players:
                if db.get(pkey).user == users.User('cpu@baghchal'):
                    humans -= 1

            # Only keep the game if there are non-CPU players left in the game.
            if humans > 0:
                self.update_player_names()
                self.put(True)
            else:
                self.delete()
        elif self.state == 'playing':
            # A player cannot actually leave a game that is in play. Instead,
            # the game is aborted and becomes unplayable.
            self.abort()
        else:
            raise LeaveError('Cannot leave a game that has already been '
                             'completed.')

    def unpack_board(self):
        """Unpacks a list of strings into a list of lists where each character
        in the list of strings represents a value in a sub-list.
        """
        if not hasattr(self, '_board'):
            self._board = [[int(val) for val in list(row)]
                           for row in self.data]
        return self._board

    def update_player_names(self):
        """Synchronizes the 'player_names' list with the names of the players in
        the game.
        """
        self.player_names = [db.get(p).nickname
                             for p in self.players]