class TileMapper:
    def __init__(self):
        # 贵阳麻将只有万、条、筒，共 27 种牌
        self.labels = [
            '1c', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c',
            '1b', '2b', '3b', '4b', '5b', '6b', '7b', '8b', '9b',
            '1d', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d'
        ]
        self.name_map = {'c': '万', 'b': '条', 'd': '筒'}

    def yolo_to_array(self, yolo_output):
        arr = [0] * 27
        for tile in yolo_output:
            if tile in self.labels:
                arr[self.labels.index(tile)] += 1
        return arr

    def get_name(self, index):
        label = self.labels[index]
        return label[0] + self.name_map[label[1]]

    def array_to_names(self, hand_array):
        names = []
        for i in range(27):
            if hand_array[i] > 0:
                names.extend([self.get_name(i)] * hand_array[i])
        return names
