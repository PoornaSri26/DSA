class Solution {
public:
    bool isPalindrome(int x) {

        // Negative numbers are never palindromes
        if (x < 0)
            return false;

        // Numbers ending in 0 are not palindromes,
        // except 0 itself
        if (x % 10 == 0 && x != 0)
            return false;

        int reversedHalf = 0;

        // Reverse only half of the digits
        while (x > reversedHalf) {
            int digit = x % 10;

            reversedHalf = reversedHalf * 10 + digit;

            x /= 10;
        }

        // Even number of digits
        // Example: 1221
        //
        // x = 12
        // reversedHalf = 12
        if (x == reversedHalf)
            return true;

        // Odd number of digits
        // Example: 12321
        //
        // x = 12
        // reversedHalf = 123
        //
        // Remove the middle digit: 123 / 10 = 12
        return x == reversedHalf / 10;
    }
};