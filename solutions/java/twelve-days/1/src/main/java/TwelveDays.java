import java.util.stream.Collectors;
import java.util.stream.IntStream;

class TwelveDays {

    private static final String[] ORDINA_DAYS = {
        "first", "second", "third", "fourth", "fifth", "sixth",
        "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"
    };

    private static final String[] GIFTS = {
        "a Partridge in a Pear Tree.",
        "two Turtle Doves, ",
        "three French Hens, ",
        "four Calling Birds, ",
        "five Gold Rings, ",
        "six Geese-a-Laying, ",
        "seven Swans-a-Swimming, ",
        "eight Maids-a-Milking, ",
        "nine Ladies Dancing, ",
        "ten Lords-a-Leaping, ",
        "eleven Pipers Piping, ",
        "twelve Drummers Drumming, "
    };

    String verse(int verseNumber) {
        StringBuilder builder = new StringBuilder();
        builder.append(String.format("On the %s day of Christmas my true love gave to me: ", ORDINA_DAYS[verseNumber - 1]));

        for (int i = verseNumber - 1; i >= 0; i--) {
            if (verseNumber > 1 && i == 0) {
                builder.append("and ");
            }
            builder.append(GIFTS[i]);
        }

        builder.append("\n");
        return builder.toString();
    }

    String verses(int startVerse, int endVerse) {
        return IntStream.rangeClosed(startVerse, endVerse)
                .mapToObj(this::verse)
                .collect(Collectors.joining("\n"));
    }

    String sing() {
        return verses(1, 12);
    }
}