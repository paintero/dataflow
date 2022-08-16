from dataflow import *

system = System("PNL System")
meg_hpl = App('meg_hpl', system)
wcat_hpl = App('wcat_hpl', system)
meg_hpl.api_call(meg_hpl, "frtb_in_scope_map_POST", "frtb_in_scope_map")
meg_hpl.api_call(meg_hpl, "adjustment_cost_center_POST", "adjustment_cost_center_2022_06_10")
meg_hpl.api_call(meg_hpl, "hpl_consistency_checker_POST", "hpl_consistency_checker_ec_2022_06_30")
meg_hpl.api_call(meg_hpl, "hpl_consistency_checker_POST", "hpl_consistency_checker_holmes_2022_06_30")

# meg_hpl.api_call("hpl_cost_center_GET", "2022-06-27", "HOLMES")
# meg_hpl.api_call("hpl_cost_center_GET", "2022-06-27", "EC")
# system.eventq.print_eventq()