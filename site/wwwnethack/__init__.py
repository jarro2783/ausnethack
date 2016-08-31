""" wwwnethack utility package
"""

# Takes an array of games that have ascended, which is a dictionary with at
# least the following keys:
# - plname: The name of the player
# - role: The role that they played
# - number: The number of ascensions for this (player, role) pair
# Returns (scores, roles), where:
# - scores: a dictionary mapping player names to a dictionary with the
# keys 'total' and 'roles'. The key 'total' maps to the total zscore. The key
# 'roles' maps to a dictionary of their zscores for each role.
# - roles is a sorted array of roles
def calculate_zscores(ascended):
    """ Calculates the zscores of ascended games"""
    roles = {}
    scores = {}

    for row in ascended:
        plname = row['plname']
        role = row['role']
        roles[role] = 0
        if plname not in scores:
            scores[plname] = {'roles' : {}, 'total' : 0}

        player = scores[plname]

        zscore = calculate_z(row['number'])
        player['total'] += zscore
        player['roles'][role] = zscore

    return (scores, sorted(roles.keys()))

def calculate_z(games):
    """Calculates a single zscore given the number of games won for a role"""
    factor = 1.0
    zscore = 0
    i = 0
    while i < games:
        zscore += factor
        i += 1
        factor /= 2

    return zscore
