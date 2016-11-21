# -*- coding: utf-8 -*-

"""
Implement the two permutation-based methods `SwapLocations` and
`ReachLocations` described in `Anonymization of trajectory data
<https://www.unece.org/fileadmin/DAM/stats/documents/ece/ces/ge.46/2011/32_Domingo-Trujillo.pdf>`_
"""

def permutate_swap_locations(cardinality=1.0, *cluster):
    """
    This method needs sets of trajectories as clusters, partitioned using
    microaggregation.  Limit yourself to clustering algorithms which try
    to minimize the sum of the intra-cluster distances.

    The cardinality of each cluster must be approximately k, with k an input
    parameter, here: `cardinality`; if the number of trajectories in the
    `cluster` is not a multiple of k, one or more clusters must absorb the up to
    k - 1 remaining trajectories, hence those clusters will have cardinalities
    between k + 1 and 2k − 1.  The purpose of setting k as the cluster size is
    to fulfill trajectory k-anonymity.

    The SwapLocations function begins with a random trajectory T in C.  The
    function attempts to cluster each unswapped triple λ in T with another
    k − 1 unswapped triples belonging to different trajectories such that:

        1) the timestamps of these triples differ by no more than a time
        threshold Rt from the timestamp of λ; and

        2) the spatial coordinates differ by no more than a space threshold Rs.

    If no k − 1 suitable triples can be found that can be clustered with λ,
    then λ is removed; otherwise, random swaps of triples are performed within
    the formed cluster.  As a result, at least one of the trajectories returned
    by this function has all its triples swapped.
    """
    size     = len(cluster)
    overhead = (size % cardinality)
    if overhead is 0:
        overhead = []
    else:
        overhead = cluster[-1 * overhead:]
        cluster  = cluster[0:-1 * overhead]

    # ... do something with the cluster here ...
    raise NotImplementedError

    return (cluster, overhead)

def permutate_reachable_locations():
    """
    This method takes reachability constraints into account: from a given
    location, only those locations at a distance below a threshold following a
    path in an underlying graph (e.g., urban pattern or road network) are
    considered to be directly reachable.  Enforcing such reachability
    constraints while requiring full trajectory k-anonymity would result in a
    lot of original locations being discarded.  To avoid this, trajectory
    k-anonymity is changed by another useful privacy definition: location
    k-diversity.

    Computationally, this means that trajectories are not microaggregated into
    clusters of size k.  Instead, each location is k-anonymized independently
    using the entire set of locations of all trajectories.  To do so, a cluster
    Cλ of “unswapped” locations is created around a given location λ,
    i.e. λ ∈ Cλ.  The cluster Cλ is constrained as follows:

        1) it must have the lowest intra-cluster distance among those clusters
        of k “unswapped” locations that contain the location λ;

        2) it must have locations belonging to k different trajectories; and

        3) it must contain only locations at a path from λ at most Rs long and
        with time-stamps differing from tλ at most Rt.

    Then, the spatial coordinates (xλ,yλ) are swapped with the spatial
    coordinates of some random location in Cλ and both locations are marked as
    “swapped”.  If no cluster Cλ can be found, the location λ is removed from
    the data set and will not be considered anymore in the subsequent
    anonymization.  This process continues until no more “unswapped” locations
    appear in the data set.
    """
    raise NotImplementedError
    pass
