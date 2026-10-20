class Fighter {

    boolean isVulnerable() {
        return true;
    }

    int getDamagePoints(Fighter fighter) {
        return 1;
    }
}

// TODO: define the Warrior class
class Warrior extends Fighter {

    public String toString() {
        return "Fighter is a Warrior";
    }

    @Override
    boolean isVulnerable() {
        return false;
    }

    @Override
    int getDamagePoints(Fighter fighter) {
        if (fighter.isVulnerable())
            return 10;

        else
            return 6;
    }
}
// TODO: define the Wizard class
class Wizard extends Fighter {
    private boolean spell = false;
    
    public String toString() {
        return "Fighter is a Wizard";
    }

    public void prepareSpell(){
        spell = true;
    }

    public boolean isVulnerable(){
        return !spell;
    }

    public int getDamagePoints(Fighter fighter){
        if (spell){
            return 12;
        }

        else
            return 3;
    }
}
