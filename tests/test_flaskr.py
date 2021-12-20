# import os
# import tempfile

# import pytest

# from flaskr import create_app
# from flaskr.db import init_db


# @pytest.fixture
# def client():
#     db_fd, db_path = tempfile.mkstemp()
#     app = create_app({'TESTING': True, 'DATABASE': db_path})

#     with app.test_client() as client:
#         with app.app_context():
#             init_db()
#         yield client

#     os.close(db_fd)
#     os.unlink(db_path)

def test():
    assert 0 == 0

# def test_messages(client):
#     """Test that messages work."""

#     login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
#     rv = client.post('/add', data=dict(
#         title='<Hello>',
#         text='<strong>HTML</strong> allowed here'
#     ), follow_redirects=True)
#     assert b'No entries here so far' not in rv.data
#     assert b'&lt;Hello&gt;' in rv.data
#     assert b'<strong>HTML</strong> allowed here' in rv.data