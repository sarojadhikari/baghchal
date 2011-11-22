# -*- coding: utf-8 -*-
"""
Player class taken from 
http://code.google.com/p/monkey-web/source/browse/trunk/monkey.py?r=23
"""
from google.appengine.ext import db

class Player(db.Model):
    user = db.UserProperty()
    nickname = db.StringProperty()
    password = db.StringProperty()
    draws = db.IntegerProperty(default = 0)
    losses = db.IntegerProperty(default = 0)
    wins = db.IntegerProperty(default = 0)
    session = db.StringProperty()
    expires = db.DateTimeProperty()

    @staticmethod
    def from_user(user, nickname = None):
        """Gets a Player instance from a User instance.
        """
        player = Player.gql('WHERE user = :1', user).get()
        if not player:
            if not nickname: nickname = user.nickname()
            player = Player(user = user,
                            nickname = nickname)
            player.put()

        return player

    @staticmethod
    def get_current(handler):
        """Retrieves a Player instance for the currently logged in user.
        """
        curuser = users.get_current_user()
        if curuser:
            # User is logged in with a Google account.
            player = Player.from_user(curuser)
        else:
            try:
                # User has a session.
                session = handler.request.cookies['session']
                query = Player.all()
                query.filter('session =', session)
                query.filter('expires >', datetime.utcnow())
                player = query.get()
            except KeyError:
                player = None

            if not player:
                # Create a new anonymous player.
                player = Player(user = users.User('anonymous@baghchal'),
                                nickname = 'Anonymous')
                player.start_session(handler)

        return player

    @staticmethod
    def log_in(nickname, password, handler):
        """Retrieves a player instance, based on a nickname and a password, and
        starts a session.

        The SHA-256 hash of the password must match the hash stored in the
        database, otherwise an exception will be raised.
        """
        player = Player.all().filter('nickname =', nickname).get()
        if not player:
            raise LogInError('Could not find a player with the specified '
                             'nickname.')

        if player.user != users.User('player@baghchal'):
            raise LogInError('Cannot log in as that user.')

        if hashlib.sha256(password).hexdigest() != player.password:
            raise LogInError('Invalid password.')

        player.start_session(handler)
        return player

    @staticmethod
    def register(nickname, password, handler = None):
        """Creates a new player that is registered to the application (instead
        of using Google Accounts.)

        Only the SHA-256 hash of the password will be stored so that in case the
        database should be exposed, the passwords would not be of any use to the
        attacker.
        """
        try:
            Player.validate(nickname)
        except PlayerNameError, e:
            raise RegisterError('Could not use nickname (%s)' % (e))

        if len(password) < 4:
            raise RegisterError('Password should be at least 4 characters '
                                'long.')

        player = Player(user = users.User('player@baghchal'),
                        nickname = nickname,
                        password = hashlib.sha256(password).hexdigest())


        if handler:
            player.start_session(handler)
        else:
            player.put()

        return player
       
    @staticmethod
    def validate(nickname):
        """Validates a nickname and throws an exception if it's invalid.
        """
        if nickname in ('Anonymous', 'CPU'):
            raise PlayerNameError(nickname + ' is a reserved nickname.')
       
        if not re.match('^[A-Za-z]([\\-\\._ ]?[A-Z0-9a-z]+)*$', nickname):
            raise PlayerNameError('Nickname should start with a letter, '
                                  'followed by letters and/or digits, '
                                  'optionally with dashes, periods, '
                                  'underscores or spaces inbetween.')
        if len(nickname) < 3:
            raise PlayerNameError('Nickname should be at least three '
                                  'characters long.')
        if len(nickname) > 20:
            raise PlayerNameError('Nickname must not be any longer than 20 '
                                  'characters.')

        if Player.all().filter('nickname =', nickname).count() > 0:
            raise PlayerNameError('Nickname is already in use.')

        return True

    def display_name(self):
        return '%s (%d)' % (self.nickname, self.wins)

    def is_anonymous(self):
        return self.user == users.User('anonymous@baghchal')

    def join(self, game):
        """Convenience method for adding a player to a game.
        """
        game.add_player(self)

    def leave(self, game):
        """Convenience method for removing a player from a game.
        """
        game.remove_player(self)

    def rename(self, nickname):
        """Changes the nickname of the player.
        """
        if nickname == self.nickname: return

        if nickname == 'Anonymous' and self.user == users.User('anonymous@baghchal'):
            pass
        else:
            Player.validate(nickname)

        self.nickname = nickname
        self.put()

        # This results in very long query times and might have to be disabled.
        # Everything would still work, it's just that games created before the
        # player changed nickname will still show the old nickname.
        games = Game.all().filter('players =', self.key())
        for game in games:
            game.update_player_names()
            game.put()

    def end_session(self, handler):
        """Removes a session from the database and the client, effectively
        logging the player out.
        """
        self.session = None
        self.expires = None
        self.put()
       
        cookie = 'session=; expires=Fri, 31-Jul-1987 03:00:00 GMT'
        handler.response.headers['Set-Cookie'] = cookie
        del handler.request.cookies['session']

    def start_session(self, handler):
        """Gives the player a session id and stores it as a cookie in the user's
        browser.
        """
        self.session = uuid.uuid4().get_hex()
        self.expires = datetime.utcnow() + timedelta(days = 7)
        self.put()

        # Build and set cookie
        ts = time.strftime('%a, %d-%b-%Y %H:%M:%S GMT',
                           self.expires.timetuple())
        cookie = '%s=%s; expires=%s' % ('session', self.session, ts)

        handler.response.headers['Set-Cookie'] = cookie
        handler.request.cookies['session'] = self.session