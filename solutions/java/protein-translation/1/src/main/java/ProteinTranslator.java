import java.util.ArrayList;
import java.util.List;

class ProteinTranslator {

    List<String> translate(String rnaSequence) {
        List<String> proteins = new ArrayList<>();

        for (int i = 0; i < rnaSequence.length(); i += 3) {
            if (i + 3 > rnaSequence.length()) {
                throw new IllegalArgumentException("Invalid codon");
            }

            String codon = rnaSequence.substring(i, i + 3);

            switch (codon) {
                case "AUG":
                    proteins.add("Methionine");
                    break;
                case "UUU":
                case "UUC":
                    proteins.add("Phenylalanine");
                    break;
                case "UUA":
                case "UUG":
                    proteins.add("Leucine");
                    break;
                case "UCU":
                case "UCC":
                case "UCA":
                case "UCG":
                    proteins.add("Serine");
                    break;
                case "UAU":
                case "UAC":
                    proteins.add("Tyrosine");
                    break;
                case "UGU":
                case "UGC":
                    proteins.add("Cysteine");
                    break;
                case "UGG":
                    proteins.add("Tryptophan");
                    break;
                case "UAA":
                case "UAG":
                case "UGA":
                    return proteins;
                default:
                    throw new IllegalArgumentException("Invalid codon");
            }
        }

        return proteins;
    }
}