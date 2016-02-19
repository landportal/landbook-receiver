__author__ = 'Dani'

class FaoUriResolver:

    def __init__(self):
        self._equivalences = {}
        self._load_dict()

    def _load_dict(self):
	# TODO extract filepath to config file
        with open("countries/iso3ToFao.txt", "r") as content:
            lines = content.readlines()
            for line in lines:
                splitted = line.split(":")
                if len(splitted) == 2:
                    self._equivalences[splitted[0]] = splitted[1].replace("\n", "")

    def get_URI_from_iso3(self, iso3):
        """
        return the FAO URI of a country represented by the given iso3. If the iso3 is not recognized
        it returns None

        :param iso3:
        :return:
        """

        if iso3 not in self._equivalences:
            return None
        else:
            return "http://aims.fao.org/aos/geopolitical.owl#" + self._equivalences[iso3]
