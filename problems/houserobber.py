def find_max_rob_value(nums: list[int]) -> int:
    if len(nums) == 0:
        return 0
    if len(nums) == 1:
        return nums[0]
    sol = [0] * (len(nums) + 1)
    sol[-2] = nums[-1]
    i = len(nums) - 2
    while i >= 0:
        sol[i] = max(nums[i] + sol[i+2], sol[i+1])
        i -= 1
    return sol[0]

assert(find_max_rob_value([5]) == 5)
assert(find_max_rob_value([5, 9]) == 9)
assert(find_max_rob_value([2, 7, 3]) == 7)
