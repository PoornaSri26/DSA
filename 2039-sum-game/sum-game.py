class Solution:
    def sumGame(self, num: str) -> bool:
        n = len(num)
        h = n // 2

        left = right = 0
        lq = rq = 0

        for i, c in enumerate(num):
            if c == '?':
                if i < h:
                    lq += 1
                else:
                    rq += 1
            elif i < h:
                left += int(c)
            else:
                right += int(c)

        # Equal number of '?' on both sides
        if lq == rq:
            return left != right

        # Bob can win only if the known difference can be
        # exactly compensated by the extra '?' side.
        diff = left - right
        qdiff = lq - rq

        return diff * 2 != -9 * qdiff