import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

class DnDCharacter {

    private final int strength;
    private final int dexterity;
    private final int constitution;
    private final int intelligence;
    private final int wisdom;
    private final int charisma;
    private final int hitpoints;

    public DnDCharacter() {
        this.strength = ability(rollDice());
        this.dexterity = ability(rollDice());
        this.constitution = ability(rollDice());
        this.intelligence = ability(rollDice());
        this.wisdom = ability(rollDice());
        this.charisma = ability(rollDice());
        this.hitpoints = 10 + modifier(this.constitution);
    }

    int ability(List<Integer> scores) {
        List<Integer> copy = new ArrayList<>(scores);
        Collections.sort(copy);
        // Sum the top 3 highest rolls (indexes 1, 2, and 3 after sorting)
        return copy.get(1) + copy.get(2) + copy.get(3);
    }

    List<Integer> rollDice() {
        Random random = new Random();
        List<Integer> dice = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            dice.add(random.nextInt(6) + 1); // Generates a number between 1 and 6
        }
        return dice;
    }

    int modifier(int input) {
        // Math.floorDiv ensures proper rounding down for odd negative values
        return Math.floorDiv(input - 10, 2);
    }

    int getStrength() {
        return strength;
    }

    int getDexterity() {
        return dexterity;
    }

    int getConstitution() {
        return constitution;
    }

    int getIntelligence() {
        return intelligence;
    }

    int getWisdom() {
        return wisdom;
    }

    int getCharisma() {
        return charisma;
    }

    int getHitpoints() {
        return hitpoints;
    }
}
