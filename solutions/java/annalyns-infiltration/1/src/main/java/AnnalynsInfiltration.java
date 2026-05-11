class AnnalynsInfiltration {
    public static boolean canFastAttack(boolean knightIsAwake) {
        if (knightIsAwake == true)
            return false;

        else
            return true;
    }

    public static boolean canSpy(boolean knightIsAwake, boolean archerIsAwake, boolean prisonerIsAwake) {
        if (knightIsAwake == true || archerIsAwake == true || prisonerIsAwake == true)
            return true;

        else
            return false;
    }

    public static boolean canSignalPrisoner(boolean archerIsAwake, boolean prisonerIsAwake) {
        if (archerIsAwake == false && prisonerIsAwake == true)
            return true;

        else
            return false;
    }

    public static boolean canFreePrisoner(boolean knightIsAwake, boolean archerIsAwake, boolean prisonerIsAwake, boolean petDogIsPresent) {
        if (archerIsAwake == false && petDogIsPresent == true)
            return true;

        else if (petDogIsPresent == false && canSignalPrisoner(archerIsAwake, prisonerIsAwake) && knightIsAwake == false)
            return true;

        else
            return false;
    }
}
