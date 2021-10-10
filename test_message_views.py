"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 999999
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "testing"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "testing")

        def test_add_message_without_auth(self):
            """Can use add a message without signing in?"""
            with self.client as c:
                resp = c.post("/messages/new", data={"text": "testing again"}, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", str(resp.data))
                #question: why is this not showing as another test?

        def test_add_invalid_user(self):
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = 888 # non-existant user

                resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", str(resp.data))


        def test_like_unlike(self):
            """ Does user Like or unlike a message for the current logged-in user"""


        def test_messages_show(self):
            """does system show a message."""
    
            m = Message(
                id=101,
                text="help me I'm meeeeellllting",
                user_id=self.testuser_id
            )
            
            db.session.add(m)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id
                
                m = Message.query.get(101)

                resp = c.get(f'/messages/{m.id}')

                self.assertEqual(resp.status_code, 200)
                self.assertIn(m.text, str(resp.data))


        def test_messages_destroy(self):
            """Does system delete a message."""
    
            m = Message(
                id=777,
                text="testingpalooza",
                user_id=self.testuser_id
            )
            db.session.add(m)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

                resp = c.post("/messages/777/delete", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                m = Message.query.get(777)
                self.assertIsNone(m)


        
