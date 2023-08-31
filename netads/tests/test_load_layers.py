__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


import processing

from tests.feedbacks import FeedbackPrint

from netads.tests.base_database import DatabaseTestCase


class TestPlugin(DatabaseTestCase):

    def test_import_layers(self):
        """ Test import layers. """
        results = processing.run(
            "netads:load_layers",
            {
                'CONNECTION_NAME': 'test_database',
                'SCHEMA': 'netads',
                'CODE_CLIENT': 'test'
            },
            feedback=FeedbackPrint(),
        )

        self.assertEqual(3, len(results['OUTPUT']))


if __name__ == "__main__":
    from qgis.testing import start_app
    start_app()
