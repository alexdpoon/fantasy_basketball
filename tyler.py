#!/usr/bin/env python

import os
import random

# adjustments are used in calculate_season_stats()
MISSED_GAME_ADJUSTMENT = .67   # set to 0.0 to analyze totals only (i.e. no adjustment for missed games) - not fair to injured players
                                # set to 1.0 to analyze averages (full adjustment for missed games) - too much boost for an injury prone player
                                # set to 0.5-0.75 for a nice blend (partial adjustment for missed games) => 0.67

PRESEASON_GAME_ADJUSTMENT = 1.0
LAST_10_GAMES_ADJUSTMENT = 1.0

NUM_SEASONS = 100000  # 10000 takes about 1 minute on MacBook Pro, 100000 takes about 5 minutes on MacBook Pro
NUM_CATS = 9
NUM_TEAMS = 10
AVG_CAT_SCORE = 0.0 + (NUM_TEAMS+1)/2
AVG_TEAM_SCORE = 0.0 + AVG_CAT_SCORE * NUM_CATS

# filename
#  filenames have no convention except that preseason stats must have pre_ in front,
#   or else no players will be considered "useful"
#  when taking a full season file and adding your own selected preseason entries
#   manually, be sure to add -PRE to the end of the person's name so that his
#   stats will be normalized higher via PRESEASON_GAME_ADJUSTMENT
# http://www.dougstats.com/
filename = "02-03RD.txt"
filename = "03-04RD.txt"
# filename = "04-05-plus-alex.txt"
# filename = "pre_05-06RD_through_10_28_2005.txt"
filename = "07-08-plus-alex.txt"
#filename = "pre_season_2008.txt
filename = "08-09RD.txt"
filename = "pre_season_2009.txt"
filename = "09-10RD-partial.txt"
#filename = "09-10LFRD.txt.2"  # LF is last 10 games
filename = "09-10RD.txt"
filename = "pre_season_2010.txt"
filename = "09-10RD-plus-alex.txt"
filename = "10-11RD.txt"
filename = "11-12RD.txt"
filename = "pre_season_2012.txt"
filename = "12-13LFRD.txt"
filename = "12-13RD.txt"
filename = "13-14RD-partial.txt"
filename = "13-14RD.txt"
#filename = "preseason_2014.txt"
filename = "16-17LFRD.txt"

filename = "17-18LFRD.txt"                  # 2nd-half of season only
#filename = "17-18RD.txt"
filename = "pre_seasonRD_2018_2019.txt"      # full preseason

# field names in each position
# (might need to tweak for each diff file each year)
name = 0
team = 1
pos = 2
gp = 3
min = 4
fgm = 5
fga = 6
threesmade = 7
threesattempted = 8
ftm = 9
fta = 10
offrebs = 11
rebs = 12
assists = 13
steals = 14
turnovers = 15
blocks = 16
fouls = 17
dqs = 18
points = 19
techs = 20
ejects = 21
ff = 22
starts = 23
plus_minus = 24
notes = 25

# the lists of players
c = []
pf = []
sf = []
sg = []
pg = []

# for holding the max games anyone has played
MAX_GAMES = 0

# for simulation, the dictionary of final player rankings, hashed by player name
rankings = {}

# ============================================================================================
# Routines for reading in from raw data file

def overwrite_append(l, player):
     # add a player to a list, but if the player is already there,
     #  then remove the previous entry first (handles case in
     #  which some players are listed more than once)
    for p in l:
        if p[name] == player[name]:
            l.remove(p)
    l.append(player)

def add_to_position_lists(player):
    # figure out which player list to add to
    if player[pos].lower() == "c":
        overwrite_append(c, player)
        return
    if player[pos].lower() == "pf":
        overwrite_append(pf, player)
        return
    if player[pos].lower() == "sf":
        overwrite_append(sf, player)
        return
    if player[pos].lower() == "sg":
        overwrite_append(sg, player)        
        return
    if player[pos].lower() == "pg":
        overwrite_append(pg, player)        
        return

def convert_to_ints(player):
    # converts int fields to int
    for x in range(gp, starts+1):
        player[x] = int(player[x])
    return player

def is_useful_player(player):
    min_games_played = 30
    min_mpg = 15
    if "pre_" in filename:
        return True
    if "partial" in filename:
        min_games_played = 5
    if "LFRD" in filename:
        min_games_played = 5
    if "-PRE" in player[name]:
        return True    
    try:
        if player[notes]:
            return True
    except:
        pass
    if (player[gp] > min_games_played) and (player[min]/player[gp] > min_mpg):
        return True
    return False

# ============================================================================================
# Print routines

def print_out_list_sizes():
    # print out list sizes
    print "\nCenters: %s" % len(c)
    print "Power forwards: %s" % len(pf)
    print "Small forwards: %s" % len(sf)
    print "Shooting guards: %s" % len(sg)
    print "Point guards: %s" % len(pg)
    print "TOTAL: %s" % (len(c) + len(pf) + len(sf) + len(sg) + len(pg))

def print_out_player_lists():
    print "\nCenters"
    for x in c:
        print x
    print "\nPower forwards"
    for x in pf:
        print x
    print "\nSmall forwards"
    for x in sf:
        print x
    print "\nShooting guards"
    for x in sg:
        print x
    print "\nPoint guards"
    for x in pg:
        print x    

# ============================================================================================
# Routines for team simulation

class Team:
    """Represents a single team."""

    def __init__(self):
        self.players = []

        # season totals        
        self.points = 0
        self.rebs = 0
        self.assists = 0
        self.threesmade = 0
        self.steals = 0
        self.turnovers = 0
        self.blocks = 0
        self.fga = 0
        self.fgm = 0
        self.fta = 0
        self.ftm = 0
        self.fgp = 0.0
        self.ftp = 0.0

        # team points
        self.points_points = 0
        self.points_rebs = 0
        self.points_assists = 0
        self.points_threesmade = 0
        self.points_steals = 0
        self.points_turnovers = 0
        self.points_blocks = 0
        self.points_fgp = 0
        self.points_ftp = 0
        
        self.TP = 0

        # winner?
        self.winner = False

    def _add_random_from_list(self, position_list):
        if (len(position_list) == 0):
            print "\nNo more players left in %s\n" % position_list
            return
        x = random.randint(0, len(position_list)-1)    
        player = position_list[x]
        self.players.append(player)
        position_list.remove(player)        

    def choose_players(self, season):
        # C
        self._add_random_from_list(season.c)

        # C
        self._add_random_from_list(season.c)        
        
        # pf
        self._add_random_from_list(season.pf)
        
        # sf
        self._add_random_from_list(season.sf)
        
        # sg
        self._add_random_from_list(season.sg)
        
        # pg
        self._add_random_from_list(season.pg)

        # g
        if random.randint(0,1)==0:
            self._add_random_from_list(season.pg)
        else:
            self._add_random_from_list(season.sg)

        # f
        if random.randint(0,1)==0:
            self._add_random_from_list(season.pf)
        else:
            self._add_random_from_list(season.sf)

        # utils (choose from any position)
        total_num_players_left = len(season.c) + len(season.pf) + len(season.sf) + len(season.sg) + len(season.pg)
        for y in range(2):
            x = random.randint(0,total_num_players_left-1)
            if x<len(season.c):
                self._add_random_from_list(season.c)
            elif x<len(season.c)+len(season.pf):
                self._add_random_from_list(season.pf)
            elif x<len(season.c)+len(season.pf)+len(season.sf):
                self._add_random_from_list(season.sf)
            elif x<len(season.c)+len(season.pf)+len(season.sf)+len(season.sg):
                self._add_random_from_list(season.sg)
            else:
                self._add_random_from_list(season.pg)            

    def calculate_season_stats(self):
        for p in self.players:
            adjustment = MISSED_GAME_ADJUSTMENT
            if "-PRE" in p[name]:
                adjustment = PRESEASON_GAME_ADJUSTMENT
            factor = ((float(MAX_GAMES)-float(p[gp]))*adjustment + float(p[gp])) / float(p[gp])
            self.points += p[points] * factor
            self.rebs += p[rebs] * factor
            self.assists += p[assists] * factor
            self.threesmade += p[threesmade] * factor
            self.steals += p[steals] * factor
            self.turnovers += p[turnovers] * factor
            self.blocks += p[blocks] * factor
            self.fga += p[fga] * factor
            self.fgm += p[fgm] * factor
            self.fta += p[fta] * factor
            self.ftm += p[ftm] * factor                 
        self.fgp = (float(self.fgm) / float(self.fga))
        self.ftp = (float(self.ftm) / float(self.fta))
        

    def print_team(self):
        print
        for p in self.players:
            print p
        print "Points: %s (%s)" % (self.points, self.points_points)
        print "Rebounds: %s (%s)" % (self.rebs, self.points_rebs)
        print "Assists: %s (%s)" % (self.assists, self.points_assists)
        print "Threes: %s (%s)" % (self.threesmade, self.points_threesmade)
        print "Steals: %s (%s)" % (self.steals, self.points_steals)
        print "Turnovers: %s (%s)" % (self.turnovers, self.points_turnovers)
        print "Blocks: %s (%s)" % (self.blocks, self.points_blocks)
        print "FGA: %s" % self.fga
        print "FGM: %s" % self.fgm
        print "FTA: %s" % self.fta
        print "FTM: %s " % self.ftm
        print "FG%%: %f (%s)" % (self.fgp, self.points_fgp)
        print "FT%%: %f (%s)" % (self.ftp, self.points_ftp)
        print "TOTAL: %s" % self.TP
        
        
        
class Season:
    """Represents a single season simulation."""

    def __init__(self):
        self.teams = []     # the list of 10 teams in the fantasy league

        # make copy of player lists; we'll be pulling from *these* lists to form the teams.
        self.c = [x for x in c]
        self.pf = [x for x in pf]
        self.sf = [x for x in sf]
        self.sg = [x for x in sg]
        self.pg = [x for x in pg]
        
    def form_teams(self):
        for x in range(NUM_TEAMS):
            t = Team()
            t.choose_players(self)
            t.calculate_season_stats()
            s.teams.append(t)

    def evaluate(self):
        # sort teams by each category to total up team points
        # points
        self.teams.sort(lambda t1, t2: cmp(t1.points, t2.points))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_points = y
            y += 1
        # rebounds
        self.teams.sort(lambda t1, t2: cmp(t1.rebs, t2.rebs))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_rebs = y            
            y += 1
        # assists
        self.teams.sort(lambda t1, t2: cmp(t1.assists, t2.assists))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_assists = y            
            y += 1            
        # threes
        self.teams.sort(lambda t1, t2: cmp(t1.threesmade, t2.threesmade))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_threesmade = y            
            y += 1            
        # steals
        self.teams.sort(lambda t1, t2: cmp(t1.steals, t2.steals))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_steals = y            
            y += 1
        # turnovers
        self.teams.sort(lambda t1, t2: cmp(t2.turnovers, t1.turnovers))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_turnovers = y            
            y += 1
        # blocks
        self.teams.sort(lambda t1, t2: cmp(t1.blocks, t2.blocks))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_blocks = y            
            y += 1              
        # fgp
        self.teams.sort(lambda t1, t2: cmp(t1.fgp, t2.fgp))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_fgp = y            
            y += 1
        # fgt
        self.teams.sort(lambda t1, t2: cmp(t1.ftp, t2.ftp))
        y = 1
        for x in self.teams:
            x.TP += y
            x.points_ftp = y            
            y += 1

        # mark the appropriate team the winner
        self.teams.sort(lambda t1, t2: cmp(t2.TP, t1.TP))
        self.teams[0].winner = True
            
        # apply team points to each player
        for t in self.teams:
            for p in t.players:
                # create player ranking if not already existing
                if not rankings.has_key(p[name]):
                    pr = Player_Ranking(p)
                    rankings[p[name]] = pr
                # ok, update the existing player rankings
                pr = rankings[p[name]]
                pr.seasons_played += 1
                # pr.points_points = ((float(pr.seasons_played)-1.0)*pr.points_points+float(t.points_points))/float(pr.seasons_played)
                pr.points_points = float(pr.seasons_played-1)*(float(pr.points_points)/float(pr.seasons_played)) + \
                                   float(t.points_points)/float(pr.seasons_played)
                pr.points_rebs = float(pr.seasons_played-1)*(float(pr.points_rebs)/float(pr.seasons_played)) + \
                                   float(t.points_rebs)/float(pr.seasons_played)
                pr.points_assists = float(pr.seasons_played-1)*(float(pr.points_assists)/float(pr.seasons_played)) + \
                                   float(t.points_assists)/float(pr.seasons_played)
                pr.points_threesmade = float(pr.seasons_played-1)*(float(pr.points_threesmade)/float(pr.seasons_played)) + \
                                   float(t.points_threesmade)/float(pr.seasons_played)
                pr.points_steals = float(pr.seasons_played-1)*(float(pr.points_steals)/float(pr.seasons_played)) + \
                                   float(t.points_steals)/float(pr.seasons_played)
                pr.points_turnovers = float(pr.seasons_played-1)*(float(pr.points_turnovers)/float(pr.seasons_played)) + \
                                   float(t.points_turnovers)/float(pr.seasons_played)
                pr.points_blocks = float(pr.seasons_played-1)*(float(pr.points_blocks)/float(pr.seasons_played)) + \
                                   float(t.points_blocks)/float(pr.seasons_played)
                pr.points_fgp = float(pr.seasons_played-1)*(float(pr.points_fgp)/float(pr.seasons_played)) + \
                                   float(t.points_fgp)/float(pr.seasons_played)
                pr.points_ftp = float(pr.seasons_played-1)*(float(pr.points_ftp)/float(pr.seasons_played)) + \
                                   float(t.points_ftp)/float(pr.seasons_played)                 
                pr.TP = float(pr.seasons_played-1)*(float(pr.TP)/float(pr.seasons_played)) + \
                                   float(t.TP)/float(pr.seasons_played)
                if t.winner:
                    pr.wins += 1

class Player_Ranking:
    """Represents a player rank."""

    def __init__(self, player):
        self.player = player
        self.seasons_played = 0
        
        # running average of points
        self.points_points = 0
        self.points_rebs = 0
        self.points_assists = 0
        self.points_threesmade = 0
        self.points_steals = 0
        self.points_turnovers = 0        
        self.points_blocks = 0
        self.points_fgp = 0
        self.points_ftp = 0
        
        self.TP = 0

        # num wins
        self.wins = 0

    def print_ranking(self, rank):
        player_note = "------"
        try:
            player_note = pr.player[notes]
        except:
            pass
        GP = float(pr.player[gp])
        print "%s) %s [%.2f] [%.1f%%] %sgp (%smin) %s %s %s" % (rank, pr.player[name].upper(), pr.TP - AVG_TEAM_SCORE, float(pr.wins)*100.0/float(pr.seasons_played), pr.player[gp], pr.player[min]/pr.player[gp], pr.player[pos], pr.player[team].upper(), player_note)
        if pr.player[fga]==0:
            fgp = 0
        else:
            fgp = pr.player[fgm]*100/pr.player[fga]
        if pr.player[fta]==0:
            ftp = 0
        else:
            ftp = pr.player[ftm]*100/pr.player[fta]            
            
        print "(%s%% fg), (%s%% ft), (%.1f 3s), (%.1f reb), (%.1f ass), (%.1f stl), (%.1f to), (%.1f pts), (%.1f blk)" % (fgp, ftp, \
                                                           float(pr.player[threesmade])/GP, float(pr.player[rebs])/GP, float(pr.player[assists])/GP, \
                                                           float(pr.player[steals])/GP, float(pr.player[turnovers])/GP, float(pr.player[points])/GP, float(pr.player[blocks])/GP)
        print "[%.1f fg], [%.1f ft], [%.1f 3s], [%.1f reb], [%.1f ass], [%.1f stl], [%.1f to], [%.1f pts], [%.1f blk]" % (pr.points_fgp - AVG_CAT_SCORE, pr.points_ftp - AVG_CAT_SCORE, \
                                                           pr.points_threesmade - AVG_CAT_SCORE, pr.points_rebs - AVG_CAT_SCORE, pr.points_assists - AVG_CAT_SCORE, \
                                                           pr.points_steals - AVG_CAT_SCORE, pr.points_turnovers - AVG_CAT_SCORE, pr.points_points - AVG_CAT_SCORE, pr.points_blocks - AVG_CAT_SCORE)        
        

# ============================================================================================


if __name__ == "__main__":
    random.seed()

    # setup
    if "LFRD" in filename:
        MISSED_GAME_ADJUSTMENT = LAST_10_GAMES_ADJUSTMENT
    
    # get the players and put them in the right lists
    in_file = open(filename, "r")
    text = in_file.readline() # toss the header
    text = in_file.readline() 
    while len(text) > 0:
        text = text[:len(text)-1] # get rid of trailing \n
        player = text.split(" ")
        player = [x for x in player if len(x) > 0]
        player = convert_to_ints(player)
        if player[gp] > MAX_GAMES:
            MAX_GAMES = player[gp]
        if is_useful_player(player):
            add_to_position_lists(player)
        else:
            # print player
            pass
        text = in_file.readline() 
    in_file.close()

    # print out list sizes
    print_out_list_sizes()    

    # print out all players
    # print_out_player_lists()

    # do a season and populate rankings
    for x in range(NUM_SEASONS):
        s = Season()
        s.form_teams()
        if x==-1:
            for t in s.teams:
                t.print_team()
        s.evaluate()  

    # sort rankings by TP
    sorted_rankings_list = []
    for pname in rankings.keys():
        pr = rankings[pname]
        sorted_rankings_list.append(pr)
    sorted_rankings_list.sort(lambda pr1, pr2: cmp(pr2.TP, pr1.TP))

    # output rankings
    x = 1
    for pr in sorted_rankings_list:
        if x<=300:
            print
            pr.print_ranking(x)
        x += 1
    
    
