# AI/ML-Generated Measures Protocol

Use this protocol when any analytic variable, match, score, topic, index, similarity, or imputation is produced by AI or machine learning.

## 1. Separate code assistance from generated measurement

### AI-generated code only

The principal risk is computational: wrong files, joins, filters, formulas, timing, estimators, or outputs. Use deterministic execution, assertions, logs, manifests, and independent checks.

### AI-generated data or covariates

The project also has measurement and inferential risk. Running the resulting variable in Stata does not validate it.

## 2. Freeze the construct before labeling

Document:

- theoretical definition;
- unit of classification or scoring;
- inclusion and exclusion criteria;
- positive, negative, ambiguous, and insufficient-information examples;
- information the model is allowed to see;
- threshold or aggregation rule;
- relationship between the generated proxy and the latent construct.

Do not tune the definition after observing downstream coefficients.

## 3. Preserve provenance for every generated record

Where technically possible, retain:

- stable observation ID;
- source-text or source-record identifier and checksum;
- model provider and exact version;
- full system and user prompt;
- parameters such as temperature, seed, top-p, or deterministic setting;
- raw model response;
- parsed label/score;
- confidence or probability if meaningful;
- run timestamp;
- retry count and error state;
- post-processing rule;
- human correction and adjudication history.

A final CSV of labels without this provenance is not an auditable AI measurement pipeline.

## 4. Design the validation sample

A validation sample should cover the intended deployment distribution. Include:

- a probability sample from the full population;
- enough positive cases to estimate false positives and precision;
- enough negative cases to estimate false negatives and specificity;
- low-confidence and boundary cases;
- important countries, years, industries, languages, and data sources;
- temporal holdout when language or model behavior may drift;
- independent human coding, preferably by at least two coders for subjective constructs;
- a prespecified disagreement-adjudication procedure.

Do not use the same cases to write the rubric, tune the prompt/threshold, and report final validation performance without a separate holdout.

## 5. Binary labels

Report the full confusion matrix and uncertainty for:

- false-positive rate;
- false-negative rate;
- sensitivity/recall;
- specificity;
- precision/positive predictive value;
- negative predictive value;
- prevalence;
- balanced accuracy or F1 when substantively useful.

Overall accuracy is especially misleading when the positive class is rare.

Check error rates by substantively important subgroup and time period. Use exact or bootstrap confidence intervals where appropriate.

## 6. Multiclass labels

Report:

- class-by-class confusion matrix;
- macro- and prevalence-weighted metrics;
- one-vs-rest false-positive and false-negative rates;
- confusion pairs with substantive consequences;
- calibration when class probabilities are used;
- whether class definitions are mutually exclusive and collectively exhaustive.

## 7. Continuous scores and ratings

Assess:

- agreement with independent human scores or established external measures;
- calibration and monotonicity;
- repeated-run stability;
- alternative prompt/model agreement;
- inter-rater or intra-class reliability when multiple raters exist;
- distributional artifacts, heaping, truncation, and scale compression;
- sensitivity to scaling, normalization, and threshold choices;
- construct, convergent, discriminant, and predictive validity as appropriate.

High correlation alone does not establish unbiased measurement or valid regression inference.

## 8. Entity matching and record linkage

Do not collapse all matches into one unqualified binary variable. Preserve match provenance such as:

- exact identifier match;
- deterministic rule-based match;
- fuzzy-string candidate;
- AI-suggested match;
- human-confirmed match;
- rejected match;
- unresolved/ambiguous match.

Validate both false matches and missed matches. Oversample high-impact and ambiguous links. Run downstream estimates on prespecified match sets, for example:

1. exact/high-confidence only;
2. exact plus human-confirmed;
3. all accepted matches;
4. worst-case inclusion/exclusion of unresolved cases.

## 9. Topic shares, embeddings, similarity, and aggregated indices

For each observation, retain the amount of source information used to estimate the measure, such as number of documents, paragraphs, tokens, events, or classified units.

Inspect whether low-information observations dominate measurement error. Report:

- corpus coverage and missingness;
- document/unit counts by observation;
- training and test separation;
- semantic coherence and human interpretability;
- external or historical validity checks;
- out-of-sample performance;
- model, hyperparameter, seed, and preprocessing stability;
- identification assumptions for latent-factor or topic models.

When a classifier is aggregated into an index, use the test-set confusion matrix to characterize misclassification rather than treating raw predicted frequencies as truth.

## 10. Downstream inference

Write the generated variable as an estimated proxy, for example:

```text
hat_theta_i estimates latent theta_i from unstructured input x_i.
```

The ordinary two-step workflow—estimate `hat_theta_i`, then treat it as error-free in a regression—can produce biased coefficients and confidence intervals with incorrect centering even when ordinary standard errors look reasonable.

For binary generated labels, the measurement-error diagnostic in the Battaglia-Christensen-Hansen-Sacher framework is related to:

```text
kappa_hat = sqrt(n) * estimated_false_positive_rate
```

under the paper's assumptions and scaling. For topic or aggregated-count settings, the relevant diagnostic depends on the average inverse amount of information per observation, schematically:

```text
kappa_hat = sqrt(n) * mean(1 / C_i)
```

These formulas are not universal plug-ins for arbitrary AI systems. Before applying a correction, verify that the upstream model and assumptions match the validated setting.

Where supported, compare:

- naive two-step estimate;
- bias-corrected estimate and confidence interval;
- joint one-step measurement/outcome model;
- human-coded validation-sample estimate;
- transparent sensitivity analysis over plausible error rates.

Define the substantive decision boundary before comparing results. Do not define robustness as “still statistically significant.”

## 11. Cross-fitting and leakage control

Use training/validation/test separation or cross-fitting when the upstream model is trained on study data. The model generating a record's covariate should not be evaluated on a case used to tune that same model unless the inference method explicitly accounts for this dependence.

Flag as critical when the model sees the downstream outcome, future information, post-treatment data, or desired manuscript conclusion.

## 12. Required reporting table

Create one row per generated variable with:

- construct and unit;
- upstream model and version;
- source information and `C_i` definition;
- training/tuning/holdout samples;
- human validation sample and sampling design;
- error metrics with uncertainty;
- subgroup/time diagnostics;
- threshold and aggregation rule;
- repeated-run/model sensitivity;
- downstream naive estimate;
- measurement-aware estimate or sensitivity range;
- unresolved limitations.

Use `assets/ai-measure-validation-template.csv` as the starting schema.
