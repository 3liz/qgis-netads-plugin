__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os
import time

from unittest import main

import processing

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
)

from netads.processing_netads.data.import_impacts import ListeType
from netads.processing_netads.provider import (
    NetAdsProvider as ProcessingProvider,
)
from netads.qgis_plugin_tools import plugin_test_data_path
from netads.tests.base_database import DatabaseTestCase

SCHEMA = "netads"


class TestImport(DatabaseTestCase):

    def tearDown(self) -> None:
        if SCHEMA in self.connection.schemas():
            self.connection.dropSchema(SCHEMA, True)
        del self.connection
        time.sleep(1)

    def test_import_impacts(self):
        """Test to import impacts in the database."""
        params = {
            "ENTREE": str(
                plugin_test_data_path("plui", "248000747_INFO_SURF_20201109.shp")
            ),
            "TYPE_IMPORT": ListeType.Servitude.value,
            "CHAMP_CODE": "code",
            "CHAMP_SOUS_CODE": "",
            "CHAMP_ETIQUETTE": "",
            "CHAMP_LIBELLE": "LIBELLE",
            "CHAMP_DESCRIPTION": "TXT",
            # "CHAMP_INSEE": "" let the one from commune layer
            "CONNECTION_NAME": os.getenv("TEST_QGIS_CONNEXION_NAME", "test_database"),
            "SCHEMA_NETADS": "netads",
        }
        provider = ProcessingProvider()
        alg = "{}:data_impacts".format(provider.id())
        results = processing.run(alg, params, feedback=self.feedback)

        # We don't have municipalities
        self.assertEqual(results["COUNT_FEATURES"], 0)
        self.assertEqual(results["COUNT_NEW_IMPACTS"], 11)

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection = metadata.findConnection("test_database")

        source = QgsCoordinateReferenceSystem(4326)
        destination = QgsCoordinateReferenceSystem(2154)
        transform = QgsCoordinateTransform(source, destination, QgsProject.instance())

        sql = "SELECT COUNT(id_impacts) FROM netads.impacts;"
        result = connection.executeSql(sql)
        self.assertEqual(11, result[0][0])

        communes = QgsVectorLayer(
            str(plugin_test_data_path("commune.geojson")), "commune", "ogr"
        )
        for feature in communes.getFeatures():
            geom = feature.geometry()
            geom.transform(transform)
            sql = (
                f"INSERT INTO netads.communes (nom, codeinsee, geom) "
                f"VALUES ("
                f"'{feature.attribute('name')}', "
                f"'{feature.attribute('insee')}', "
                f"ST_GeomFromText('{geom.asWkt()}', '2154')"
                f");"
            )
            # feedback.pushDebugInfo(sql)
            connection.executeSql(sql)

        sql = "SELECT COUNT(*) FROM netads.communes;"
        result = connection.executeSql(sql)
        self.assertEqual(1, result[0][0])

        results = processing.run(alg, params)

        # We have municipalities now
        self.assertEqual(results["COUNT_FEATURES"], 71)
        self.assertEqual(results["COUNT_NEW_IMPACTS"], 0)

        # INSEE should match the geojson
        sql = "SELECT codeinsee FROM netads.geo_impacts GROUP BY codeinsee;"
        result = connection.executeSql(sql)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "80016")

        # Empty geo_impacts
        sql = "TRUNCATE netads.geo_impacts RESTART IDENTITY;"
        connection.executeSql(sql)

        params["CHAMP_INSEE"] = "WRONGINSEE"
        alg = "{}:data_impacts".format(provider.id())
        results = processing.run(alg, params)

        # 0 because the INSEE code is 80999
        # The WRONGINSEE column has only INSEE code which are not in the commune.geojson
        # 80999 versus 800016
        self.assertEqual(results["COUNT_FEATURES"], 0)
        self.assertEqual(results["COUNT_NEW_IMPACTS"], 0)

        params["CHAMP_INSEE"] = "INSEE"
        alg = "{}:data_impacts".format(provider.id())
        results = processing.run(alg, params)

        # 70 because only 70 have a code INSEE = 80016
        self.assertEqual(results["COUNT_FEATURES"], 70)
        self.assertEqual(results["COUNT_NEW_IMPACTS"], 0)

        # INSEE should match the field 80016
        sql = "SELECT codeinsee FROM netads.geo_impacts GROUP BY codeinsee;"
        result = connection.executeSql(sql)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "80016")


if __name__ == "__main__":
    main()
