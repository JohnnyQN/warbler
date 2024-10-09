import os
from unittest import TestCase
from models import db, User
from app import app, CURR_USER_KEY

# Set the environment variable to use the test database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Disable CSRF during tests
app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    """Test user views."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            self.u1 = User.signup("test1", "test1@test.com", "password", None)
            self.u2 = User.signup("test2", "test2@test.com", "password", None)

            db.session.commit()

            self.u1_id = self.u1.id
            self.u2_id = self.u2.id

            # Log in user1
            with self.client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_view(self):
        """Test basic view functionality."""
        with app.app_context():
            resp = self.client.get(f"/users/{self.u1_id}")
            self.assertEqual(resp.status_code, 200)

    def test_followers(self):
        """Test if followers view works."""
        with app.app_context():
            resp = self.client.get(f"/users/{self.u1_id}/followers")
            self.assertEqual(resp.status_code, 200)

    def test_following(self):
        """Test if following view works."""
        with app.app_context():
            resp = self.client.get(f"/users/{self.u1_id}/following")
            self.assertEqual(resp.status_code, 200)
