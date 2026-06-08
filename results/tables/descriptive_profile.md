# Descriptive profile

Grouped descriptive statistics for structural and behavioural variables.
BPR statistics use behaviourally scored runs within each group.

**Scored analysis set:** n=209 of 240 total runs.

## By `model`

| group | n_runs | behaviourally_scored_n | mean_bpr | median_bpr | full_pass_n | full_pass_rate_scored | mean_requirement_coverage | mean_n_states | mean_n_transitions | mean_missing_transitions | mean_extra_transitions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemma2:9b | 60 | 55 | 0.451 | 0.312 | 10 | 0.182 | 0.611 | 3.583 | 4.700 | 3.091 | 3.400 |
| llama3.1:8b | 60 | 44 | 0.511 | 0.500 | 5 | 0.114 | 0.774 | 3.583 | 6.083 | 2.091 | 3.682 |
| mistral-nemo:12b | 60 | 55 | 0.474 | 0.353 | 10 | 0.182 | 0.695 | 3.583 | 5.483 | 3.182 | 4.345 |
| qwen2.5-coder:7b | 60 | 55 | 0.518 | 0.500 | 5 | 0.091 | 0.653 | 3.583 | 5.250 | 2.545 | 3.364 |

## By `system_id`

| group | n_runs | behaviourally_scored_n | mean_bpr | median_bpr | full_pass_n | full_pass_rate_scored | mean_requirement_coverage | mean_n_states | mean_n_transitions | mean_missing_transitions | mean_extra_transitions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| access_control | 20 | 20 | 0.458 | 0.500 | 0 | 0.000 | 0.537 | 2.000 | 5.050 | 1.500 | 4.300 |
| atm | 20 | 14 | 0.312 | 0.312 | 0 | 0.000 | 0.786 | 4.000 | 6.450 | 4.071 | 4.357 |
| bike_rental | 20 | 5 | 0.765 | 0.765 | 0 | 0.000 | 0.625 | 4.000 | 5.250 | 1.000 | 1.000 |
| elevator | 20 | 15 | 0.250 | 0.250 | 0 | 0.000 | 0.500 | 4.000 | 4.500 | 4.000 | 4.000 |
| hotel_booking | 20 | 20 | 0.750 | 0.875 | 5 | 0.250 | 0.787 | 4.000 | 6.800 | 1.250 | 2.550 |
| login_system | 20 | 20 | 0.625 | 0.500 | 5 | 0.250 | 0.667 | 3.000 | 4.000 | 2.000 | 2.000 |
| package_locker | 20 | 20 | 0.441 | 0.353 | 0 | 0.000 | 0.688 | 4.000 | 5.500 | 3.250 | 4.750 |
| parking_gate | 20 | 15 | 0.294 | 0.294 | 0 | 0.000 | 0.533 | 4.000 | 4.500 | 3.667 | 4.333 |
| smart_thermostat | 20 | 20 | 1.000 | 1.000 | 20 | 1.000 | 0.781 | 3.000 | 6.250 | 0.000 | 0.250 |
| train_ticket_booking | 20 | 20 | 0.250 | 0.250 | 0 | 0.000 | 0.812 | 4.000 | 6.750 | 5.000 | 6.750 |
| vending_machine | 20 | 20 | 0.500 | 0.500 | 0 | 0.000 | 0.583 | 3.000 | 3.500 | 2.000 | 2.500 |
| warehouse_inventory | 20 | 20 | 0.250 | 0.250 | 0 | 0.000 | 0.750 | 4.000 | 6.000 | 5.000 | 6.000 |

## By `g2_pass`

| group | n_runs | behaviourally_scored_n | mean_bpr | median_bpr | full_pass_n | full_pass_rate_scored | mean_requirement_coverage | mean_n_states | mean_n_transitions | mean_missing_transitions | mean_extra_transitions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | 20 | 20 | 0.469 | 0.375 | 0 | 0.000 | 0.798 | 3.750 | 6.050 | 3.000 | 4.550 |
| True | 189 | 189 | 0.489 | 0.353 | 30 | 0.159 | 0.666 | 3.497 | 5.286 | 2.735 | 3.608 |
| missing | 31 | 0 | nan | nan | 0 | nan | nan | 4.000 | 5.516 | nan | nan |

## By `g3_pass`

| group | n_runs | behaviourally_scored_n | mean_bpr | median_bpr | full_pass_n | full_pass_rate_scored | mean_requirement_coverage | mean_n_states | mean_n_transitions | mean_missing_transitions | mean_extra_transitions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | 26 | 26 | 0.480 | 0.500 | 0 | 0.000 | 0.705 | 2.962 | 6.346 | 1.808 | 4.231 |
| True | 183 | 183 | 0.488 | 0.353 | 30 | 0.164 | 0.674 | 3.601 | 5.219 | 2.896 | 3.623 |
| missing | 31 | 0 | nan | nan | 0 | nan | nan | 4.000 | 5.516 | nan | nan |

## By `g3a_pass`

| group | n_runs | behaviourally_scored_n | mean_bpr | median_bpr | full_pass_n | full_pass_rate_scored | mean_requirement_coverage | mean_n_states | mean_n_transitions | mean_missing_transitions | mean_extra_transitions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | 21 | 21 | 0.386 | 0.500 | 0 | 0.000 | 0.665 | 2.714 | 5.714 | 2.238 | 4.762 |
| True | 188 | 188 | 0.499 | 0.353 | 30 | 0.160 | 0.680 | 3.612 | 5.319 | 2.819 | 3.580 |
| missing | 31 | 0 | nan | nan | 0 | nan | nan | 4.000 | 5.516 | nan | nan |
