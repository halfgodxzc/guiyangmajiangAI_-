import check_ting

def get_best_discards(hand_array, table):
    best_strategies = []
    max_ting_count = 0

    for i in range(27):
        if hand_array[i] > 0:
            hand_array[i] -= 1
            
            ting_indices = check_ting.get_ting_tiles(hand_array, table)
            ting_count = len(ting_indices)
            
            if ting_count > 0:
                if ting_count > max_ting_count:
                    max_ting_count = ting_count
                    best_strategies = [(i, ting_indices)]
                elif ting_count == max_ting_count:
                    best_strategies.append((i, ting_indices))
            
            hand_array[i] += 1

    return best_strategies

def get_1_shanten_discards(hand_array, table):
    """
    【第 1 层逻辑：一向听预测】
    如果当前怎么打都听不了，往后看一步：
    寻找打出哪张牌后，能带来最多的“有效进张”(摸到后就能听牌的牌)。
    """
    best_strategies = []
    max_effective_draws = 0

    # 1. 第一层循环：我该打哪张牌？
    for discard_idx in range(27):
        if hand_array[discard_idx] > 0:
            hand_array[discard_idx] -= 1  # 假设打出这张牌 (剩 13 张)

            effective_draws = [] # 记录打出这张牌后，摸哪些牌能听

            # 2. 第二层循环：下一轮我可能摸到什么牌？
            for draw_idx in range(27):
                if hand_array[draw_idx] < 4:
                    hand_array[draw_idx] += 1  # 假设摸到了这张牌 (变回 14 张)

                    # 3. 第三层循环：摸到这张牌后，我能听牌吗？(判断是否达到了 0 向听)
                    # (只需要能听就行，哪怕只听 1 张)
                    can_ting_after_draw = False
                    for next_discard in range(27):
                        if hand_array[next_discard] > 0:
                            hand_array[next_discard] -= 1 # 再次尝试打出

                            # 调用底层的查表法，看看剩下13张能不能听牌
                            if len(check_ting.get_ting_tiles(hand_array, table)) > 0:
                                can_ting_after_draw = True
                                hand_array[next_discard] += 1
                                break # 只要存在一种打法能听牌，说明这个 draw_idx 就是有效进张！

                            hand_array[next_discard] += 1

                    if can_ting_after_draw:
                        effective_draws.append(draw_idx)

                    hand_array[draw_idx] -= 1  # 把摸的牌退回去

            # 判断这个打法带来的进张面够不够宽
            draws_count = len(effective_draws)
            if draws_count > 0:
                if draws_count > max_effective_draws:
                    max_effective_draws = draws_count
                    best_strategies = [(discard_idx, effective_draws)]
                elif draws_count == max_effective_draws:
                    best_strategies.append((discard_idx, effective_draws))

            hand_array[discard_idx] += 1  # 把打出的牌捡回来

    return best_strategies
