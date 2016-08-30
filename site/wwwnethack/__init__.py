class ZScore:
    def __init__(self, plname, zscore):
        self.plname = plname
        self.zscore = zscore

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
    roles = {}
    scores = {}

    for r in ascended:
        plname = r['plname']
        role = r['role']
        roles[role] = 0
        if plname not in scores:
            scores[plname] = {'roles' : {}, 'total' : 0}

        player = scores[plname]

        zscore = calculate_z(r['number'])
        player['total'] += zscore
        player['roles'][role] = zscore

    return (scores, sorted(roles.keys()))

def calculate_z(n):
    factor = 1.0
    z = 0
    i = 0
    while i < n:
        z += factor
        i += 1
        factor /= 2

    return z
