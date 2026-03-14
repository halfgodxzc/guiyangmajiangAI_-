def get_ting_tiles(hand_array, table):
    ting_list = []
    # 严格遍历 27 种牌
    for i in range(27):
        if hand_array[i] < 4:
            hand_array[i] += 1
            if table.can_hu(hand_array):
                ting_list.append(i)
            hand_array[i] -= 1
            
    return ting_list
