class Acronym {

    private String acro = "";
    
    Acronym(String phrase) {
        
        for (int i=0; i<phrase.length(); i++)
            {
                char c = ' ';
                
                if (i==0 && Character.isUpperCase(phrase.charAt(i)))
                    c = phrase.charAt(i);

                else if (phrase.charAt(i) == '-')
                {
                    if (phrase.charAt(i+1) == ' ')
                    {
                        c = phrase.charAt(i+2);
                        i++;
                        i++;
                    }

                    else 
                    {
                        c = phrase.charAt(i+1);
                        i++;
                    }
                }

                else if (phrase.charAt(i) == ' ' && phrase.charAt(i+1) != '-' && phrase.charAt(i+1) != '_')
                {
                    c = phrase.charAt(i+1);
                    i++;
                }

                else if (phrase.charAt(i) == '_' && phrase.charAt(i+1) != ' ')
                {
                    c = phrase.charAt(i+1);
                    i++;
                }

                if (c != ' ')
                    acro = acro + Character.toString(c);
            }
    }

    String get() {
        return this.acro.toUpperCase();
    }

}
