__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Callable, Dict, List, Tuple, Union

from qgis import processing
from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsCoordinateReferenceSystem,
    QgsDataSourceUri,
    QgsExpression,
    QgsExpressionContextUtils,
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeatureSource,
    QgsProcessingFeedback,
    QgsProcessingOutputNumber,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterProviderConnection,
    QgsProcessingUtils,
    QgsProviderConnectionException,
    QgsProviderRegistry,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import NULL

from netads.processing_netads.data.base import BaseDataAlgorithm

LISTE_TYPE = (
    'ZONAGE', 'SERVITUDE', 'PRESCRIPTION', 'INFORMATION',
)

# Impact = namedtuple('Impact', ['type', 'code', 'sous_code', 'etiquette', 'libelle', 'description'])


def sql_error_handler(func: Callable):
    """Decorator to catch sql exceptions."""

    def inner_function(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(f"Erreur SQL : {str(e)}")

    return inner_function


class ImportImpactsAlg(BaseDataAlgorithm):
    """
    Import des données impacts PLUI
    """

    ENTREE = "ENTREE"
    TYPE_IMPORT = "TYPE_IMPORT"
    CHAMP_CODE = "CHAMP_CODE"
    CHAMP_SOUS_CODE = "CHAMP_SOUS_CODE"
    CHAMP_ETIQUETTE = "CHAMP_ETIQUETTE"
    CHAMP_LIBELLE = "CHAMP_LIBELLE"
    CHAMP_DESCRIPTION = "CHAMP_DESCRIPTION"
    CHAMP_INSEE = "CHAMP_INSEE"
    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA_NETADS = "SCHEMA_NETADS"
    COUNT_FEATURES = "COUNT_FEATURES"
    COUNT_NEW_IMPACTS = "COUNT_NEW_IMPACTS"

    def name(self):
        return "data_impacts"

    def displayName(self):
        return "Import des impacts"

    def shortHelpString(self):
        return (
            "Ajout des données pour les tables des impacts"
            "<br>"
            f"Le champ pour le 'type' doit contenir exclusivement les valeurs suivantes : "
            f"{','.join(LISTE_TYPE)}"
        )

    # noinspection PyMethodOverriding
    def initAlgorithm(self, config: Dict):
        # noinspection PyUnresolvedReferences
        param = QgsProcessingParameterFeatureSource(
            self.ENTREE,
            "Couche en entrée pour les impacts",
            [QgsProcessing.TypeVectorPolygon],
            optional=False,
        )
        param.setHelp("Couche vecteur qu'il faut importer dans la base de données")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterEnum(
            self.TYPE_IMPORT,
            "Type d'import",
            options=LISTE_TYPE,
            optional=False,
        )
        param.setHelp("Type d'import concernant la couche")
        param.setUsesStaticStrings(True)
        self.addParameter(param)

        param = QgsProcessingParameterField(
            self.CHAMP_CODE,
            "Champ pour le code",
            parentLayerParameterName=self.ENTREE,
            optional=False,
        )
        # TODO check ?
        param.setHelp(
            "Zonage, Impacts, Servitudes, Droit de Préemption, Lotissement, ou tout autre valeur libre"
        )
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.CHAMP_SOUS_CODE,
            "Champ pour le sous-code",
            parentLayerParameterName=self.ENTREE,
            optional=True,
        )
        param.setHelp("Valeur libre")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.CHAMP_ETIQUETTE,
            "Champ des étiquettes",
            parentLayerParameterName=self.ENTREE,
            optional=True,
        )
        param.setHelp("Champ des étiquettes pour l'impact")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.CHAMP_LIBELLE,
            "Champ des libellés",
            parentLayerParameterName=self.ENTREE,
            optional=False,
        )
        param.setHelp("Champ des libellés pour l'impact")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.CHAMP_DESCRIPTION,
            "Champ des descriptions",
            parentLayerParameterName=self.ENTREE,
            optional=True,
        )
        param.setHelp("Champ des libellés pour l'impact")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.CHAMP_INSEE,
            "Champ du code INSEE",
            parentLayerParameterName=self.ENTREE,
            optional=True,
        )
        param.setHelp(
            "Champ du code INSEE pour l'impact. Si le champ n'est pas fourni, le code INSEE proviendra "
            "de l'intersection avec la commune."
        )
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            "Connexion PostgreSQL vers la base de données",
            "postgres",
            optional=False,
            defaultValue=QgsExpressionContextUtils.globalScope().variable(
                "netads_connection_name"
            ),
        )
        param.setHelp("Base de données de destination")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA_NETADS,
            "Schéma NetADS",
            self.CONNECTION_NAME,
            defaultValue="netads",
            optional=False,
        )
        param.setHelp("Nom du schéma des données NetADS")
        self.addParameter(param)

        self.addOutput(
            QgsProcessingOutputNumber(self.COUNT_FEATURES, "Nombre d'entités importés")
        )

        self.addOutput(
            QgsProcessingOutputNumber(
                self.COUNT_NEW_IMPACTS, "Nombre de nouveaux impacts"
            )
        )

    # noinspection PyMethodOverriding
    def checkParameterValues(self, parameters: Dict, context: QgsProcessingContext):
        # noinspection PyArgumentList
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        # schema_netads = self.parameterAsSchema(
        #     parameters, self.SCHEMA_NETADS, context
        # )
        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        connection: QgsAbstractDatabaseProviderConnection
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )
        # TODO faire la vérification
        return super().checkParameterValues(parameters, context)

    # noinspection PyMethodOverriding
    def processAlgorithm(
        self,
        parameters: Dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        # noinspection PyArgumentList
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema_netads = self.parameterAsSchema(parameters, self.SCHEMA_NETADS, context)

        # noinspection PyArgumentList
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        connection: QgsAbstractDatabaseProviderConnection
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )

        couche_entree = self.parameterAsSource(parameters, self.ENTREE, context)
        import_type = self.parameterAsEnumString(parameters, self.TYPE_IMPORT, context)
        champ_code = self.parameterAsString(parameters, self.CHAMP_CODE, context)
        champ_sous_code = self.parameterAsString(parameters, self.CHAMP_SOUS_CODE, context)
        champ_etiquette = self.parameterAsString(parameters, self.CHAMP_ETIQUETTE, context)
        champ_libelle = self.parameterAsString(parameters, self.CHAMP_LIBELLE, context)
        champ_description = self.parameterAsString(parameters, self.CHAMP_DESCRIPTION, context)
        champ_insee = self.parameterAsString(parameters, self.CHAMP_INSEE, context)

        results = {
            self.COUNT_FEATURES: 0,
            self.COUNT_NEW_IMPACTS: 0,
        }

        if feedback.isCanceled():
            return results

        uniques = self.unique_couple_input(
            feedback,
            import_type,
            champ_code,
            champ_sous_code,
            champ_etiquette,
            champ_libelle,
            champ_description,
            couche_entree,
        )
        # uniques :

        connection.executeSql("BEGIN;")

        existing_impacts = self.existing_impacts_in_database(connection, schema_netads, feedback)

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return results

        missing_in_db = list(set(uniques) - set(existing_impacts.values()))

        feedback.pushInfo(
            f"Dans le jeu de données, il y a {len(missing_in_db)} nouveau(x) impact(s) par rapport à la "
            f"base: "
        )

        self.insert_new_impacts(
            connection,
            existing_impacts,
            feedback,
            missing_in_db,
            schema_netads,
        )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return results

        crs = self.check_current_crs(connection, schema_netads, feedback)
        feedback.pushInfo(f"La projection du schéma {schema_netads} est en EPSG:{crs}.")

        couche_entree = self.prepare_data(
            context,
            feedback,
            self.parameterAsLayer(parameters, self.ENTREE, context),
            QgsCoordinateReferenceSystem(f"EPSG:{crs}"),
        )
        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return results

        if not champ_insee:
            feedback.pushInfo(
                "Le champ code INSEE n'est pas renseigné, l'import des impacts va donc découper les "
                f"impacts selon les communes de la couche 'communes' dans le schéma '{schema_netads}'."
            )
            couche_entree = self.split_layer_impacts(
                context, feedback, couche_entree, connection, schema_netads
            )
            champ_insee = "communes_codeinsee"
            insee_list = None
        else:
            feedback.pushInfo(
                f"Le code INSEE est '{champ_insee}' dans la couche {couche_entree.name()}. L'import va "
                f"utiliser la valeur de ce champ pour l'import."
            )
            sql = f"SELECT codeinsee FROM {schema_netads}.communes GROUP BY codeinsee;"
            result = connection.executeSql(sql)
            insee_list = [str(f[0]) for f in result]
            feedback.pushDebugInfo(
                f"Uniquement les impacts dont le code INSEE est dans la liste suivante "
                f"{','.join(insee_list)} vont être importés car ils sont dans la table "
                f"{schema_netads}.communes."
            )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return results

        feedback.pushInfo("Insertion des geo-impacts dans la base de données")
        success = self.import_new_geo_impacts(
            connection,
            feedback,
            import_type,
            champ_insee,
            insee_list,
            champ_code,
            champ_sous_code,
            champ_etiquette,
            champ_libelle,
            champ_description,
            couche_entree,
            schema_netads,
            crs,
        )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return results

        connection.executeSql("COMMIT;")
        feedback.pushInfo(f"{success} nouvelles géo-impacts dans la base de données")
        results[self.COUNT_FEATURES] = success
        results[self.COUNT_NEW_IMPACTS] = len(missing_in_db)
        return results

    @sql_error_handler
    def split_layer_impacts(
        self,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
        layer: QgsVectorLayer,
        connection: QgsAbstractDatabaseProviderConnection,
        schema: str,
    ) -> Union[QgsVectorLayer, None]:
        """Make the union between impacts and municipalities."""

        uri = QgsDataSourceUri(connection.uri())
        uri.setSchema(schema)
        uri.setTable("communes")
        uri.setKeyColumn("id_communes")
        uri.setGeometryColumn("geom")
        municipalities = QgsVectorLayer(uri.uri(), "communes", "postgres")

        feedback.pushInfo("Intersection des impacts avec les communes")
        params = {
            "INPUT": layer,
            "OVERLAY": municipalities,
            "OVERLAY_FIELDS_PREFIX": "communes_",
            "OUTPUT": "memory:",
        }

        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:union",
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo("Transformation de multi vers unique de la nouvelle couche")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:multiparttosingleparts",
            {
                "INPUT": result["OUTPUT"],
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo("Intersection OK des impacts avec les communes.")
        layer = QgsProcessingUtils.mapLayerFromString(result["OUTPUT"], context, True)
        return layer

    @sql_error_handler
    def import_new_geo_impacts(
        self,
        connection: QgsAbstractDatabaseProviderConnection,
        feedback: QgsProcessingFeedback,
        import_type: str,
        champ_insee: str,
        insee_list: list,
        champ_code: str,
        champ_sous_code: str,
        champ_etiquette: str,
        champ_libelle: str,
        champ_description: str,
        layer: QgsVectorLayer,
        schema: str,
        crs: str,
    ) -> int:
        """Import in the database new geo-impacts."""
        success = 0
        fail = 0
        for feature in layer.getFeatures():
            content_code = self.clean_value(feature.attribute(champ_code))
            content_libelle = self.clean_value(feature.attribute(champ_libelle))
            insee_code = self.clean_value(feature.attribute(champ_insee))

            if insee_code == "":
                feedback.pushDebugInfo(
                    f"Omission de l'entité {feature.id()} car elle n'a pas de code INSEE."
                )
                fail += 1
                continue

            if insee_list and str(insee_code) not in insee_list:
                feedback.pushDebugInfo(
                    f"Omission de l'entité {feature.id()} car son code INSEE n'est pas dans la table "
                    f"netads.communes"
                )
                fail += 1
                continue

            # noinspection PyArgumentList
            sql = (
                f"SELECT id_impacts "
                f"FROM "
                f"{schema}.impacts "
                f"WHERE "
                f"type = {QgsExpression.quotedString(import_type)} "
                f"AND code = {QgsExpression.quotedString(content_code)} "
                f"AND libelle = {QgsExpression.quotedString(content_libelle)} "
            )
            if champ_sous_code:
                content_sous_code = self.clean_value(feature.attribute(champ_sous_code))
                sql += f"AND sous_code = {QgsExpression.quotedString(content_sous_code)} "

            if champ_etiquette:
                content_etiquette = self.clean_value(feature.attribute(champ_etiquette))
                sql += f"AND etiquette = {QgsExpression.quotedString(content_etiquette)} "

            if champ_description:
                content_description = self.clean_value(feature.attribute(champ_description))
                sql += f"AND description = {QgsExpression.quotedString(content_description)}"

            sql += ';'
            # feedback.pushDebugInfo(sql)
            result = connection.executeSql(sql)
            if len(result) == 0:
                # This case shouldn't happen ... it's covered before
                feedback.reportError(
                    f"Omission de l'entité {feature.id()} car elle n'y a pas d'impact dans la base"
                )
                fail += 1
            else:
                # Useless, but better to check
                ids = [str(v[0]) for v in result]
                if len(ids) > 1:
                    feedback.reportError(
                        f"Erreur, il y a plusieurs identifiants lors de l'exécution : {sql}"
                    )
                    fail += 1
                    continue
                else:
                    ids = ids[0]

                # noinspection PyArgumentList
                sql = (
                    f"INSERT INTO {schema}.geo_impacts (id_impacts, libelle, codeinsee, geom) "
                    f"VALUES ("
                    f"'{ids}', "
                    f"{QgsExpression.quotedString(content_libelle)}, "
                    f"'{insee_code}', "
                    f"ST_GeomFromText('{feature.geometry().asWkt()}', '{crs}')"
                    f") RETURNING id_geo_impacts;"
                )
                # feedback.pushDebugInfo(sql)
                result = connection.executeSql(sql)
                feedback.pushDebugInfo(
                    f"    Insertion source ID {result[0][0]} → {feature.id()}"
                )
                success += 1

        if fail > 0:
            feedback.reportError(
                f"Veuillez lire logs ci-dessus, car il y a {fail} entités en défaut."
            )

        return success

    @classmethod
    def clean_value(cls, value: str) -> str:
        """Replace the NULL by empty string if needed."""
        if value == NULL:
            value = ""
        return value

    @classmethod
    @sql_error_handler
    def check_current_crs(
        cls,
        connection: QgsAbstractDatabaseProviderConnection,
        schema: str,
        feedback: QgsProcessingFeedback,
    ) -> str:
        """The current CRS in the database"""
        # Let's do it on communes
        # QGIS doesn't manage well if geometry_columns is not the search_path anyway
        sql = (
            f"SELECT srid FROM public.geometry_columns "
            f"WHERE f_table_schema = '{schema}' AND f_table_name = 'communes';"
        )
        feedback.pushInfo("Récupération du CRS de la base de données.")
        feedback.pushDebugInfo(sql)
        result = connection.executeSql(sql)
        return str(result[0][0])

    @staticmethod
    def existing_impacts_in_database(
        connection: QgsAbstractDatabaseProviderConnection,
        schema_netads: str,
        feedback: QgsProcessingFeedback,
    ) -> dict[str, Tuple[str, str, str, str, str, str]]:
        """Return the list of existing impacts in database."""
        uri = QgsDataSourceUri(connection.uri())
        uri.setSchema(schema_netads)
        uri.setTable("impacts")
        uri.setKeyColumn("id_impacts")
        existing_impacts = {}
        existing_constraints_layer = QgsVectorLayer(uri.uri(), "impacts", "postgres")
        for feature in existing_constraints_layer.getFeatures():
            existing_impacts[feature.attribute("id_impacts")] = (
                feature['type'],
                feature['code'],
                feature['sous_code'],
                feature['etiquette'],
                feature['libelle'],
                feature['description'],
            )
        feedback.pushInfo(f"Il y a {len(existing_impacts)} impact(s) dans la base de données.")
        return existing_impacts

    @staticmethod
    @sql_error_handler
    def insert_new_impacts(
        connection: QgsAbstractDatabaseProviderConnection,
        existing_impacts: Dict,
        feedback: QgsProcessingFeedback,
        missing_in_db: List[Tuple[str, str, str, str, str, str]],
        schema_netads: str,
    ) -> dict[str, Tuple[str, str, str, str, str, str]]:
        """Insert new impacts in the database and return the list of new IDs."""
        # Input import_type, contenu_code, contenu_sous_code, contenu_etiquette,
        # contenu_libelle, contenu_description
        for new in missing_in_db:
            # Quicker, to get the impact_id with raw SQL query
            # noinspection PyArgumentList
            sql = (
                f"INSERT INTO {schema_netads}.impacts "
                f"(type, code, sous_code, etiquette, libelle, description) "
                f"VALUES ("
                f"{QgsExpression.quotedString(new[0])}, "
                f"{QgsExpression.quotedString(new[1])}, "
                f"{QgsExpression.quotedString(new[2])}, "
                f"{QgsExpression.quotedString(new[3])}, "
                f"{QgsExpression.quotedString(new[4])}, "
                f"{QgsExpression.quotedString(new[5])}) "
                f"RETURNING id_impacts;"
            )
            result = connection.executeSql(sql)
            feedback.pushDebugInfo(
                f"    Insertion dans la table 'impacts' : ID {result[0][0]} → {new}"
            )
            existing_impacts[result[0][0]] = (new[0], new[1], new[2], new[3], new[4], new[5])
        return existing_impacts

    @staticmethod
    def prepare_data(
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
        layer: QgsVectorLayer,
        target_crs: QgsCoordinateReferenceSystem,
    ) -> Union[QgsVectorLayer, None]:
        """Preparing the data : fixing geometries, projection and multi."""
        feedback.pushInfo("Correction des géométries dans la couche en entrée")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:fixgeometries",
            {
                "INPUT": layer,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo("Transformation de multi vers unique")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:multiparttosingleparts",
            {
                "INPUT": result["OUTPUT"],
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo(f"Reprojection vers {target_crs.authid()}")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:reprojectlayer",
            {
                "INPUT": result["OUTPUT"],
                "TARGET_CRS": target_crs,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        layer = QgsProcessingUtils.mapLayerFromString(result["OUTPUT"], context, True)
        feedback.pushInfo("Les données sont désormais OK pour l'import.")
        return layer

    @staticmethod
    def unique_couple_input(  # noqa: C901
        feedback: QgsProcessingFeedback,
        import_type: str,
        champ_code: str,
        champ_sous_code: str,
        champ_etiquette: str,
        champ_libelle: str,
        champ_description: str,
        layer: QgsProcessingFeatureSource,
    ) -> List[Tuple[str, str, str, str, str, str]]:
        """Fetch unique couples in the input layer."""
        uniques = []
        uniques_str = []
        for feature in layer.getFeatures():
            # Optional inputs
            contenu_sous_code = ''
            contenu_etiquette = ''
            contenu_description = ''

            contenu_code = ImportImpactsAlg.clean_value(feature[champ_code])
            if champ_sous_code:
                contenu_sous_code = ImportImpactsAlg.clean_value(feature[champ_sous_code])
            if champ_etiquette:
                contenu_etiquette = ImportImpactsAlg.clean_value(feature[champ_etiquette])
            contenu_libelle = ImportImpactsAlg.clean_value(feature[champ_libelle])
            if champ_description:
                contenu_description = ImportImpactsAlg.clean_value(feature[champ_description])

            couple = (
                import_type, contenu_code, contenu_sous_code, contenu_etiquette, contenu_libelle,
                contenu_description
            )
            if couple not in uniques:
                uniques.append(couple)
                uniques_str.append(str(couple))

            if feedback.isCanceled():
                return []

        couple = [champ_code, champ_sous_code, champ_etiquette, champ_libelle, champ_description]
        # To remove empty variables, all fields are not required
        couple = [f for f in couple if f]
        feedback.pushInfo(
            f"Dans la source, il y a {len(uniques)} couples uniques sur le couple : {','.join(couple)}"
        )
        if len(couple) != 5:
            feedback.pushInfo(
                "Étant donné que certain(s) champ(s) est/sont vide(s) dans lors du lancement de "
                "l'algorithme :")
            if not champ_sous_code:
                feedback.pushInfo("⚫ Sous-code")
            if not champ_etiquette:
                feedback.pushInfo("⚫ Étiquette")
            if not champ_sous_code:
                feedback.pushInfo("⚫ Description")
        feedback.pushDebugInfo(
            f"Liste des couples uniques dans la couche : {','.join(uniques_str)}"
        )

        return uniques
