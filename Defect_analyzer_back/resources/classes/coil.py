class Coil:
    areas = {}

    def __init__(self, id, date, time, path, image_list):
        self.id = id
        self.date = date
        self.time = time
        self.path = path
        self.image_list = image_list

    def set_areas_from_dict(self, areas_dict):
        self.areas = areas_dict

    def get_areas(self):
        return self.areas
