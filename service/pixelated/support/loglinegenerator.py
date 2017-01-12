from zope.interface import Interface


class ILogLineGenerator(Interface):
    def getLogLine(self):
        """ Return a string that will be logged, or None. This method will be called every second.
        """
