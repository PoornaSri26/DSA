class Solution:
    def missingInteger(self, nums):
        # Find sum of longest sequential prefix
        total = nums[0]

        for i in range(1, len(nums)):
            if nums[i] == nums[i - 1] + 1:
                total += nums[i]
            else:
                break

        # Store all numbers for O(1) average lookup
        seen = set(nums)

        # Find smallest missing number >= total
        while total in seen:
            total += 1

        return total