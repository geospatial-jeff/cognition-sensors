import os
from datetime import datetime
from dateutil.parser import parse
from copy import deepcopy

import requests
import satstac
from . import stac
from . import utils


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
        parts_copy = deepcopy(self.parts)
        tile_numbers = parts_copy.pop(3)
        d = {'wrs_path': tile_numbers[:3],
             'wrs_row': tile_numbers[3:],
             'acquisition_date': datetime.strptime(parts_copy.pop(3), '%Y%m%d'),
             'production_date': datetime.strptime(parts_copy.pop(3), '%Y%m%d'),
             "collection_number": parts_copy.pop(3),
             "collection_category": parts_copy.pop(3),
             "processing_level": parts_copy.pop(-1)}
        for idx, item in enumerate(self.lut):
            d.update({self.labels[idx]: self.lut[idx][parts_copy.pop(0)]})
        return d

    def stac_item(self, vrt):
        #Build STAC item with metadata
        metadata = self.metadata()
        stac_item = stac.Item(vrt)
        stac_item['properties'] = metadata
        stac_item['assets'] = {'raw': {'href': vrt.filename}}

        #Create stat-stac item
        item_path = '${wrs_path}/${wrs_row}/${acquisition_date}'
        satstac_item = satstac.Item(stac_item)
        return satstac_item

class LandsatAWSEarth(Landsat):

    def __init__(self, parts):
        Landsat.__init__(self, parts)

    def metadata(self):
        parts_copy = deepcopy(self.parts)
        tile_numbers = parts_copy.pop(3)
        d = {'wrs_path': tile_numbers[:3],
             'wrs_row': tile_numbers[3:],
             'acquisition_date': datetime.strptime(parts_copy.pop(3), '%Y%m%d'),
             'production_date': datetime.strptime(parts_copy.pop(3), '%Y%m%d'),
             "collection_number": parts_copy.pop(3),
             "collection_category": parts_copy.pop(3),
             "band": parts_copy.pop(3)[1:],
             "processing_level": parts_copy.pop(-1)
             }
        for idx, item in enumerate(self.lut):
            d.update({self.labels[idx]: self.lut[idx][parts_copy.pop(0)]})
        return d

    def stac_item(self, vrt):
        """https://github.com/sat-utils/sat-stac-landsat/blob/master/lambda/lambda_function.py"""
        if vrt.filename.startswith('/vsicurl/'):
            url = vrt.filename[9:]
        elif vrt.filename.startswith('/vsis3/'):
            splits = vrt.filename.split('/')
            bucket = splits.pop(0)
            key = '/'.join(splits)
            url = 'https://{}.s3.amazonaws.com/{}'.format(bucket, key)
        else:
            raise ValueError("Invalid vrt filename")

        root_url = os.path.dirname(url)
        file_root = '_'.join(os.path.splitext(os.path.split(vrt.filename)[-1])[0].split('_')[:-1])

        mdfile = file_root + '_MTL.txt'

        md = utils.get_metadata(os.path.join(root_url, mdfile))

        coordinates = [[
            [float(md['CORNER_UL_LON_PRODUCT']), float(md['CORNER_UL_LAT_PRODUCT'])],
            [float(md['CORNER_UR_LON_PRODUCT']), float(md['CORNER_UR_LAT_PRODUCT'])],
            [float(md['CORNER_LR_LON_PRODUCT']), float(md['CORNER_LR_LAT_PRODUCT'])],
            [float(md['CORNER_LL_LON_PRODUCT']), float(md['CORNER_LL_LAT_PRODUCT'])],
            [float(md['CORNER_UL_LON_PRODUCT']), float(md['CORNER_UL_LAT_PRODUCT'])]
        ]]

        lats = [c[1] for c in coordinates[0]]
        lons = [c[0] for c in coordinates[0]]
        bbox = [min(lons), min(lats), max(lons), max(lats)]

        assets = {
        'index': {'href': url},
        'thumbnail': {'href': file_root + '_thumb_large.jpg'},
        'B1': {'href': file_root + '_B1.TIF'},
        'B2': {'href': file_root + '_B2.TIF'},
        'B3': {'href': file_root + '_B3.TIF'},
        'B4': {'href': file_root + '_B4.TIF'},
        'B5': {'href': file_root + '_B5.TIF'},
        'B6': {'href': file_root + '_B6.TIF'},
        'B7': {'href': file_root + '_B7.TIF'},
        'B8': {'href': file_root + '_B8.TIF'},
        'B9': {'href': file_root + '_B9.TIF'},
        'B10': {'href': file_root + '_B10.TIF'},
        'B11': {'href': file_root + '_B11.TIF'},
        'ANG': {'href': file_root + '_ANG.txt'},
        'MTL': {'href': file_root + '_MTL.txt'},
        'BQA': {'href': file_root + '_BQA.TIF'},
        }

        props = {
            'collection': 'landsat-8-l1',
            'datetime': parse('%sT%s' % (md['DATE_ACQUIRED'], md['SCENE_CENTER_TIME'])).isoformat(),
            'eo:sun_azimuth': md['SUN_AZIMUTH'],
            'eo:sun_elevation': md['SUN_ELEVATION'],
            'eo:cloud_cover': md['CLOUD_COVER'],
            'landsat:product_id': md.get('LANDSAT_PRODUCT_ID', None),
            'landsat:scene_id': md['LANDSAT_SCENE_ID'],
            'landsat:processing_level': md['DATA_TYPE'],
            'landsat:path': md['WRS_PATH'],
            'landsat:row': md['WRS_ROW']
        }

        if 'UTM_ZONE' in md:
            center_lat = (min(lats) + max(lats)) / 2.0
            props['eo:epsg'] = int(('326' if center_lat > 0 else '327') + md['UTM_ZONE'])

        _item = {
            'type': 'Feature',
            'id': file_root,
            'bbox': bbox,
            'geometry': {
                'type': 'Polygon',
                'coordinates': coordinates
            },
            'properties': props,
            'assets': assets
        }

        return satstac.Item(_item)






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
                    {'04': 'Landsat4ARD',
                     '05': 'Landsat5ARD',
                     '07': 'Landsat7ARD',
                     '08': 'Landsat8ARD'
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


    def stac_item(self, vrt):
        #Build STAC item with metadata
        metadata = self.metadata()
        stac_item = stac.Item(vrt)
        stac_item['properties'] = metadata
        stac_item['assets'] = {'raw': {'href': vrt.filename}}

        #Create stat-stac item
        item_path = '${horizontal_tile_number}/${vertical_tile_number}/${acquisition_date}'
        satstac_item = satstac.Item(stac_item)
        return satstac_item

    def stac_path(self):
        return '${horizontal_tile_number}/${vertical_tile_number}/${acquisition_date}'