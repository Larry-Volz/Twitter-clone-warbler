"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

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


class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="TestyTesterson",
                                    email="testy@test.com",
                                    password="password",
                                    image_url=None)

        self.testuser_id = 999999
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("TestithonTesterson", "testy1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("TestopherTesterson", "testy2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("Zaphod", "zaphod@hgg.com", "password", None)
        self.u4 = User.signup("Arthur", "arthur@hgg.com", "password", None)

        db.session.commit()

        def tearDown(self):
            resp = super().tearDown()
            db.session.rollback()
            return resp

        def test_users_list(self):
            """does view list all users?"""
            with self.client as client:
                resp = client.get("/users")

                self.assertIn("TestyTesterson", str(resp.data))
                self.assertIn("TestithonTesterson", str(resp.data))
                self.assertIn("TestopherTesterson", str(resp.data))
                self.assertIn("Zaphod", str(resp.data))
                self.assertIn("Arthur", str(resp.data))

        def test_users_search(self):
            """does view return the searched-for string?"""
            with self.client as client:
                resp = client.get("/users?q=test")

                self.assertIn("TestyTesterson", str(resp.data))
                self.assertIn("TestithonTesterson", str(resp.data))            

                self.assertNotIn("Zaphod", str(resp.data))
                self.assertNotIn("Arthur", str(resp.data))

        def test_user_show_oneuser(self):
            """does view return the user by id?"""
            with self.client as client:
                resp = client.get(f"/users/{self.testuser_id}")

                self.assertEqual(resp.status_code, 200)

                self.assertIn("TestyTesterson", str(resp.data))

        def setup_msgs_likes(self):
            """create test messages and a like"""
            m1 = Message(text="message number 1", user_id=self.testuser_id)
            m2 = Message(text="2nd warble", user_id=self.testuser_id)
            m3 = Message(id=555, text="liked post", user_id=self.u1_id)
            db.session.add_all([m1, m2, m3])
            db.session.commit()

            like1 = Likes(user_id=self.testuser_id, message_id=555)

            db.session.add(like1)
            db.session.commit()

        with self.client as client:
            resp = client.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

        # question:  (to study later) FROM SOLUTION WITH NO EXPLANATION OR EXAMPLES IN THE ASSIGNMENTS USING 'BEAUTIFULSOUP'
        # def test_user_show_with_likes(self):
        #     self.setup_likes()
        #     self.assertIn("@testuser", str(resp.data))
        #     soup = BeautifulSoup(str(resp.data), 'html.parser')
        #     found = soup.find_all("li", {"class": "stat"})
        #     self.assertEqual(len(found), 4)

        #     # test for a count of 2 messages
        #     self.assertIn("2", found[0].text)

        #     # Test for a count of 0 followers
        #     self.assertIn("0", found[1].text)

        #     # Test for a count of 0 following
        #     self.assertIn("0", found[2].text)

        #     # Test for a count of 1 like
        #     self.assertIn("1", found[3].text)

        def test_add_like(self):
            """does add_like create a like?"""
            msg = Message(id=1965, text="my birthyear", user_id=self.u1_id)
            db.session.add(msg)
            db.session.commit()

            with self.client as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser_id

                resp = client.post("/messages/1965/like", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                likes = Likes.query.filter(Likes.message_id==1965).all()
                self.assertEqual(len(likes), 1)
                self.assertEqual(likes[0].user_id, self.testuser_id)


        
    