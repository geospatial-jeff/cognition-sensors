import re

from sensors.landsat import Landsat_ARD, Landsat

ls7_ard = re.compile(r"^L(\S{1})(07)_(\S{2})_(\d{6})_(\d{8})_(\d{8})_(\w{3})_(\w{3})_(\w+)(\w{2}\.\S{3})")
ls8_ard = re.compile(r"^L(\S{1})(08)_(\S{2})_(\d{6})_(\d{8})_(\d{8})_(\w{3})_(\w{3})_(\w+)(\w{2}\.\S{3})")
ls8 = re.compile(r"^L(\S{1})(08)_(\w{4})_(\d{6})_(\d{8})_(\d{8})_(\d{2})_(\w{2})")

class InvalidPattern(BaseException):
    pass

class AssetLibrary(object):

    def __init__(self):
        self.regexes = {ls8: Landsat,
                        ls7_ard: Landsat_ARD,
                        ls8_ard: Landsat_ARD
                        }

class Asset(AssetLibrary):

    def __init__(self, fname):
        AssetLibrary.__init__(self)
        self.fname = fname
        self.sensor = self.lookup()

    def lookup(self):
        for regex in self.regexes:
            match = regex.match(self.fname)
            if match is not None:
                return self.regexes[regex](match.groups())
        raise InvalidPattern("Filename does not match any sensors in the library")

    def metadata(self):
        return self.sensor.metadata()