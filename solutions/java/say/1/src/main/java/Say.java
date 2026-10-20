public class Say {
    private static final String[] ONES = {"", "one", "two", "three", "four", "five", "six",
        "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"};
    private static final String[] TENS = {"", "", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety"};

    public String say(long number) {
        if (number < 0 || number > 999_999_999_999L)
        throw new IllegalArgumentException("input out of range");
        
        if (number == 0) return "zero";
        if (number < 20) return ONES[(int) number];
        if (number < 100) return TENS[(int) number / 10] + (number % 10 > 0 ? "-" + ONES[(int) number % 10] : "");
        if (number < 1_000) return say(number / 100) + " hundred" + (number % 100 > 0 ? " " + say(number % 100) : "");
        if (number < 1_000_000) return say(number / 1_000) + " thousand" + (number % 1_000 > 0 ? " " + say(number % 1_000) : "");
        if (number < 1_000_000_000) return say(number / 1_000_000) + " million" + (number % 1_000_000 > 0 ? " " + say(number % 1_000_000) : "");
        return say(number / 1_000_000_000) + " billion" + (number % 1_000_000_000 > 0 ? " " + say(number % 1_000_000_000) : "");
    }
}