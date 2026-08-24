from typing import List

class Solution:
    def stoneGameVIII(self, stones: List[int]) -> int:
        n = len(stones)

        # Prefix sums
        prefix = [0] * n
        prefix[0] = stones[0]

        for i in range(1, n):
            prefix[i] = prefix[i - 1] + stones[i]

        # Start with the only possible state when 2 stones remain
        ans = prefix[n - 1]

        for i in range(n - 2, 0, -1):
            ans = max(prefix[i] - ans, ans)

        return ans