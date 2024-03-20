import pandas as pd

from sys import argv
from BCBio import GFF

from metrics.string import get_protein_links, predict_string
from metrics.intergenic_distances import calculate_intergenic_dist, predict_operon_inter_dist


def parse_gff(path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses file.gff from given path.
    :param path: path to file
    :return: pd.DataFrame with the columns necessary for subsequent analysis; taxon_id for species
    """
    taxon_id = ""
    info = []
    limit_info = dict(gff_type=["gene"])

    handle = open(path)
    for record in GFF.parse(handle, limit_info=limit_info):
        taxon_id = record.annotations["species"][0].split("=")[-1]  # FIXME
        for feature in record.features:
            info.append(
                [
                    record.id,
                    int(feature.location.start) + 1,
                    int(feature.location.end),
                    "+" if feature.location.strand == 1 else "-",
                    "".join(feature.qualifiers["gene"]),
                    feature.id.split("-")[1],
                ]
            )
    handle.close()

    columns = ["contig", "start", "end", "strand", "gene_name", "locus_name"]
    parsed_gff = pd.DataFrame(data=info, columns=columns)

    return parsed_gff, taxon_id


if __name__ == "__main__":
    _, path_to_gff, output_filename = argv
    parsed_gff_file, species_id = parse_gff(path_to_gff)
    parsed_gff_file = pd.read_csv()
    protein_links = get_protein_links(species_id)
    string_scores_df = predict_string(parsed_gff_file, protein_links)
    inter_dist_df = calculate_intergenic_dist(parsed_gff_file)
    inter_dist_pred = predict_operon_inter_dist(inter_dist_df)
    string_scores_df.to_csv(
        output_filename,
        sep="\t",
        encoding="utf-8",
    )