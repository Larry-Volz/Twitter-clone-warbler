"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

from sqlalchemy import exc #exception types

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

"""Does message model work """

""" Do likes work"""

class MessageModelTestCase(TestCase):
    """ test message model"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 105
        u = User.signup("TestUser", "testy@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    
    def test_message_model(self):
        """Does message model work?"""
        
        msg= Message(
            text="secret message",
            user_id=self.uid
        )

        db.session.add(msg)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "secret message")

    def test_likes(self):
        msg1 = Message(
            text="secret message",
            user_id=self.uid
        )

        msg2 = Message(
            text="another, even more secret message",
            user_id=self.uid 
        )

        u = User.signup("BartSimpson", "bart@email.com", "password", None)
        uid = 888
        u.id = uid
        db.session.add_all([msg1, msg2, u])
        db.session.commit()

        u.likes.append(msg1)

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, msg1.id)

