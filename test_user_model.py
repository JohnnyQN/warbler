import os
from unittest import TestCase
from models import db, User
from app import app

# Set the environment variable to use the test database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Disable CSRF during tests
app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            u1 = User.signup("test1", "test1@test.com", "password", None)
            u2 = User.signup("test2", "test2@test.com", "password", None)

            db.session.add_all([u1, u2])
            db.session.commit()

            self.u1_id = u1.id
            self.u2_id = u2.id

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_model(self):
        """Does basic user model work?"""

        with app.app_context():
            u = User.query.get(self.u1_id)
            self.assertEqual(u.username, "test1")
            self.assertEqual(u.email, "test1@test.com")

    def test_signup(self):
        """Can a user sign up?"""
        with app.app_context():
            new_user = User.signup("newuser", "new@user.com", "password", None)
            db.session.commit()
            
            self.assertEqual(User.query.filter_by(username="newuser").first().email, "new@user.com")
