# -*- coding: utf-8 -*-

import configparser
import os
import sc2_stats

from pathlib import Path

def get_config_file():
    """Return location of configuration file

    In order
    1. ~/sc2_stats/sc2_stats
    2. The installation folder of sc2_stats

    Returns
    -------
    loc : string
        File path of the dataiorc configuration file

    References
    ----------
    modeled completely from helipy/util/config.py
    """
    config_filename = '.sc2_irc'

    # Get user configuration location
    home_dir = Path.home()
    config_file_1 = home_dir / 'sc2_stats' / config_filename

    module_dir = Path(sc2_stats.__file__)
    config_file_2 = module_dir / '..' / config_filename
    config_file_2 = config_file_2.resolve()

    for f in [config_file_1, config_file_2]:
        if f.is_file():
            return str(f)    
        
def load_config():
    """Read in configuration file neccessary for downloading and
    loading data.

    Returns
    -------
    config_dic : dict
        Dictionf containing all options from configuration file.
    """
    
    config_path = get_config_file()
    configf = configparser.ConfigParser()
    configf.read(config_path)
    
    config_dic = {}
    
    # get the data that's required
    config_dic['c_id'] = configf['DEFAULT']['c_id']
    config_dic['s_id'] = configf['DEFAULT']['s_id']
    config_dic['sc2id'] = configf['DEFAULT']['sc2id']
    
    # get the rest of the file
    sec_dic = d = {s:dict(configf.items(s)) for s in configf.sections()}
    
    for k in sec_dic.keys():
        config_dic[k] = sec_dic[k]
    
    return config_dic