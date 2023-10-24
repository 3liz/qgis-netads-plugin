__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


import processing

from qgis.core import QgsProcessingContext, QgsProcessingException, QgsProject

from netads.processing_netads.data.load_layers import Key
from netads.tests.base_database import DatabaseTestCase
from netads.tests.feedbacks import FeedbackPrint


class TestPlugin(DatabaseTestCase):
    def test_import_layers(self):
        """Test import layers."""
        project = QgsProject()
        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))
        context = QgsProcessingContext()
        context.setProject(project)

        params = {
            "CONNECTION_NAME": "test_database",
            "SCHEMA": "netads",
        }
        alg = "netads:load_layers"

        with self.assertRaises(QgsProcessingException):
            # Code client is not correct
            processing.run(alg, params, feedback=FeedbackPrint(), context=context)

        params["CODE_CLIENT"] = "test"
        params["PREFIX_PARCELLE"] = "140"

        results = processing.run(
            alg,
            params,
            feedback=FeedbackPrint(),
            context=context,
        )

        variables = project.customVariables()
        self.assertEqual(variables[Key.Code], "test")
        self.assertEqual(variables[Key.Prefix], "140")

        self.assertEqual(3, len(results["OUTPUT"]))

    def test_import_layers_no_prefix(self):
        """Test import layers."""
        project = QgsProject()
        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))
        context = QgsProcessingContext()
        context.setProject(project)

        params = {
            "CONNECTION_NAME": "test_database",
            "SCHEMA": "netads",
        }
        alg = "netads:load_layers"

        with self.assertRaises(QgsProcessingException):
            # Code client is not correct
            processing.run(alg, params, feedback=FeedbackPrint(), context=context)

        params["CODE_CLIENT"] = "test"

        results = processing.run(
            alg,
            params,
            feedback=FeedbackPrint(),
            context=context,
        )

        variables = project.customVariables()
        self.assertEqual(variables[Key.Code], "test")
        self.assertNotIn(Key.Prefix, list(variables.keys()))

        self.assertEqual(3, len(results["OUTPUT"]))

    def test_import_layers_error_prefix(self):
        """Test import layers."""
        project = QgsProject()
        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))
        context = QgsProcessingContext()
        context.setProject(project)

        params = {
            "CONNECTION_NAME": "test_database",
            "SCHEMA": "netads",
        }
        alg = "netads:load_layers"

        with self.assertRaises(QgsProcessingException):
            # Code client is not correct
            processing.run(alg, params, feedback=FeedbackPrint(), context=context)

        params["CODE_CLIENT"] = "test"
        # Too short
        params["PREFIX_PARCELLE"] = "14"

        self.assertRaises(
            QgsProcessingException,
            processing.run,
            alg,
            params,
            feedback=FeedbackPrint(),
            context=context,
        )

        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))

        # Too long
        params["PREFIX_PARCELLE"] = "test"

        self.assertRaises(
            QgsProcessingException,
            processing.run,
            alg,
            params,
            feedback=FeedbackPrint(),
            context=context,
        )

        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))

    def test_import_layers_code_client_mandatory(self):
        """Test import layers."""
        project = QgsProject()
        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))
        context = QgsProcessingContext()
        context.setProject(project)

        params = {
            "CONNECTION_NAME": "test_database",
            "SCHEMA": "netads",
        }
        alg = "netads:load_layers"

        with self.assertRaises(QgsProcessingException):
            # Code client is not correct
            processing.run(alg, params, feedback=FeedbackPrint(), context=context)

        params["PREFIX_PARCELLE"] = "140"

        self.assertRaises(
            QgsProcessingException,
            processing.run,
            alg,
            params,
            feedback=FeedbackPrint(),
            context=context,
        )

        variables = project.customVariables()
        self.assertNotIn(Key.Code, list(variables.keys()))
        self.assertNotIn(Key.Prefix, list(variables.keys()))


if __name__ == "__main__":
    from qgis.testing import start_app

    start_app()
