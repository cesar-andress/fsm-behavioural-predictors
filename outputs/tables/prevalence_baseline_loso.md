# Prevalence-only baseline — LOSO by held-out system

Held-out rows scored with global training prevalence only (seed=42 not used; deterministic scoring).

| held_out_system | n_test | n_positive | n_negative | global_train_prevalence | roc_auc | pr_auc | balanced_accuracy | f1 | mcc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| access_control | 20 | 0 | 20 | 0.159 | nan | nan | nan | nan | nan |
| atm | 14 | 0 | 14 | 0.154 | nan | nan | nan | nan | nan |
| bike_rental | 5 | 0 | 5 | 0.147 | nan | nan | nan | nan | nan |
| elevator | 15 | 0 | 15 | 0.155 | nan | nan | nan | nan | nan |
| hotel_booking | 20 | 5 | 15 | 0.132 | 0.500 | 0.250 | 0.500 | 0.000 | 0.000 |
| login_system | 20 | 5 | 15 | 0.132 | 0.500 | 0.250 | 0.500 | 0.000 | 0.000 |
| package_locker | 20 | 0 | 20 | 0.159 | nan | nan | nan | nan | nan |
| parking_gate | 15 | 0 | 15 | 0.155 | nan | nan | nan | nan | nan |
| smart_thermostat | 20 | 20 | 0 | 0.053 | nan | nan | nan | nan | nan |
| train_ticket_booking | 20 | 0 | 20 | 0.159 | nan | nan | nan | nan | nan |
| vending_machine | 20 | 0 | 20 | 0.159 | nan | nan | nan | nan | nan |
| warehouse_inventory | 20 | 0 | 20 | 0.159 | nan | nan | nan | nan | nan |
