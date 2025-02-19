import numpy as np
from deeperwin.wandb_utils import get_all_eval_energies, get_ensable_averge_energy_error, EnsembleEnergies, remove_data_at_epoch
import pickle
import re

def build_local_cache_file(optimizer, reload_blacklist=None, reload_whitelist=None):
    wandb_entity = "schroedinger_univie"
    cache_fname = f"/home/mscherbela/tmp/data_shared_vs_indep_{optimizer}.pkl"
    n_max = -1

    wandb_names = dict()
    for molecule in ['H4p', 'H6', 'H10', 'Ethene', 'Methane']:
        wandb_names[molecule] = dict()
        for curve in ['Indep', 'Shared_75', 'Shared_95', 'ReuseIndep', 'ReuseShared95', 'ReuseFromIndep', 'ReuseFromIndepSingleLR',
                      'ReuseFromSmallerShared']:
            wandb_names[molecule][curve] = f'PES_{molecule}_{curve}_{optimizer}{"_eval" if "Shared_" in curve else ""}'

    wandb_names['H10']['Shared_95'] = f'PES_H10_Shared95_{optimizer}_eval'
    wandb_names['Ethene']['ReuseFromSmallerShared'] = f'PES_Ethene_ReuseFromMethaneShared_{optimizer}'
    wandb_names['H10']['ReuseFromSmallerShared']= f'PES_H10_ReuseShared95H6_{optimizer}'

    if optimizer == 'adam':
        wandb_names['Ethene']['Shared_95'] = f'PES_Ethene_Shared95_{optimizer}_opt'
        wandb_names['Ethene']['ReuseShared95'] = f'PES_Ethene_Reuse_Shared95Adam'
    else:
        wandb_names['Ethene']['Shared_95'] = f'PES_Ethene_Shared95_{optimizer}_eval'

    wandb_names['Ethene']['Shared_75'] = f'PES_Ethene_Shared75_{optimizer}_eval'
    wandb_names['H10']['Shared_75'] = f'PES_H10_Shared75_{optimizer}_eval'


    with open(cache_fname, 'rb') as f:
        full_plot_data = pickle.load(f)
    for molecule in wandb_names:
        if molecule not in full_plot_data:
            full_plot_data[molecule] = dict()
        for curve, wandb_project in wandb_names[molecule].items():
            try:
                if reload_whitelist is None:
                    do_reload = True
                    if reload_blacklist is not None:
                        for pattern in reload_blacklist:
                            if re.search(pattern, wandb_project) is not None:
                                do_reload = False
                else:
                    do_reload = any([(re.search(pattern, wandb_project) is not None) for pattern in reload_whitelist])
                if do_reload:
                    df = get_all_eval_energies(wandb_entity + "/" + wandb_project, print_progress=True, n_max=n_max)
                    full_plot_data[molecule][curve] = get_ensable_averge_energy_error(df, exclude_unrealistic_deviations=False)
                    remove_data_at_epoch(full_plot_data[molecule][curve], 3096)
            except ValueError as e:
                print(str(e))

    # Add empty dummy entry for legend
    full_plot_data['H4p']['ReuseFromIndep'] = EnsembleEnergies(*[[] for _ in range(8)])
    full_plot_data['H4p']['ReuseFromSmallerShared'] = EnsembleEnergies(*[[] for _ in range(8)])
    full_plot_data['H4p']['ReuseFromIndepSingleLR'] = EnsembleEnergies(*[[] for _ in range(8)])


    with open(cache_fname, 'wb') as f:
        pickle.dump(full_plot_data, f)

if __name__ == '__main__':
    # build_local_cache_file('adam', ['H4p', 'H6', 'H10', 'Shared', 'Reuse'])
    # build_local_cache_file('adam', ['H4p', 'H6', 'H10', 'Indep', 'Reuse', '95'])
    build_local_cache_file('adam', reload_whitelist=['PES_H4p_Shared_95_adam_eval'])
    # build_local_cache_file('kfac')
    # build_local_cache_file('kfac', ['H4p', '_H6', 'H10', 'Methane_', '95', 'Indep'])
    # build_local_cache_file('kfac', reload_whitelist=['ReuseFromIndepSingleLR'])
    # build_local_cache_file('kfac', reload_whitelist=['Ethene'])



