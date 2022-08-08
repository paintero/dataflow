select  h.business_date,
        a.sub_desk_id,
        a.sub_desk_name,
        a.frtb_scope,
        a.frtb_cost_center_classification,
        ifnull(f.frtb_in_scope,"OUT OF SCOPE") frtb_in_scope,
        h.cost_center_id,
        h.pnl_attribute,
        h.finance_pnl_usd,
        h.constructed_pnl_usd
from    hpl_consistency_checker h
left join adjustment_cost_center a ON h.cost_center_id = a.cost_center_id
left join frtb_in_scope_map f ON a.frtb_cost_center_classification = f.frtb_cost_center_classification
                            AND a.frtb_scope = f.frtb_scope;
