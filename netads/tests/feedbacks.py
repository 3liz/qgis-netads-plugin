__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.core import QgsProcessingFeedback


class FeedbackPrint(QgsProcessingFeedback):

    def setProgressText(self, text: str):
        print(text)

    def pushInfo(self, info: str):
        print(info)

    def pushCommandInfo(self, info: str):
        print(info)

    def pushDebugInfo(self, info: str):
        print(info)

    def pushConsoleInfo(self, info: str):
        print(info)

    def pushWarning(self, warning: str) -> None:
        print(warning)

    # noinspection PyPep8Naming
    def reportError(self, error: str, fatalError: bool = False):
        _ = fatalError
        print(error)
