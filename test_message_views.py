import os
from unittest import TestCase
from models import db, connect_db, Message, User
from app import app, CURR_USER_KEY

# Set the environment variable to use the test database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Disable CSRF during tests
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)

            db.session.add(self.testuser)
            db.session.commit()

            # Refresh testuser to keep it attached to the session
            self.testuser = db.session.get(User, self.testuser.id)

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_message(self):
        """Can user add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now that the session is set, add the message
            resp = c.post("/messages/new", data={"text": "Hello"})

            # Check if it redirected
            self.assertEqual(resp.status_code, 302)

            # Make sure the message was added
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
