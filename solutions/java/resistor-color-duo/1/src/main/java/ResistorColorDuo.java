import java.util.List;

class ResistorColorDuo {

    private static final List<String> COLORS = List.of(
        "black", "brown", "red", "orange", "yellow",
        "green", "blue", "violet", "grey", "white"
    );

    int value(String[] colors) {
        int firstDigit = COLORS.indexOf(colors[0]);
        int secondDigit = COLORS.indexOf(colors[1]);

        return firstDigit * 10 + secondDigit;
    }
}
