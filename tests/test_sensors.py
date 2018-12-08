import unittest
import gdaljson
from sensors import Asset
import sensors

class SensorTestCases(unittest.TestCase):

    @staticmethod
    def open_vrt(path):
        with open(path) as vrtfile:
            contents = vrtfile.read()
            vrt = gdaljson.VRTDataset(contents)
            return vrt

    def setUp(self):
        self.awsearth_landsat8 = self.open_vrt('templates/aws_earth_landsat8.vrt')

    def test_aws_earth_landsat8(self):
        asset = Asset(self.awsearth_landsat8)
        self.assertEqual(type(asset.sensor), sensors.sensors.LandsatAWSEarth)