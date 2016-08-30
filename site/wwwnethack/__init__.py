class ZScore:
    def __init__(self, plname, zscore):
        self.plname = plname
        self.zscore = zscore

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

    return (scores, roles)

def calculate_z(n):
    factor = 1.0
    z = 0
    i = 0
    while i < n:
        z += factor
        i += 1
        factor /= 2

    return z
