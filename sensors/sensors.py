from datetime import datetime
from copy import deepcopy

import satstac
from . import stac


class Landsat(object):

    """https://landsat.usgs.gov/landsat-collections"""

    def __init__(self, parts):
        self.parts = list(parts)
        self.labels = ['sensor', 'satellite']
        self.lut = [{'C': 'OLI_TIRS',
                     'O': 'OLI',
                     'E': 'ETM+',
                     'T': 'TM',
                     'M': 'MSS'
                     },
                    {'07': 'Landsat7',
                     '08': 'Landsat8',
                     },
                    ]

    def metadata(self):
        tile_numbers = self.parts.pop(3)
        d = {'wrs_path': tile_numbers[:3],
             'wrs_row': tile_numbers[3:],
             'acquisition_date': datetime.strptime(self.parts.pop(3), '%Y%m%d'),
             'production_date': datetime.strptime(self.parts.pop(3), '%Y%m%d'),
             "collection_number": self.parts.pop(3),
             "collection_category": self.parts.pop(3),
             "processing_level": self.parts.pop(-1)}
        for idx, item in enumerate(self.lut):
            d.update({self.labels[idx]: self.lut[idx][self.parts.pop(0)]})
        return d


class Landsat_ARD(object):

    """https://landsat.usgs.gov/ard"""

    def __init__(self, parts):
        self.parts = list(parts)
        self.labels = ["sensor", "satellite", "regional_grid", "product"]
        self.lut = [{'T': 'TM',
                     'E': 'ETM',
                     'C': 'OLI_TIRS',
                     'O': 'OLI',
                     },
                    {'04': 'Landsat4',
                     '05': 'Landsat5',
                     '07': 'Landsat7',
                     '08': 'Landsat8'
                     },
                    {'CU': 'CONUS',
                     'AK': 'Alaska',
                     'HI': 'Hawaii'
                     },
                    {'TA': 'top of atmosphere reflectance',
                     'BT': 'brightness temperature',
                     'SR': 'surface reflectance',
                     'ST': 'land surface temperature',
                     'SOA': 'solar azimuth angle',
                     'SOZ': 'solar zenith angle',
                     'SEA': 'sensor azimuth angle',
                     'SEZ': 'sensor zenith angle',
                     'PIXELQA': 'pixel quality attributes',
                     'RADSATQA': 'radiometric saturation',
                     'LINEAGEQA': 'lineage index',
                     'SRATMOSOPACITYQA': 'internal landsat 4-7 surface reflectance atmospheric opacity',
                     'SRCLOUDQA': 'internal Landsat 4-7 surface reflectane quality',
                     'SRAEROSOLQA': 'internal Landsat 8 surface reflectance aerosol parameters'}]

    def metadata(self):
        parts_copy = deepcopy(self.parts)
        tile_numbers = parts_copy.pop(3)
        d = {'horizontal_tile_number': tile_numbers[:3],
             'vertical_tile_number': tile_numbers[3:],
             'acquisition_date': datetime.strptime(parts_copy.pop(3), '%Y%m%d').strftime('%Y-%m-%d'),
             'production_date': datetime.strptime(parts_copy.pop(3), '%Y%m%d').strftime('%Y-%m-%d'),
             'collection_number': parts_copy.pop(3),
             'ard_version': parts_copy.pop(3),
             'band': parts_copy.pop(-1)[1]
             }
        for idx, item in enumerate(self.lut):
            d.update({self.labels[idx]: self.lut[idx][parts_copy.pop(0)]})
        return d


    def stac_item(self, vrt, catalog):
        #Build STAC item with metadata
        metadata = self.metadata()
        stac_item = stac.Item(vrt)
        stac_item['properties'] = metadata
        stac_item['assets'] = {'raw': {'href': vrt.filename}}

        #Create stat-stac item
        item_path = '${horizontal_tile_number}/${vertical_tile_number}/${acquisition_date}'
        satstac_item = satstac.Item(stac_item)
        catalog.add_item(satstac_item, path=item_path)
        return satstac_item


