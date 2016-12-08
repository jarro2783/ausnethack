""" wwwnethack utility package
"""

from . import recordings

RECORDINGS = {
    'local': recordings.local,
    's3': recordings.s3,
}

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

def plural(unit, amount):
    """Pluralise a word depending on the count."""
    if amount == 1:
        return unit
    else:
        return unit + 's'

def format_human_readable(seconds):
    """Format time as human readable with two units."""
    formatted = []

    units = [
        (60, 'second'),
        (60, 'minute'),
        (60, 'hour'),
        (24, 'day'),
        (365, 'year'),
    ]

    remaining = seconds
    for unit in units:
        amount = remaining % unit[0]

        if amount != 0:
            formatted.append("{} {}".format(amount, plural(unit[1], amount)))

        remaining = remaining // unit[0]

        if remaining == 0:
            break

    if len(formatted) == 0:
        return '0 seconds'
    else:
        return ' '.join(formatted[-1:-3:-1])

def get_recordings_backend(config):
    """Gets the backend used for listing recordings based on the config.
    """
    backend = config['RECORDINGS_BACKEND']
    if backend in RECORDINGS:
        return RECORDINGS[backend].ListFiles(config)
