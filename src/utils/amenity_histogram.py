
import matplotlib.pyplot as plt
import csv
from node_data.neo4j_data import node_stats


data_path = "../data/csv"
plot_path = "../plots"


def city_amenity_histogram(city: str, lim_sup: int = None):

    amenity_tags = (val[0] for val in node_stats.get_amenity_tags(city))
    count_dict = dict()
    for tag in amenity_tags:
        result = node_stats.get_amenity_numbers_city(tag,city)
        count_dict[tag] = result
    count_dict : dict = dict(
        sorted(count_dict.items(), key=lambda x: x[1], reverse=True))
    if count_dict.keys().__contains__("Place"):
        del count_dict["Place"]
    # less_results = session.execute_read(get_n_of_nodes_by_appareance,min_app)
    fig = plt.figure(figsize=(16, 9), dpi=1200)
    # fig.tight_layout()

    plt.rcParams['figure.dpi'] = 500
    plt.rcParams['savefig.dpi'] = 500
    plt.rcParams["figure.figsize"] = [17.00, 13.50]
    plt.rcParams["figure.autolayout"] = True
    count_keys = list(count_dict.keys())
    count_values = list(count_dict.values())
    if lim_sup is None:
        plt.bar(count_keys, count_values,
                color="red", align="center")
    else:

        plt.bar(count_keys[-lim_sup:], list(count_dict.values())[-lim_sup:],
                color="red", align="center")

    plt.xlabel("Amenity")
    plt.ylabel("Nº de nodos")
    plt.xticks(rotation=90, ha="right", fontsize=5)
    # plt.tight_layout(h_pad=0.01, w_pad=1.5)
    plt.title(f"Nº de apariciones de cada amenity en {city}")

    # plt.autoscale()
    # plt.xscale()
    if lim_sup is None:
        plot_name = f"{plot_path}/BarAmenity-{city}.png"
    else:
        plot_name = f"{plot_path}/BarAmenity-{city}"+str(lim_sup)+".png"
        
    plt.savefig(plot_name, bbox_inches='tight', dpi=500)
    # plt.figure()
    # plt.rcParams['figure.dpi'] = 500
    # plt.rcParams['savefig.dpi'] = 500
    # plt.rcParams["figure.figsize"] = [17.00, 13.50]
    # plt.rcParams["figure.autolayout"] = True
    # plt.xlabel("Amenity")
    # plt.ylabel("Nº de nodos")
    # plt.xticks(rotation=90, ha="right", fontsize=5)
    # plt.title("Nº de apariciones de cada amenity")
    # plt.bar([lr[0] for lr in less_results], [lr[1] for lr in less_results], color="red", align="center")
    # plt.savefig(f"LessAmenity-{min_app}.png", bbox_inches='tight', dpi=500)
    # plt.show()
    write_amenities_to_csv(city, count_dict)


def write_amenities_to_csv(city: str, stats_dict: dict):
    with open(f"{data_path}/number_of_amenities-{city}.csv", "w", newline="", encoding="UTF-8") as writer:
        csv_writer = csv.writer(writer)

        csv_writer.writerow(["Amenity", "N de apariciones"])
        # writer.write("Amenity: N de apariciones")
        for k, v in stats_dict.items():
            # writer.write(f"{k}: {v}")
            csv_writer.writerow([k, v])
