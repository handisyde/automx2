"""
Test basic functions of the automx2 Flask application.
"""
import unittest

from flask import Response

from automx2.generators.outlook import NS_AUTODISCOVER
from automx2.generators.outlook import NS_RESPONSE
from automx2.model import db
from automx2.model import populate_db
from automx2.server import APPLE_CONFIG_ROUTE
from automx2.server import MOZILLA_CONFIG_ROUTE
from automx2.server import MSOFT_CONFIG_ROUTE
from automx2.server import app
from automx2.views import CONTENT_TYPE_XML
from automx2.views import EMAIL_MOZILLA
from automx2.views import EMAIL_OUTLOOK


def body(response: Response) -> str:
    return str(response.data, encoding='utf-8', errors='strict')


class TestCase(unittest.TestCase):
    create_db = True

    def setUp(self) -> None:
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        with app.app_context():
            db.init_app(app)
            db.drop_all()
            if self.create_db:
                db.create_all()
                populate_db()
                db.session.commit()

    def tearDown(self) -> None:
        with app.app_context():
            db.drop_all()
            db.session.commit()

    def get(self, *args, **kwargs) -> Response:
        kwargs['follow_redirects'] = True
        return self.app.get(*args, **kwargs)

    def post(self, *args, **kwargs) -> Response:
        kwargs['follow_redirects'] = True
        return self.app.post(*args, **kwargs)

    def get_apple_config(self, address: str) -> Response:
        return self.get(f'{APPLE_CONFIG_ROUTE}?{EMAIL_MOZILLA}={address}')

    def get_mozilla_config(self, address: str) -> Response:
        return self.get(f'{MOZILLA_CONFIG_ROUTE}?{EMAIL_MOZILLA}={address}')

    def get_msoft_config(self, address: str) -> Response:
        data = (
            f'<Autodiscover xmlns="{NS_AUTODISCOVER}">'
            f'<AcceptableResponseSchema>{NS_RESPONSE}</AcceptableResponseSchema>'
            '<Request>'
            f'<{EMAIL_OUTLOOK}>{address}</{EMAIL_OUTLOOK}>'
            '</Request>'
            '</Autodiscover>'
        )
        return self.post(MSOFT_CONFIG_ROUTE, data=data, content_type=CONTENT_TYPE_XML)


if __name__ == '__main__':
    unittest.main()
