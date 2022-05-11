"""
Handling the definition of clusters
"""

from hysut.utils.tools import read_range_function, type_consistency_check


def check_years_clusters(clusters, years):

    """Retruns the corrected form of clusters definiton with errors

    Parameters
    ----------
    clusters : dict
        clusters definition dict e.g.
        {
            'cluster_1' : [2020,2021,2022]
            "cluster_2' : 'range(2023,2030)'
        }
    Returns
    -------
    dict
        {
            "errors" : List of errors,
            "time_cluster" : dict of clusters (keys represent the name of cluster and values the list of years)
        }
    """
    errors = []
    time_clusters = {}

    for cluster_name, cluster_years in clusters.items():

        if isinstance(cluster_years, list):
            cluster = cluster_years

        elif isinstance(cluster_years, str) and "range" in cluster_years:
            rng = read_range_function(
                range_data=cluster_years, item=f"clusters: {cluster_name}"
            )
            cluster = rng["data"]
            errors.extend(rng["error"])

        else:
            errors.append(
                "A cluster can be defined only as a list of integers or a range function"
                f"(error in the definition of {cluster_name}."
            )
            continue

        diff = set(cluster).difference(years)
        if diff:
            errors.append(
                f"cluster '{cluster_name}' has years ({diff}) that are not valid years."
            )
        else:
            time_clusters[cluster_name] = sorted(set(cluster))

    return {"errors": errors, "time_clusters": time_clusters}


def add_missing_years_to_cluster(clusters, years):
    """Checks if for a given set of cluster, specific years are missed

    Parameters
    ----------
    cluster : dict
        _description_
    years : list
        _description_

    Returns
    -------
    list
        clusters + years that are not covered by clusters.
        e.g.

        years = [2021,2022,2023,2024]
        clusters = {"cls1": [2021],"cls2": [2022,2023]}

        function output will be:
        ["cls1","cls2",2024]

    """

    giveng_years_by_clusters = [
        year for cluster in clusters.values() for year in cluster
    ]
    missing_years = list(set(years).difference(set(giveng_years_by_clusters)))

    return [*clusters] + sorted(missing_years)
