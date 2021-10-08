"""User model tests."""

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()


        user1 = User.signup("Adam", "adam@eden.com", "noAppleForYou", "static/images/adam.jfif")
        user1.id = 101

        user2 = User.signup("Eve", "eve@eden.com", "justOneSliceOfPie?", "static/images/eve.jpg")
        user2.id = 102


        db.session.commit()

        u1 = User.query.get(user1.id)
        u2 = User.query.get(user2.id)

        self.u1 = u1
        self.u1_id = user1.id

        self.u2 = u2
        self.u2_id = user2.id


        self.client = app.test_client()

    
    def tearDown(self):
        result = super().tearDown()
        db.session.rollback()
        return result



    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_repre(self):
        """Does the repr method work as expected?"""
        # question: how?  No example in solution
        # self.assertEqual(self.u1.repr, f"<User #{self.id}: {self.username}, {self.email}>")

    def test_user_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_user_followed(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        self.assertEqual(len(self.u1.following), 0)

    def test_u1_followed(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        self.u1.followers.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.followers), 1)
        self.assertEqual(self.u1.followers[0].id, self.u2.id)

    def test_u1_not_followed(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        self.assertEqual(len(self.u1.followers), 0)

    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?"""
        user3 = User.signup("Testy", "whatev@now.com", "password", 'image.jpg')
        u_id = 103
        user3.id = u_id
        db.session.commit()

        user3 = User.query.get(u_id)

        # question: do I not need self. inside the assertion because it is a class method instead of instance?
        self.assertIsNotNone(user3)
        self.assertEqual(user3.username, "Testy")
        self.assertEqual(user3.email, "whatev@now.com")
        self.assertNotEqual(user3.password, "password")
        self.assertEqual(user3.image_url, "image.jpg")

        # Bcrypt strings should start with $2b$ - per instructor solution
        # note  .startswith() <-- in flask-sqlalchemy docs?
        self.assertTrue(user3.password.startswith("$2b$"))

    def test_not_unique_user(self):
        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        # user3 = User.signup("Testy", "whatev@now.com", "password", 'image.jpg')
        # u_id = 103
        # user3.id = u_id

        # user3_copy = User.signup("Testy", "whatev@now.com", "password", 'image.jpg')
        # u_copy_id = 103
        # user3_copy.id = u_copy_id

        # db.session.commit()

        # user3 = User.query.get(u_id)
        # user3_copy = User.query.get(u_copy_id)

        # question: how to test if these things are not unique?

        # self.assertNotEqual(user3.username, "Testy")
        # self.assertEqual(user3.email, "whatev@now.com")
        # self.assertNotEqual(user3.password, "password")
        # self.assertEqual(user3.image_url, "image.jpg")


    def test_no_username(self):
        '''Does user require a username'''
        no_username = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        no_username.id = uid
        with self.assertRaises(exc.IntegrityError) as context: #per solution question: why this syntax, where list?
            db.session.commit()

    def test_authenticate_user(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        u1 = self.u1
        response = User.authenticate("Adam", "noAppleForYou")
        self.assertEqual(u1, response)

    def test_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        u1 = self.u1
        response = User.authenticate("WrongName", "noAppleForYou")
        self.assertNotEqual(u1, response)
        self.assertFalse(response)

    def test_invalid_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        u1 = self.u1
        response = User.authenticate("Adam", "wrongPassword")
        self.assertNotEqual(u1, response)
        self.assertFalse(response)
