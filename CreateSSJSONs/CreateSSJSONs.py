import gzip
from correctionlib.schemav2 import CorrectionSet,Correction,Category,CategoryItem
from itertools import chain
import correctionlib.schemav2 as schema
from JSONTools import *
import pandas as pd
import numpy as np
from SandS_class import *
import os
#############################################################
years=["Prompt2022FG","Rereco2022BCD"]
folders=["Prompt2022FG","Rereco2022BCD"]
gain=[1.0,6.0,12.0]

smearing_urldict={
    "Prompt2022FG":"https://akapoordocs.web.cern.ch/akapoordocs/step2_Prompt2022FG_26_06_2023_v0_smearings.dat",
    "Rereco2022BCD":"https://akapoordocs.web.cern.ch/akapoordocs/step2_Prompt2022FG_26_06_2023_v0_smearings.dat",
}

scale_url_dict = {
    "Prompt2022FG":"https://akapoordocs.web.cern.ch/akapoordocs/step4closure_Prompt2022FG_28_06_2023_v0_scales.dat",
    "Rereco2022BCD":"https://akapoordocs.web.cern.ch/akapoordocs/step4closure_Prompt2022FG_28_06_2023_v0_scales.dat",
}
#############################################################

for name in folders:
    if not os.path.exists(name):
        os.makedirs(name)
        print(f"Folder '{name}' created.")
    else:
        print(f"Folder '{name}' already exists.")

for year,folder in zip(years,folders):
    print(year)
    corrs=[]
    runbinsall,fulldict=get_SS_runbins_and_SS_dict(year,scale_url_dict)
    workhorse=SandS(runbinsall,fulldict,getSmearingdictRun2(year,smearing_urldict))
    
    corr = Correction.parse_obj(
        {
            "version": 2,
            "name": f'{year}_ScaleJSON',
            "description": "yes",
            "inputs": [
                {"name": "valtype","type": "string", "description": "correction (total_correction) or uncertainty (total_uncertainty)"},
                {"name": "gain","type": "int", "description": "seed gain"},
                {"name": "run","type": "real", "description": "run"},
                {"name": "eta","type": "real", "description": "supercluster eta"},
                {"name": "r9", "type": "real", "description": "r9"},
                {"name": "et", "type": "real", "description": "et"},],
                #{"name": "gain", "type": "real", "description": "gain"},
            "output": {"name": "weight", "type": "real", "description": "value"},
            "data": Category.parse_obj({
                "nodetype": "category",
                "input": "valtype",
                "content": [
                    schema.CategoryItem.parse_obj({
                        "key": valtype, 
                        "value": schema.Category.parse_obj({
                            "nodetype": "category",
                            "input": "gain",
                            "content":[CategoryItem.parse_obj({"key":gain,
                                                               "value":workhorse.getrunSSnew(runbinsall,gain,valtype)
                                                              }) for gain in [1,6,12] 
                            ]
                        })
                    })
                    for valtype in ["total_correction","total_uncertainty"]
                ]
            })
        })
    corrs.append(corr)
    
    corr = Correction.parse_obj(
        {
            "version": 2,
            "name": f'{year}_SmearingJSON',
            "description": "yes",
            "inputs": [
                {"name": "valtype","type": "string", "description": "correction (total_correction) or uncertainty (total_uncertainty)"},
                {"name": "eta","type": "real", "description": "supercluster eta"},
                {"name": "r9", "type": "real", "description": "r9"},],
                #{"name": "gain", "type": "real", "description": "gain"},
            "output": {"name": "weight", "type": "real", "description": "value"},
            "data": Category.parse_obj({
                "nodetype": "category",
                "input": "valtype",
                "content": [
                    schema.CategoryItem.parse_obj({
                        "key": valtype, 
                        "value":workhorse.getrunSmearingnew(valtype,year)    
                    })
                    for valtype in ["rho","err_rho"]
                ]
            })
        })
    corrs.append(corr)
    

    #Save JSON
    cset = CorrectionSet(schema_version=2, corrections=corrs,description=f"These are the Scale and smearing corrections")
    with open(f"{folder}/SS.json", "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
        

# Testing
from correctionlib import _core
#Download the correct JSON files
evaluator = _core.CorrectionSet.from_file('Prompt2022FG/SS.json')


##
evaluator["Prompt2022FG_ScaleJSON"].evaluate("total_correction",1,362720.0,-2.5,0.5,100.0)
