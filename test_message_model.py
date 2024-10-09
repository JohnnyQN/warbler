import os
from unittest import TestCase
from app import app
from models import db, Message, User

# Set the environment variable to use the test database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Disable CSRF during tests
app.config['WTF_CSRF_ENABLED'] = False

class MessageModelTestCase(TestCase):
    """Test message model."""

    def setUp(self):
        """Set up test client and sample data."""
        self.client = app.test_client()

        # Set up application context
        with app.app_context():
            db.drop_all()
            db.create_all()

            # Add a sample user
            u = User.signup(username="testuser", email="test@test.com", password="password", image_url=None)
            db.session.commit()

            self.user_id = u.id

    def tearDown(self):
        """Clean up fouled transactions."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_message_model(self):
        """Does basic message model work?"""
        with app.app_context():
            # Add a sample message
            m = Message(text="Test message", user_id=self.user_id)
            db.session.add(m)
            db.session.commit()

            # Check that the message is in the database
            self.assertEqual(Message.query.count(), 1)
            self.assertEqual(m.text, "Test message")
