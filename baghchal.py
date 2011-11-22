"""
As it stands now, the code below is based on the most basic demo from
the google appengine code and is very preliminary as it just about
runs the already existing html/javascript code that has all the
baghchal code ready to go.

The next step is to modify the following code to make the program be
able to identify users from their login information, and create a
game when there are two people logged in simultaneously and be
able to change turns and identify winners and prompt so.
"""

import cgi
import datetime # not needed now.
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class GetInfo(db.Model):
	author = db.UserProperty();
	date = db.DateTimeProperty(auto_now_add=True)
	
class MainPage(webapp.RequestHandler):
  def get(self):
    template_values = {'game':1, 'turn':1}
    user = users.get_current_user()
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))
    self.response.out.write(user)

application = webapp.WSGIApplication([
  ('/', MainPage)],
  debug = True)
  
def main():
  run_wsgi_app(application)
  
if __name__ == "__main__":
  main()
