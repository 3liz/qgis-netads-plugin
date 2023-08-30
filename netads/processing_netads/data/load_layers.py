__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Dict

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsExpressionContextUtils,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProcessingParameterString,
    QgsProviderRegistry,
)

from netads.processing_netads.data.base import BaseDataAlgorithm


class LoadLayersAlgorithm(BaseDataAlgorithm):
    """
    Chargement des couches netads depuis la base de données
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"
    CODE_CLIENT = "CODE_CLIENT"
    OUTPUT = "OUTPUT"

    def name(self):
        return "load_layers"

    def displayName(self):
        return "Chargement des couches depuis la base"

    def shortHelpString(self):
        return "Charger les couches de la base de données."

    def initAlgorithm(self, config: Dict):
        # INPUTS
        # Database connection parameters
        default = QgsExpressionContextUtils.globalScope().variable(
            "netads_connection_name"
        )
        # noinspection PyArgumentList
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            "Connexion PostgreSQL vers la base de données",
            "postgres",
            optional=False,
            defaultValue=default,
        )
        param.setHelp("Base de données où sont stockés les données")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA,
            "Schéma",
            self.CONNECTION_NAME,
            defaultValue="netads",
            optional=False,
        )
        param.setHelp("Nom du schéma des données netads")
        self.addParameter(param)

        param = QgsProcessingParameterString(
            self.CODE_CLIENT,
            "Code client NetADS",
            optional=True,
        )
        param.setHelp("Code client NetADS attribué à la collectivité")
        self.addParameter(param)

        self.addOutput(
            QgsProcessingOutputMultipleLayers(self.OUTPUT, "Couches de sortie")
        )

    def processAlgorithm(
        self,
        parameters: Dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema = self.parameterAsSchema(parameters, self.SCHEMA, context)

        key = "netads_idclient"
        code_client = self.parameterAsString(parameters, self.CODE_CLIENT, context)
        if code_client:
            QgsExpressionContextUtils.setProjectVariable(context.project(), key, code_client)
            feedback.pushInfo(
                f"Ajout du code client NetADS {code_client} dans la variable du projet '{key}'."
            )
        else:
            # The input was empty so the variable must be in the project already
            variables = context.project().customVariables()
            url = variables.get(key)
            if not url:
                # The virtual field needs this variable on runtime.
                raise QgsProcessingException(
                    f"Votre projet ne contient pas la variable {key}, vous devez donc renseigner la valeur "
                    f"pour l'URL"
                )

        feedback.pushInfo("## Connexion à la base de données ##")

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        connection: QgsAbstractDatabaseProviderConnection
        result_msg, uri = self.get_uri(connection)
        feedback.pushInfo(result_msg)

        feedback.pushInfo("")
        feedback.pushInfo("## Chargement des couches ##")

        output_layers = []
        for name in self.layers_name:
            result_msg, layer = self.import_layer(context, uri, schema, name)
            feedback.pushInfo(result_msg)
            if layer:
                output_layers.append(layer.id())

        return {
            self.OUTPUT: output_layers,
        }
