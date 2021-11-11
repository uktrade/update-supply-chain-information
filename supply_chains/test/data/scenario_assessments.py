two_full_scenario_assessments_csv = """
sc_reporting_id_lvl_zero,supply_chain_reporting_name,type,scenario,severity,implications and rationale,critical_flag,critical_scenarios
SC001,Supply Chain One,supply,borders closed,n/a,"One borders closed implication",0,
SC001,Supply Chain One,supply,storage full,red,"One storage full implication",0,
SC001,Supply Chain One,supply,ports blocked,tbc,"One ports blocked implication",0,
SC001,Supply Chain One,supply,raw material shortage,red,"One raw material shortage implication",0,
SC001,Supply Chain One,supply,labour shortage,red,"One labour shortage implication",0,
SC001,Supply Chain One,supply,demand spike,red,"One demand spike implication",0,
SC002,Supply Chain Two,supply,borders closed,amber,"Two borders closed implication",1,"Two borders closed critical scenario"
SC002,Supply Chain Two,supply,storage full,amber,"Two storage full implication",1,"Two storage full critical scenario"
SC002,Supply Chain Two,supply,ports blocked,amber,"Two ports blocked implication",1,"Two ports blocked critical scenario"
SC002,Supply Chain Two,supply,raw material shortage,amber,"Two raw material shortage implication",1,"Two raw material shortage critical scenario"
SC002,Supply Chain Two,supply,labour shortage,amber,"Two labour shortage implication",1,"Two labour shortage critical scenario"
SC002,Supply Chain Two,supply,demand spike,amber,"Two demand spike implication",1,"Two demand spike critical scenario"
"""

scenario_assessment_with_transition_period_scenario_csv = """
SC002,Supply Chain Two,supply,borders closed,amber,"Two borders closed implication",1,"Two borders closed critical scenario"
SC002,Supply Chain Two,supply,storage full,amber,"Two storage full implication",0,
SC002,Supply Chain Two,supply,ports blocked,amber,"Two ports blocked implication",0,
SC002,Supply Chain Two,supply,raw material shortage,amber,"Two raw material shortage implication",0,
SC002,Supply Chain Two,supply,labour shortage,amber,"Two labour shortage implication",0,
SC002,Supply Chain Two,supply,End of transition with no negotiated outcome,amber,"Two eot implication",0,
SC002,Supply Chain Two,supply,demand spike,amber,"Two demand spike implication",1,"Two demand spike critical scenario"
"""
