class MahjongTable:
    def __init__(self):
        self.plain_table = set()
        self.eye_table = set()
        self._build_tables()
        print(f"建表完成: plain_table容量 {len(self.plain_table)}, eye_table容量 {len(self.eye_table)} (内存极速查表版)")

    def _build_tables(self):
        """
        在类初始化时运行一次 DFS，动态生成所有单花色（9张牌）的合法组合。
        彻底摆脱外部表文件依赖，速度极快。
        """
        def dfs(arr):
            t = tuple(arr)
            # 如果已经记录过，直接剪枝
            if t in self.plain_table:
                return
            self.plain_table.add(t)

            # 基础牌型最多 4 组（12张牌），超过就不能再加了
            if sum(arr) >= 12:
                return

            for i in range(9):
                # 1. 尝试加刻子 (3张一样)，前提是加完不能超过 4 张
                if arr[i] <= 1:
                    arr[i] += 3
                    dfs(arr)
                    arr[i] -= 3

                # 2. 尝试加顺子 (前提是 i <= 6 且每张牌都不能超过 3 张)
                if i <= 6 and arr[i] <= 3 and arr[i+1] <= 3 and arr[i+2] <= 3:
                    arr[i] += 1
                    arr[i+1] += 1
                    arr[i+2] += 1
                    dfs(arr)
                    arr[i] -= 1
                    arr[i+1] -= 1
                    arr[i+2] -= 1

        # 第一步：生成所有不带将牌的合法基础组合 (plain_table)
        dfs([0] * 9)

        # 第二步：遍历 plain_table，为每个基础组合加上一对将牌，生成带有眼睛的组合 (eye_table)
        for plain in self.plain_table:
            for i in range(9):
                if plain[i] <= 2:  # 保证加上将牌后该张牌不超过 4 张
                    eye = list(plain)
                    eye[i] += 2
                    self.eye_table.add(tuple(eye))

    def can_hu(self, hand_array):
        """
        核心接口不变：O(1) 极速查表判断胡牌
        :param hand_array: 长度为 27 的一维数组
        """
        if sum(hand_array) == 14:
            # 只要所有的牌的数量都是偶数（0, 2, 4），那必然是七对（包含豪华七对的4张）
            is_seven_pairs = True
            for count in hand_array:
                if count % 2 != 0:
                    is_seven_pairs = False
                    break
            
            if is_seven_pairs:
                return True


        # 将 27 张牌直接切片成 万、条、筒 3 个独立的单花色元组
        w = tuple(hand_array[0:9])
        t = tuple(hand_array[9:18])
        b = tuple(hand_array[18:27])

        # 胡牌条件极其简单暴力：
        # 必须有且仅有一个花色带将牌 (存在于 eye_table)
        # 另外两个花色必须是不带将的合法组合 (存在于 plain_table，包括全空的 (0,0,0,0,0,0,0,0,0))

        # 情况1：万字牌做将
        if w in self.eye_table and t in self.plain_table and b in self.plain_table:
            return True
        # 情况2：条字牌做将
        if t in self.eye_table and w in self.plain_table and b in self.plain_table:
            return True
        # 情况3：筒字牌做将
        if b in self.eye_table and w in self.plain_table and t in self.plain_table:
            return True

        return False
