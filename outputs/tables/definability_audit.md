# LOSO definability audit by system_id

Family B / `random_forest` LOSO ROC-AUC is definable only when the held-out system contains both pass and fail labels. Summary: 2/12 dual-class systems; 19.1% of scored rows belong to definable systems.

| system_id | n_rows | n_positive | n_negative | prevalence | labels_present | loso_roc_auc_definable | family_b_rf_loso_roc_auc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| access_control | 20 | 0 | 20 | 0.000 | single-class | False | n/a |
| atm | 14 | 0 | 14 | 0.000 | single-class | False | n/a |
| bike_rental | 5 | 0 | 5 | 0.000 | single-class | False | n/a |
| elevator | 15 | 0 | 15 | 0.000 | single-class | False | n/a |
| hotel_booking | 20 | 5 | 15 | 0.250 | dual-class | True | 0.500 |
| login_system | 20 | 5 | 15 | 0.250 | dual-class | True | 0.667 |
| package_locker | 20 | 0 | 20 | 0.000 | single-class | False | n/a |
| parking_gate | 15 | 0 | 15 | 0.000 | single-class | False | n/a |
| smart_thermostat | 20 | 20 | 0 | 1.000 | single-class | False | n/a |
| train_ticket_booking | 20 | 0 | 20 | 0.000 | single-class | False | n/a |
| vending_machine | 20 | 0 | 20 | 0.000 | single-class | False | n/a |
| warehouse_inventory | 20 | 0 | 20 | 0.000 | single-class | False | n/a |
