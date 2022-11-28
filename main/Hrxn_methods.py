import numpy as np

# ANL0
def anl0_hrxn(delE: dict, *args) -> float:
    """
    Calculate the heat of reaction using energies and 
    corrections computed by ANL0 methodology.

    Dictionary must contain keys:
    - 'avqz'
    - 'av5z'
    - 'zpe'
    Should contain correction keys:
    - 'core_0_tz'
    - 'core_X_tz'
    - 'core_0_qz'
    - 'core_X_qz'
    - 'ccQ'
    - 'ccT'
    - 'ci_DK'
    - 'ci_NREL'
    - 'zpe_anharm'
    - 'zpe_harm'

    ARGUMENTS
    ---------
    :delE:      [dict] Contains energy (Hartree) and correction values
                    for ANL0.
    :*args:     IGNORED

    RETURNS
    -------
    :Hrxn:      [float] The heat of reaction using ANL0
    """

    # these constants are used for basis set extrapolation
    hartree_to_kJpermole = 2625.499748 # (kJ/mol) / Hartree
    cbs_tz_qz = 3.0**3.7 / (4.0**3.7 - 3.0**3.7)
    cbs_tz_qz_low = - cbs_tz_qz
    cbs_tz_qz_high = 1.0 + cbs_tz_qz
    cbs_qz_5z = 4.0**3.7 / (5.0**3.7 - 4.0**3.7)
    cbs_qz_5z_low = - cbs_qz_5z
    cbs_qz_5z_high = 1.0 + cbs_qz_5z

    cbs = cbs_qz_5z_low * delE['avqz'] + cbs_qz_5z_high * delE['av5z']
    Hrxn = (cbs + delE['zpe']) * hartree_to_kJpermole

    keys = delE.keys()
    # don't add corrections if they are over 4 kJ/mol
    if 'core_0_tz' and 'core_X_tz' and 'core_0_qz' and 'core_X_qz' in keys: 
        core = cbs_tz_qz_low * (delE['core_0_tz'] - delE['core_X_tz']) + cbs_tz_qz_high * (delE['core_0_qz'] - delE['core_X_qz'])
        if abs(core * hartree_to_kJpermole) < 4.0:
            Hrxn += core * hartree_to_kJpermole
    if 'ccQ' and 'ccT' in keys:
        ccTQ = delE['ccQ'] - delE['ccT']
        if abs(ccTQ * hartree_to_kJpermole) < 4.0:
            Hrxn += ccTQ * hartree_to_kJpermole
    if 'ci_DK' and 'ci_NREL' in keys:
        ci = delE['ci_DK'] - delE['ci_NREL']
        if abs(ci * hartree_to_kJpermole) < 4.0:
            Hrxn += ci * hartree_to_kJpermole
    if 'zpe_anharm' and 'zpe_harm' in keys:
        anharm = delE['zpe_anharm'] - delE['zpe_harm'] 
        if abs(anharm) < 4.0:
            Hrxn += anharm # already kJ/mol
    
    return Hrxn

def sum_Hrxn(delE:dict, *args:str) -> float:
    """
    Calculates the heat of reaction for a generic coupled cluster
    result. 

    ARGUMENTS
    ---------
    :delE:      [dict] Contains energy (Hartree) values.
    :**args:    [str] Dictionary keys to sum for single point energy
                    Typically the single point energy and zpe.
    
    RETURNS
    -------
    :Hrxn:      [float] The heat of reaction using ANL0
    """

    hartree_to_kJpermole = 2625.499748 # (kJ/mol) / Hartree
    Hrxn = (sum([delE[k] for k in args])) * hartree_to_kJpermole
    return Hrxn
