class ReverseString {

    String reverse(String inputString) {
        StringBuilder reversed = new StringBuilder(inputString);
        reversed.reverse();
        return reversed.toString();
    }
  
}
