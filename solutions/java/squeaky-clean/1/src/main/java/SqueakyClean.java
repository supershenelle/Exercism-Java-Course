import java.util.Set;

class SqueakyClean {
    static String clean(String identifier) {
        
        StringBuilder newString = new StringBuilder();
        boolean capitalize = false;
        
        for (char ch: identifier.toCharArray())
            {
                if (Character.isLetter(ch))
                {
                    if (capitalize == true)
                    {
                        newString.append(Character.toUpperCase(ch));
                        capitalize = false;
                    }

                    else
                         newString.append(ch);
                }
                
                if (Character.isWhitespace(ch))
                    newString.append('_');

                if (ch == '-')
                    capitalize = true;

                if (Set.of('4', '3', '0', '1', '7').contains(ch))
                {
                    switch (ch)
                        {
                            case '4': newString.append('a'); break;
                            case '3': newString.append('e'); break;
                            case '0': newString.append('o'); break;
                            case '1': newString.append('l'); break;
                            case '7': newString.append('t'); break;
                        }
                } 
            }
        return newString.toString();
    }
}
