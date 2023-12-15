"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follow
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from flask import session
from flask_bcrypt import Bcrypt

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

bcrypt = Bcrypt()
PASSWORD = bcrypt.generate_password_hash("password", rounds=5).decode("utf-8")

class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Tests that user model has 0 messages and 0 followers."""
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_user1_is_following_user2(self):
        """Tests that user1 is following user 2."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)

        db.session.commit()

        self.assertEqual(len(u1.following), 1)
        self.assertNotEqual(len(u1.following), 0)
        self.assertTrue(u1.is_following(u2))

    def test_user1_is_not_following_user2(self):
        """Tests that user1 is not following user 2."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.following), 0)
        self.assertNotEqual(len(u1.following), 1)
        self.assertFalse(u1.is_following(u2))

    def test_user1_is_followed_by_user2(self):
        """Tests that user1 is followed by user2."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u2.following.append(u1)

        db.session.commit()

        self.assertTrue(u1.is_followed_by(u2))
        self.assertEqual(len(u2.following), 1)
        self.assertNotEqual(len(u2.following), 0)

    def test_user1_is_not_followed_by_user2(self):
        """Tests that user1 is not followed by user2."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_followed_by(u2))
        self.assertEqual(len(u2.following), 0)
        self.assertNotEqual(len(u2.following), 1)