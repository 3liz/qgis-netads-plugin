__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


import processing

from qgis.core import QgsProcessingContext, QgsProcessingException, QgsProject

from netads.tests.base_database import DatabaseTestCase
from netads.tests.feedbacks import FeedbackPrint


class TestPlugin(DatabaseTestCase):

    def test_import_layers(self):
        """ Test import layers. """
        project = QgsProject()
        variables = project.customVariables()
        self.assertNotIn("netads_idclient", list(variables.keys()))
        context = QgsProcessingContext()
        context.setProject(project)

        params = {
            'CONNECTION_NAME': 'test_database',
            'SCHEMA': 'netads',
        }
        alg = "netads:load_layers"

        with self.assertRaises(QgsProcessingException):
            # Code client is not correct
            processing.run(alg, params, feedback=FeedbackPrint(), context=context)

        params['CODE_CLIENT'] = 'test'

        results = processing.run(
            alg,
            params,
            feedback=FeedbackPrint(),
            context=context,
        )

        variables = project.customVariables()
        self.assertEqual(variables["netads_idclient"], "test")

        self.assertEqual(3, len(results['OUTPUT']))


if __name__ == "__main__":
    from qgis.testing import start_app
    start_app()
