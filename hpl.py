from dataflow import *

meg_hpl = App('meg_hpl')
meg_hpl.api_call("hpl_consistency_checker_POST", "hpl_consistency_checker_holmes_2022_06_30")
meg_hpl.api_call("adjustment_cost_center_POST", "adjustment_cost_center_2022_06_10")
meg_hpl.api_call("frtb_in_scope_map_POST", "frtb_in_scope_map")
