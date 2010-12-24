# -*- coding: utf-8 -*-
import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

import players
import games

class MainPage(webapp.RequestHandler):
    def get(self):
	template_values = {'game':1, 'turn':1}
	user = users.get_current_user()
	path = os.path.join(os.path.dirname(__file__), 'index.html')
	self.response.out.write(template.render(path, template_values))
	self.response.out.write(user)

    def create_game(self, which):
	"""Creates a new game
	"""
	player = players.Player.get_current(self)
	game = games.Game(which)
	game.put()
	
	player.join(game)
	
	return game.key().id()
	
    def join_game(self, game):
	"""Joins an existing game.
	"""
	if not isinstance(game, games.Game):
	    game = monkey.Game.get_by_id(game)
	    if not game: raise ValueError('Invalid game id.')
	    
	    player = monkey.Player.get_current(self)
	    player.join(game)
	    
	    return self.get_game_status(game)

    def leave_game(self, game):
	"""Leaves an existing game.
	"""
	if not isinstance(game, monkey.Game):
	    game = monkey.Game.get_by_id(game)
	    if not game: raise ValueError('Invalid game id.')
	    player = monkey.Player.get_current(self)
	    player.leave(game)
			
	
application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
  run_wsgi_app(application)
  
if __name__ == "__main__":
  main()
