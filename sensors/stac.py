import os

class Item(dict):

    def __init__(self, vrt):
        super(dict).__init__()
        self['type'] = 'Feature'
        self['id'] = os.path.splitext(os.path.split(vrt.filename)[-1])[0]
        self['bbox'] = [vrt.extent[0], vrt.extent[2], vrt.extent[1], vrt.extent[3]]
        self['geometry'] = {
            'type': 'Polygon',
            'coordinates': [[
                [vrt.extent[0], vrt.extent[3]],
                [vrt.extent[1], vrt.extent[3]],
                [vrt.extent[1], vrt.extent[2]],
                [vrt.extent[0], vrt.extent[2]],
                [vrt.extent[0], vrt.extent[3]]
                 ]]
        }