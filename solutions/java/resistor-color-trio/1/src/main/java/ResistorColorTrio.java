import java.util.Arrays;
import java.util.List;

class ResistorColorTrio {

    private final List<String> colorsList = Arrays.asList(
        "black", "brown", "red", "orange", "yellow", 
        "green", "blue", "violet", "grey", "white"
    );

    String label(String[] colors) {
        int firstDigit = colorsList.indexOf(colors[0]);
        int secondDigit = colorsList.indexOf(colors[1]);
        int exponent = colorsList.indexOf(colors[2]);

        long mainValue = (firstDigit * 10L + secondDigit);
        long rawValue = mainValue * (long) Math.pow(10, exponent);

        if (rawValue >= 1_000_000_000) {
            return (rawValue / 1_000_000_000) + " gigaohms";
        } else if (rawValue >= 1_000_000) {
            return (rawValue / 1_000_000) + " megaohms";
        } else if (rawValue >= 1_000) {
            return (rawValue / 1_000) + " kiloohms";
        } else {
            return rawValue + " ohms";
        }
    }
}