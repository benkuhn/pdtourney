import collections
import imp
import os.path
import os
import sys
import random
import numpy as np
import numpy.random

PAYOFF = {
    'CC': (2, 2),
    'DC': (4, -2),
    'CD': (-2, 4),
    'DD': (0, 0)
}

N_MOVES = 433

def pd_imp(fname):
    mname = os.path.basename(fname)[:-3]
    return imp.load_source(mname, fname)

def run_game(p1, p2, n_moves):
    p1_moves = []
    p2_moves = []
    for i in xrange(n_moves):
        m1 = get_move(p1, p1_moves, p2_moves)
        m2 = get_move(p2, p2_moves, p1_moves)
        p1_moves.append(m1)
        p2_moves.append(m2)
    return score_game(p1_moves, p2_moves)

exceptions = collections.defaultdict(lambda: 0)

def get_move(player, moves, other_moves):
    try:
        move = player.get_move(moves, other_moves)
        assert move in 'CD'
    except:
        exceptions[player.__name__] += 1
        move = 'C'
    return move

def score_game(moves1, moves2):
    score1 = 0
    score2 = 0
    for m1, m2 in zip(moves1, moves2):
        s1, s2 = PAYOFF[m1 + m2]
        score1 += s1
        score2 += s2
    return score1, score2

module_dir = os.path.join(os.path.dirname(__file__), 'pdmod')

players = []
for fname in os.listdir(module_dir):
    if fname[-3:] != '.py':
        continue
    players.append(os.path.join(module_dir, fname))

n_players = len(players)

n_games = n_players * (n_players - 1) / 2

game_results = [[0 for p1 in players] for p2 in players]

for i in xrange(len(players)):
    for j in xrange(i + 1, len(players)):
        p1 = pd_imp(players[i])
        p2 = pd_imp(players[j])
        print p1.__name__, 'vs.', p2.__name__,
        sys.stdout.flush()
        score1, score2 = run_game(p1, p2, N_MOVES)
        print ':', score1, '-', score2
        game_results[i][j] = score1
        game_results[j][i] = score2

print game_results

scores = {}

for i in xrange(len(players)):
    scores[players[i]] = sum(game_results[i])
    print 'player', i, '(', players[i], '):', game_results[i], sum(game_results[i])

OUTFILE = 'matrix.html'

outtxt = ['<table><tr></td><td>']
for i in xrange(len(players)):
    outtxt.append('<td>' + os.path.basename(players[i])[:-3] + '</td>')
outtxt.append('</tr>')

for i in xrange(len(players)):
    outtxt.append('<tr><td>%s</td>' % os.path.basename(players[i])[:-3])
    for j in xrange(len(players)):
        if i == j:
            outtxt.append('<td></td>')
        else:
            outtxt.append('<td>%d vs %d</td>' % (game_results[i][j], game_results[j][i]))
    outtxt.append('</tr>')
outtxt.append('</table>')

with open(OUTFILE, 'w') as f:
    f.write('\n'.join(outtxt))

print '============'
print 'FINAL SCORES'

print scores
print exceptions

finalstr = []
finalscore = []
for k, v in list(scores.iteritems()):
    if scores[k] > 0:
        finalstr.append(k)
        finalscore.append(v)

finalscore = np.array(finalscore) * 1.0
cumsum = (finalscore * 1.0 / finalscore.sum()).cumsum()
finali = sum(cumsum < random.random())

print cumsum, finali, finalstr, finalscore

print finali, finalstr[finali], finalscore[finali]
