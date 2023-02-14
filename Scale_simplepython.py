import numpy as np
def getsimplepythonScale(val, year, run, eta, r9, et, gain):
    url_dict = {
        "2016_preVFP": "https://raw.githubusercontent.com/cms-data/EgammaAnalysis-ElectronTools/master/ScalesSmearings/Run2016_UltraLegacy_preVFP_RunFineEtaR9Gain_scales.dat",
        "2016_postVFP": "https://raw.githubusercontent.com/cms-data/EgammaAnalysis-ElectronTools/master/ScalesSmearings/Run2016_UltraLegacy_postVFP_RunFineEtaR9Gain_scales.dat",
        "2017": "https://raw.githubusercontent.com/cms-data/EgammaAnalysis-ElectronTools/master/ScalesSmearings/Run2017_24Feb2020_runEtaR9Gain_v2_scales.dat",
        "2018": "https://raw.githubusercontent.com/cms-data/EgammaAnalysis-ElectronTools/master/ScalesSmearings/Run2018_29Sep2020_RunFineEtaR9Gain_scales.dat",
    }
    data = np.genfromtxt(url_dict[year])  # Extracts data from the target_url, giving an array of shape (n_row, n_cols)
    # Meaning of columns taken from Rajdeeps e-mail
    run_bin_low       = data[:,0]
    run_bin_high      = data[:,1]
    eta_bin_low       = data[:,2]
    eta_bin_high      = data[:,3]
    r9_bin_low        = data[:,4]
    r9_bin_high       = data[:,5]
    et_bin_low        = data[:,6]
    et_bin_high       = data[:,7]
    gain_seed         = data[:,8]
    total_correction  = data[:,9]
    total_uncertainty = data[:,10]
    
    
    # Here we find the indices of the input variables for each "category"
    run_indices = np.argwhere((run_bin_low <= run) & (run <= run_bin_high)) # is an array with shape (X, 1) where X is the number of times run was found in the binning defined by the two arrays
    eta_indices = np.argwhere((eta_bin_low <= eta) & (eta <= eta_bin_high))
    r9_indices = np.argwhere((r9_bin_low <= r9) & (r9 <= r9_bin_high))
    et_indices = np.argwhere((et_bin_low <= et) & (et <= et_bin_high))
    gain_indices = np.argwhere(gain_seed==gain)

    # This command reduces the indices by finding the intersection
    index = set(run_indices.flatten()) & set(eta_indices.flatten()) & set(r9_indices.flatten()) & set(et_indices.flatten()) & set(gain_indices.flatten())

    print(index)
    # If you give invalid values (e.g. run number that does not exist) or if the input .dat file allows multiple correction values for one set of input values nothing gets returned. Can change this behaviour if needed
    if len(index) == 1:
        index = index.pop()
    else:
        print("Error. Arguments to this function did not yield a unique value.")
        return None

    # For now we have the keys "scale_nominal" and "scale_smearing"
    if val=="scale_nominal":
        return total_correction[index]
    elif val=="scale_uncertainty":
        return total_uncertainty[index]
    else:
        print("Error. Not implemented yet.")
        return None