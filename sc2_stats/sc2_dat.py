# -*- coding: utf-8 -*-

import requests
import pandas as pd
import io

from PIL import Image


def bliz_token(c_id, 
               s_id, 
               token_url='https://oauth.battle.net/token'):
    
    tk_dat = {'grant_type':'client_credentials'}

    tk_res = requests.post(token_url, data=tk_dat, auth=(c_id, s_id))
    
    try:
        tk = tk_res.json()['access_token']
    except:
        print('No Token Returned')
        tk = None

    return tk


def sc2_profile(reg,
                regID,
                rlmID,
                proID,
                header,
                pro_url='.api.blizzard.com/sc2/profile/'):
    
    p_url = f'https://{reg}{pro_url}{regID}/{rlmID}/{proID}'+\
                     '?locale=en_US'
    
    p_res = requests.get(p_url, headers=header)
    
    if p_res.status_code != 200: return None
    
    p_dict = p_res.json()
    
    r_d = {}
    r_d['name'] = p_dict['summary']['displayName']
    r_d['clanName'] = p_dict['summary']['clanName']
    r_d['clanTag'] = p_dict['summary']['clanTag']
    
    try:
        imgUrl = p_dict['summary']['portrait']
        r = requests.get(imgUrl, stream=True)
        r_d['portrait'] = Image.open(io.BytesIO(r.content))
    except:
        r_d['portrait'] = None
    
    for k in p_dict['snapshot'].keys():
        r_d[k] = p_dict['snapshot'][k]
    
    return r_d

def sc2_ladsum(reg,
               regID,
               rlmID,
               proID,
               header,
               ladder='1v1',
               pro_url='.api.blizzard.com/sc2/profile/'):
    
    # ladder rankings
    lrank = {'Bronze':1,'Silver':2,'Gold':3,'Platinum':4,
             'Diamond':5,'Master':6,'Grandmaster':7}
    
    p_url = f'https://{reg}{pro_url}{regID}/{rlmID}/{proID}/ladder/summary'+\
                     '?locale=en_US' 
    p_res = requests.get(p_url, headers=header)  
        
    if p_res.status_code != 200: return None
    
    lad_mem = p_res.json()['allLadderMemberships']
    pl_rk = -1
    pl_id = -1
    # get the highest ranked ladder that matches ladder
    for ld in lad_mem:
        lad_div = ld['localizedGameMode'].split(' ')[-1] # eg Master
        lad_type = ld['localizedGameMode'].split(' ')[0] # eg 1v1
        if lad_type != ladder: continue
        if lrank[lad_div] > pl_rk:
            pl_rk = lrank[lad_div]
            pl_id = ld['ladderId']
    
    r_d = {'rank':pl_rk,'ladder_id':pl_id}
    
    return r_d

def sc2_ladspc(reg,
               regID,
               rlmID,
               proID,
               ladID,
               header,
               pro_url='.api.blizzard.com/sc2/profile/'):
    
    p_url = f'https://{reg}{pro_url}{regID}/{rlmID}/{proID}/ladder/{ladID}'+\
                     '?locale=en_US'
    p_res = requests.get(p_url, headers=header)  
    
    if p_res.status_code != 200: return None
    
    lad_d = p_res.json()
    
    #lad_type = ['currentLadderMembership']['currentLadderMembership'].split(' ')[0]
    #lad_size =  lad_type.split('v')
    
    
    rank = lad_d['ranksAndPools'][0]['rank']
    mmr = lad_d['ranksAndPools'][0]['mmr']
    
    wins = lad_d['ladderTeams'][rank-1]['wins']
    loss = lad_d['ladderTeams'][rank-1]['losses']
    team = lad_d['ladderTeams'][rank-1]['teamMembers']
    
    r_d = {'rank':rank, 'mmr':mmr, 'wins':wins, 'losses':loss, 
          'team':team, 'team_size':len(team)}
        
    return r_d

def sc2_match(reg,
              regID,
              rlmID,
              proID,
              header,
              gtype='1v1',
              pro_url='.api.blizzard.com/sc2/legacy/profile/'):

    p_url = f'https://{reg}{pro_url}{regID}/{rlmID}/{proID}/matches'
    p_res = requests.get(p_url, headers=header)  
    
    if p_res.status_code != 200: return None
    
    mhs = pd.DataFrame(p_res.json()['matches'])
    mhs = mhs[mhs['type']==gtype]
    mhs['DateTime'] = pd.to_datetime(mhs['date'],unit='s',utc=True)
    
    return mhs

# ladders = ['1v1','2v2','3v3','4v4']

# player_lad = [s for s in ladders if s in u_dat.keys()]

# tk = bliz_token(u_dat['c_id'],u_dat['s_id'])

# tk_header = {'Authorization': f'Bearer {tk}'}

# pp = sc2_profile(u_dat['1v1']['server'],
#                  u_dat['1v1']['region'],
#                  u_dat['1v1']['realm'],
#                  u_dat['1v1']['sc2id'],
#                  tk_header) 

# ll = sc2_ladsum(u_dat['1v1']['server'],
#                  u_dat['1v1']['region'],
#                  u_dat['1v1']['realm'],
#                  u_dat['1v1']['sc2id'],
#                  tk_header,
#                  ladder=player_lad[0]) 

# lspc = sc2_ladspc(u_dat['1v1']['server'],
#                  u_dat['1v1']['region'],
#                  u_dat['1v1']['realm'],
#                  u_dat['1v1']['sc2id'],
#                  ll['ladder_id'],
#                  tk_header)

# mhs = sc2_match(u_dat['1v1']['server'],
#                  u_dat['1v1']['region'],
#                  u_dat['1v1']['realm'],
#                  u_dat['1v1']['sc2id'],
#                  tk_header)

