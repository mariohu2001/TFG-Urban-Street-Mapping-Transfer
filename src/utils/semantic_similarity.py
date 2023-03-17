import csv
import textdistance as td
from node_data.neo4j_data.node_stats import *
import itertools
from functools import partial
import Levenshtein

# Formato de csv
# Amenity | Frecuencia de la Amenity | Amenity más próxima | Medida de similitud


def comp_func(function, am1, am2):
    if am1 == am2:
        return 0

    return function(am1, am2)


def amenity_similarity(result_path: str):
    amenity_frequency: dict = dict(get_n_of_nodes_by_appareance())
    amenities = amenity_frequency.keys()

    text_distance_funcs: list = [td.jaro_winkler.normalized_similarity,
                                 td.damerau_levenshtein.normalized_similarity, td.lcsstr.normalized_similarity, td.lcsseq.normalized_similarity]
    csv_values = [["Amenity", "Frequency", "Jaro Winkler", "Similarity", "Frequency",
                   "Damerau Levenshtein", "Similarity", "Frequency", "LCSSTR", "Similarity", "Frequency","LCSSEQ", "Similarity", "Frequency"]]

    for am1 in amenities:
        amenity_results = [am1, amenity_frequency[am1]]

        for func in text_distance_funcs:
            sim = max(amenities, key=partial(comp_func, func, am1))
            amenity_results.append(sim)
            amenity_results.append(func(am1,sim))
            amenity_results.append(amenity_frequency[sim])

        csv_values.append(amenity_results)

    csv_file = open(result_path, "w", encoding="UTF=8", newline='')
    csv_writer = csv.writer(csv_file)

    csv_writer.writerows(csv_values)

    for row in csv_values[1:]:
        if row[3] >= 0.95:
            print("Jaro_Winkler",row[0],"->",row[2])
        if row[6] >= 0.85:
            print("Damerau Levenshtein",row[0],"->",row[5])
        if row[9] >= 0.95:
            print("LCSSTR",row[0],"->",row[8])
        if row[12] >= 0.95:
            print("LCSSEQ",row[0],"->",row[11])

    csv_file.close()
