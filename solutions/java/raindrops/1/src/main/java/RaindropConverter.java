class RaindropConverter {

    String convert(int number) {
        String ans = "";

        if (number % 3 == 0)
            ans = ans + "Pling";

        if (number % 5 == 0)
            ans = ans + "Plang";

        if (number % 7 == 0)
            ans = ans + "Plong";

        else if (number % 3 != 0 && number % 5 != 0 && number % 7 != 0)
            ans = Integer.toString(number);

           return ans;
    }
}
