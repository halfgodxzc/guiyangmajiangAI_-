class TileMapper:
    def __init__(self):
        # 贵阳麻将只有万、条、筒，共 27 种牌
        self.labels = [
            '1w', '2w', '3w', '4w', '5w', '6w', '7w', '8w', '9w',
            '1t', '2t', '3t', '4t', '5t', '6t', '7t', '8t', '9t',
            '1b', '2b', '3b', '4b', '5b', '6b', '7b', '8b', '9b'
        ]
        self.name_map = {'w': '万', 't': '条', 'b': '筒'}

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
