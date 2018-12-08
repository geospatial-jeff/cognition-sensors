import re
import os

from sensors.sensors import Landsat_ARD, Landsat

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

    def __init__(self, vrt):
        AssetLibrary.__init__(self)
        self.vrt = vrt
        self.fname = os.path.split(vrt.filename)[-1]
        self.sensor = self.lookup()

    def lookup(self):
        for regex in self.regexes:
            match = regex.match(self.fname)
            if match is not None:
                return self.regexes[regex](match.groups())
        raise InvalidPattern("Filename does not match any sensors in the library")

    def metadata(self):
        return self.sensor.metadata()

    def stac_item(self):
        """Creates a STAC item and adds to collection (opened with sat-stac)"""
        return self.sensor.stac_item(self.vrt)

    def stac_path(self):
        return self.sensor.stac_path()