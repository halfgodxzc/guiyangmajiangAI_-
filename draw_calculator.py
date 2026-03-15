class ShantenCalculator:
    def __init__(self, suit_analyzer):
        self.analyzer = suit_analyzer

    def get_shanten(self, hand_array):
        """
        计算全局向听数 (拼图逻辑)
        手牌长度27，切成三个长度为9的数组分别算
        """
        w_arr = hand_array[0:9]
        t_arr = hand_array[9:18]
        b_arr = hand_array[18:27]

        # 查表拿到万、条、筒的 (m, d) 成绩单
        w_res = self.analyzer.evaluate_suit(w_arr)
        t_res = self.analyzer.evaluate_suit(t_arr)
        b_res = self.analyzer.evaluate_suit(b_arr)

        min_shanten = 8 # 最差情况是8向听

        # 遍历 4 种假设：谁来提供将牌？(0:没人提供, 1:万, 2:条, 3:筒)
        for jiang_suit in range(4):
            # 拿到对应的成绩
            mw, dw = (w_res['p1'] if jiang_suit == 1 else w_res['p0'])
            mt, dt = (t_res['p1'] if jiang_suit == 2 else t_res['p0'])
            mb, db = (b_res['p1'] if jiang_suit == 3 else b_res['p0'])

            # 如果某一家尝试做将牌，但其实凑不出对子(返回了-1)，就跳过这种假设
            if mw == -1 or mt == -1 or mb == -1:
                continue

            total_m = mw + mt + mb
            total_d = dw + dt + db
            has_jiang = 1 if jiang_suit > 0 else 0

            # 核心规则：搭子超载处理 (m + d 最多只能是 4)
            if total_m + total_d > 4:
                total_d = 4 - total_m  # 超过的搭子是废的，不减向听数

            # 套入终极公式
            current_s = 8 - 2 * total_m - total_d - has_jiang
            
            if current_s < min_shanten:
                min_shanten = current_s

        return min_shanten


    def get_effective_draws(self, hand_array):
        """
        进张测算器：遍历 27 种牌，看看摸谁能让向听数下降
        """
        current_shanten = self.get_shanten(hand_array)
        effective_draws = {} # 格式: {牌的索引: 剩余张数}
        total_effective_count = 0

        for i in range(27):
            # 只有外面还有这张牌，才能去摸
            if hand_array[i] < 4:
                # 1. 模拟摸牌
                hand_array[i] += 1
                
                # 2. 算新的向听数
                new_shanten = self.get_shanten(hand_array)
                
                # 3. 如果向听数下降了，说明这牌有用！
                if new_shanten < current_shanten:
                    left_count = 4 - (hand_array[i] - 1) # 算算外面还有几张
                    effective_draws[i] = left_count
                    total_effective_count += left_count
                
                # 4. 把牌退回去，测试下一张
                hand_array[i] -= 1

        return effective_draws, total_effective_count
