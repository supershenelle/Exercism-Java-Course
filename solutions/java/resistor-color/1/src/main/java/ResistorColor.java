class ResistorColor {
    private static final String col[] = {"black", "brown", "red", "orange", "yellow", "green", "blue", "violet", "grey", "white"};
    
    int colorCode(String color) {
        int res = -1;
        for (int i=0; i<col.length; i++)
            {
                if (col[i] == color)
                res = i;
            }

        return res;
    }

    String[] colors() {
        return col;
    }
}
