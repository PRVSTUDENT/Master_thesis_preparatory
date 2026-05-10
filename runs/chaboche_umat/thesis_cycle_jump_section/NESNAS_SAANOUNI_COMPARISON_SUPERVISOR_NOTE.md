# Comparison Between Nesnas--Saanouni Damage-Based Cycle Jumping and the Present Chaboche UMAT Cycle-Jump Workflow

Current status: The cycle-jump thesis section is complete through Stage 8 and ready for supervisor review.

The present work is inspired by the adaptive cycle-jump idea of Nesnas--Saanouni, but it is not a direct implementation of their coupled damage-viscoplasticity formulation. The main difference is that the research paper controls the jump size using a damage variable, whereas this project adapts the same idea to a Chaboche unified viscoplastic UMAT without damage. Therefore, the damage variable is replaced by generalized Chaboche control variables such as backstress, viscoplastic strain tensor components, and residual stress.

| Aspect | Nesnas--Saanouni Paper | This Chaboche UMAT Project | Main Difference |
|---|---|---|---|
| Material model | Coupled viscoplasticity-damage model | Chaboche unified viscoplastic UMAT | The present model does not include explicit damage. |
| Main cycle-jump control variable | Damage variable \(D\) | Generalized Chaboche control variables \(Y_i\) | \(D\) is replaced by backstress, viscoplastic strain tensor, and stress-based quantities. |
| Physical meaning of jump control | Limit the admissible damage growth during a jump | Limit the admissible change of selected Chaboche state variables | The jump is controlled by internal-state consistency, not damage evolution. |
| Admissible jump budget | Damage increment limit, often written as \(\Delta L\) or admissible damage change | Admissible state change \(A_i = \tau_i S_i\) | The damage budget is generalized into a variable-wise state-change budget. |
| Jump-size formula | Based on damage evolution rate per cycle | \(\Delta N_i = \left\lfloor \dfrac{\eta A_i}{\lvert\operatorname{mean}(\Delta Y_i)\rvert+\varepsilon} \right\rfloor\) | Same adaptive logic, but applied to Chaboche variables instead of damage. |
| Global jump decision | Controlled mainly by damage evolution | Grouped minimum: \(\Delta N_{\mathrm{restart}} = \min(\Delta N_X,\Delta N_{\varepsilon^{vp}},\Delta N_S)\) | The present method uses grouped controllers rather than one damage controller. |
| Role of accumulated plastic/viscoplastic strain | Often coupled with damage evolution | `STATEV1 = p` is used only as an accuracy monitor | Cumulative \(p\) was too conservative for jump control because it gave \(\Delta N=1\). |
| Restart implementation | Research-level cycle-jump framework for damage-viscoplasticity | Abaqus continuation using `SDVINI` and `SIGINI` | This project demonstrates actual Abaqus state injection and continuation. |
| Validation style | Paper validates the proposed damage-based cycle-jump method | Stage 5B, Stage 6D, and Stage 7C are validated against no-skip Abaqus references | Validation is focused on Abaqus UMAT workflow correctness and prediction error. |
| Best result in this project | Not applicable | Stage 7C: \(\Delta N=17\), 16 skipped cycles, `STATEV1` error `0.0231584782019%`, `S11` error `2.36494669088%` | The adaptive jump was directly validated in Abaqus. |
| Main limitation | Accuracy depends on damage-variable evolution and constitutive model assumptions | Stress/backstress extrapolation limits larger jumps | Accumulated viscoplastic strain prediction is accurate, but stress prediction becomes the limiting factor. |
| Scope | Full damage-viscoplastic cycle-jump method | Demonstration of Chaboche UMAT cycle-jump continuation | The present work is a workflow and methodology demonstration, not yet a full fatigue-life/damage model. |

In summary, the research paper uses a damage-based adaptive cycle-jump technique, while this project generalizes the same jump-control philosophy to a Chaboche viscoplastic UMAT without damage. The main contribution of this project is the practical Abaqus implementation: predicted `STATEV` values are injected using `SDVINI`, residual stress is injected using `SIGINI`, and the continuation response is validated against no-skip Abaqus reference simulations.
