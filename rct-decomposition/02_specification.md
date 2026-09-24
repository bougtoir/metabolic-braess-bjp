# 仕様書：KOTHA Framework

## Knowledge-driven Observational-Trial Harmonization Approach

**RCTの構造的情報量不足を定量化し、観察研究との統合的エビデンス評価を実現するための方法論的枠組み**

---

## 1. フレームワーク概要

### 1.1 名称と略称

- **正式名称**: KOTHA Framework (Knowledge-driven Observational-Trial Harmonization Approach)
- **日本語名称**: KOTHA法 ― 知識駆動型観察研究・臨床試験調和アプローチ

### 1.2 目的

RCT（ランダム化比較試験）のメタ解析と観察研究のメタ解析との間に生じる結果の乖離について、その構造的原因を定量的に明らかにし、より適切なエビデンス評価と臨床推奨の策定を支援する。

### 1.3 背景にある課題

| 課題 | 説明 |
|---|---|
| RCTの代表性喪失 | 症例選別過程で高リスク群が排除され、実臨床母集団との乖離が生じる |
| イベント数不足 | 高リスク群の排除によりイベント発生率が低下し、検出力が不十分となる |
| メタ解析の不精確性 | パワー不足のRCT群を統合しても総情報量がOIS未満となり得る |
| 推奨の歪み | 「有意差なし」が「効果なし」と誤読され、有効な治療が推奨されない |

### 1.4 フレームワーク構成

KOTHA Frameworkは以下の3つのモジュールから構成される：

```
┌─────────────────────────────────────────────────────────────────┐
│                     KOTHA Framework                             │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │   Module K       │  │   Module T       │  │  Module H     │  │
│  │  Kontrafaktische │  │  Trial-Obs       │  │  Hermeneutic  │
│  │  Power           │  │  Bayesian        │  │  Guideline    │
│  │  Simulation      │  │  Integration     │  │  Interpreter  │
│  │                  │  │                  │  │               │  │
│  │ 反実仮想         │  │ 階層ベイズ       │  │ 解釈指針      │
│  │ パワー           │  │ エビデンス       │  │ モジュール    │
│  │ シミュレーション │  │ 統合             │  │               │  │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘  │
│           │                     │                    │          │
│           └─────────────────────┼────────────────────┘          │
│                                 │                               │
│                    ┌────────────▼────────────┐                  │
│                    │  統合的推奨判断         │                  │
│                    │  Integrated Recommendation│                 │
│                    └─────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

- **Module K** (Kontrafaktische Power Simulation): RCTの情報量不足を定量的に検証
- **Module T** (Trial-Observational Bayesian Integration): RCTと観察研究を階層ベイズで統合
- **Module H** (Hermeneutic Guideline Interpreter): 低イベントメタ解析の解釈指針を提供

---

## 2. Module K：反実仮想パワーシミュレーション

### 2.1 目的

後ろ向きデータを活用し、「もしRCTが実臨床に近いリスク分布で実施されていたら」という反実仮想シナリオを構築して、既存RCTの検出力不足を定量的に評価する。

### 2.2 入力データ仕様

| データ項目 | 必須/任意 | 説明 |
|---|---|---|
| 後ろ向きコホートデータ | 必須 | ベースライン共変量（年齢、併存症、重症度等）、フォローアップ期間、イベント発生有無・時点 |
| RCTのベースライン表 | 推奨 | 既存RCTの患者特性（Table 1相当）、リスク分布の比較に使用 |
| RCTの適格基準 | 推奨 | 後ろ向きデータに適用して「RCT的集団」を模擬するため |
| 想定治療効果（HR等） | 必須 | 感度分析用に複数設定（例：HR = 0.75, 0.80, 0.85） |

### 2.3 処理フロー

```
Step A: エンドポイントと時間枠の定義
    ↓
Step B: 後ろ向きデータでベースラインリスクモデル構築
    │  ├── 二値アウトカム → ロジスティック回帰 P(event|X)
    │  └── time-to-event → Cox比例ハザードモデル hazard(t|X)
    ↓
Step C: リスク分布シナリオの定義
    │  ├── Scenario 1（実臨床）: 後ろ向きデータの母集団全体
    │  ├── Scenario 2（RCT模擬）: RCT適格基準を適用した集団
    │  └── Scenario 3（改善案）: 高リスク層を一定割合含めた集団
    ↓
Step D: 治療効果の設定（感度分析）
    │  └── HR = 0.75 / 0.80 / 0.85（または領域に応じた妥当な範囲）
    ↓
Step E: Monte Carlo シミュレーション（1,000〜10,000回）
    │  ├── 各シナリオの分布からN人をサンプリング
    │  ├── 1:1ランダム化
    │  ├── 予測リスクに基づきイベント発生（治療群はHR適用）
    │  ├── 統計検定（log-rank / Cox / 比率差）
    │  └── p < α を満たした割合 = 推定パワー
    ↓
Step F: 結果の可視化と報告
```

### 2.4 出力仕様

| 出力項目 | 形式 | 用途 |
|---|---|---|
| シナリオ別リスクスコア分布 | ヒストグラム / 密度プロット | リスク分布の乖離を可視化 |
| シナリオ別期待イベント率 | 表 | イベント率低下の定量化 |
| シナリオ別期待イベント数 | 表（N・追跡期間固定） | 情報量不足の定量化 |
| シナリオ×効果量別推定パワー | 表 + ヒートマップ | 検出力不足の網羅的評価 |
| 必要症例数（パワー80%達成に要するN） | 表 | 適切な試験設計への示唆 |

### 2.5 妥当性検証

- リスクモデルのキャリブレーション（較正プロット、Hosmer-Lemeshow検定）
- 識別能の評価（C-statistic / AUC）
- RCTベースライン表との外部較正（利用可能な場合）
- 複数リスクモデル（ロジスティック回帰、ランダムフォレスト等）での感度分析

---

## 3. Module T：階層ベイズエビデンス統合

### 3.1 目的

RCT（高内的妥当性・低情報量）と観察研究（高情報量・バイアス懸念）を、バイアス構造を明示的にモデル化した上で統合し、意思決定に耐える効果推定を提供する。

### 3.2 基本モデル

各研究 *i* が報告する効果推定値を y_i（例：log(HR)）、標準誤差を s_i とする。

```
【観測モデル】
    y_i ~ Normal(θ_i, s_i²)

【構造モデル】
    θ_i = μ + u_i + b_i

    μ   : 全体の平均治療効果（推定の中核パラメータ）
    u_i : 研究間の真のばらつき（heterogeneity）
          u_i ~ Normal(0, τ²)
    b_i : 研究デザイン由来のバイアス項
          - RCT:       b_i ~ Normal(0, σ_RCT²)    [σ_RCT は小さい]
          - 観察研究:  b_i ~ Normal(δ, σ_OBS²)    [δ, σ_OBS は大きい]
```

### 3.3 観察研究の割引手法

以下の3手法を実装し、感度分析で比較する：

| 手法 | 概要 | パラメータ |
|---|---|---|
| **Evidence class別バイアス分布** | RCTと観察研究でb_iの事前分布を変える | δ, σ_RCT, σ_OBS |
| **Power prior / Discounting** | 観察研究の尤度に重みα（0〜1）を付与 | α（α=0で無視、α=1で同等） |
| **Robust mixture prior** | 観察研究の情報を取り込むが、矛盾時は自動的に影響を弱める | 混合比率、各成分の分散 |

### 3.4 入力データ仕様

| データ項目 | 形式 | 説明 |
|---|---|---|
| RCT効果推定値 | log(HR) or log(OR) + SE | 各RCTの点推定値と標準誤差 |
| 観察研究効果推定値 | 同上 | 各観察研究の点推定値と標準誤差 |
| 研究デザイン分類 | カテゴリ（RCT / コホート / ケースコントロール等） | バイアス項の事前分布割当に使用 |
| （任意）リスク・オブ・バイアス評価 | スコアまたはカテゴリ | 観察研究の割引程度の調整に使用 |

### 3.5 出力仕様

| 出力項目 | 形式 | 用途 |
|---|---|---|
| μ の事後分布 | 分布（中央値、95% CrI） | 統合された治療効果の推定 |
| P(HR < 1) | 確率値 | 治療有効確率 |
| P(HR < 臨床的閾値) | 確率値 | 臨床的に意味のある効果の確率 |
| 予測分布 | 分布 | 新規研究が出た場合の予測 |
| リスク層別絶対効果 | ARR / NNT | ベースラインリスクを入れた絶対効果 |
| 感度分析結果 | 割引手法別の推定値比較 | 結論の頑健性評価 |

### 3.6 実装仕様

- **推定方法**: Markov Chain Monte Carlo (MCMC) ― Stan / JAGS / PyMC
- **収束診断**: Rhat < 1.05、有効サンプルサイズ > 1000
- **事前分布の選択**: 弱情報事前分布を基本とし、感度分析で情報的事前分布も検討
- **モデル比較**: WAIC / LOO-CV による適合度評価

---

## 4. Module H：低イベントメタ解析の解釈指針

### 4.1 目的

ガイドライン作成委員会およびシステマティックレビュー著者向けに、低イベントRCTメタ解析の結果を適切に解釈するためのチェックリスト型指針を提供する。

### 4.2 チェックリスト仕様

```
CHECK 1: 情報量の評価
├── 総イベント数を明示する
├── OIS（Optimal Information Size）を算出する
│   └── OIS = 必要イベント数（D）を通常のRCT設計と同じ公式で算出
├── 総イベント数 < OIS → 「不精確（imprecision）」として格下げ
└── 結論を「未確定」として扱う

CHECK 2: 信頼区間の臨床的評価
├── CIが「臨床的に重要な利益」と「無益」を跨いでいるか評価
├── 例：RR 0.75〜1.05 → 利益の可能性が残る
└── CIの幅自体が結論の確実性を示す

CHECK 3: 代表性（Indirectness）の評価
├── 組み入れられた患者群と推奨対象集団の乖離を評価
├── 高リスク群が除外されていないか確認
├── Module K の結果を参照可能
└── 乖離がある場合は直接性の問題として明示

CHECK 4: 試験逐次解析（TSA）
├── 累積メタ解析にTSA境界を適用
├── 情報分画（information fraction）を算出
├── TSA境界未到達 → 「結論は早計」と判定
└── 低イベントでの「有意差なし」のリスクを定量化

CHECK 5: 推奨表現の標準化
├── 「推奨しない」→ 避ける
├── 推奨表現：「現時点のRCTは情報量不足で結論不能。
│    高リスク群では利益の可能性があり、追加研究が必要」
├── 少なくとも条件付き推奨の余地を残す
└── Module T の結果がある場合はベイズ推定結果を併記
```

### 4.3 GRADE連携

既存のGRADEフレームワークとの整合性：

| GRADEドメイン | KOTHA Module Hでの追加評価 |
|---|---|
| Imprecision（不精確性） | OIS評価 + TSA による情報量不足の定量化 |
| Indirectness（非直接性） | Module K によるリスク分布乖離の定量的根拠 |
| Overall certainty | Module T による統合推定の併記（補助的エビデンス） |

### 4.4 出力形式

- ガイドライン委員会向け：構造化されたEvidence Profileテーブル（GRADE拡張版）
- SR著者向け：チェックリスト付き報告テンプレート
- 臨床家向け：推奨の確実性と条件を明示したサマリー

---

## 5. モジュール間の連携

### 5.1 統合ワークフロー

```
Phase 1: データ収集・準備
├── 対象とする臨床疑問の定義
├── 既存RCT・観察研究のシステマティック検索
├── 後ろ向きコホートデータの取得
└── 各研究のリスク・オブ・バイアス評価

Phase 2: Module K 実行
├── リスクモデル構築
├── シナリオ定義
├── パワーシミュレーション実行
└── 出力：RCTの情報量不足の定量的根拠

Phase 3: Module T 実行
├── 効果推定値の抽出
├── 階層ベイズモデルの構築・推定
├── 感度分析
└── 出力：統合された効果推定と治療有効確率

Phase 4: Module H 適用
├── チェックリストに基づく評価
├── Module K・T の結果を統合
├── 推奨表現の策定
└── 出力：エビデンスプロファイルと推奨文

Phase 5: 統合的推奨判断
├── 3モジュールの結果を統合
├── 条件付き推奨の妥当性評価
└── 追加研究のデザイン提言（Module K による最適設計の示唆）
```

### 5.2 モジュール間のデータフロー

```
Module K ──→ Module H
 │  リスク分布乖離の定量的根拠（CHECK 3に利用）
 │  パワー不足の定量的根拠（CHECK 1, 4に利用）
 │
Module T ──→ Module H
 │  統合効果推定（CHECK 5の推奨表現に利用）
 │  治療有効確率（条件付き推奨の根拠に利用）
 │
Module K ──→ Module T
    リスク層別のベースラインイベント率（絶対効果算出に利用）
```

---

## 6. 適用範囲と制約

### 6.1 適用が想定される臨床状況

- 後ろ向き研究では有意な治療効果が示されるが、RCTメタ解析では有意差がない状況
- RCTの対象集団が実臨床母集団と乖離している疑いがある場合
- イベント発生率が低い（稀なアウトカム、短い追跡期間）RCTが多い場合
- ガイドライン作成において「エビデンス不十分」と判定されそうな治療法の再評価

### 6.2 制約事項

- Module K は後ろ向きデータの質とアクセス可能性に依存する
- Module T の結果は観察研究のバイアス構造の仮定に敏感であり、感度分析が必須
- Module H は既存のガイドライン作成プロセスとの合意形成が必要
- 本フレームワークは「治療が効くことの証明」ではなく「RCTの情報量不足の検証」である

### 6.3 倫理的考慮

- 本フレームワークの使用が、エビデンスの質の低い治療の不適切な推奨につながらないよう、Module T の割引パラメータの設定には保守的な立場を推奨する
- ガイドライン委員会での透明な議論と、方法論の開示が必須

---

## 7. 技術的要件

### 7.1 ソフトウェア環境

| コンポーネント | 推奨ツール |
|---|---|
| リスクモデル構築（Module K） | R (survival, rms) / Python (lifelines, scikit-learn) |
| パワーシミュレーション（Module K） | R / Python (NumPy, SciPy) |
| 階層ベイズモデル（Module T） | Stan (rstan/cmdstanpy) / PyMC / JAGS |
| TSA（Module H） | R (rtsa) / TSA software |
| メタ解析（共通） | R (meta, metafor) / Python (pymare) |
| 可視化 | R (ggplot2) / Python (matplotlib, seaborn) |

### 7.2 再現性要件

- すべての解析コードはバージョン管理下に置く
- 乱数シード（seed）を固定して再現性を保証
- 事前分布・割引パラメータ等の選択根拠を文書化
- 感度分析の全結果をサプリメントとして公開

---

## 8. 改訂履歴

| 版 | 日付 | 変更内容 |
|---|---|---|
| 0.1 | 2026-03-23 | 初版作成（議論整理に基づく） |

---

# English Translation

---

# Specification: KOTHA Framework

## Knowledge-driven Observational-Trial Harmonization Approach

**A methodological framework for quantifying the lack of structural information in RCTs and realizing integrated evidence evaluation with observational studies**

---

## 1. Framework overview

### 1.1 Names and abbreviations

- **Official name**: KOTHA Framework (Knowledge-driven Observational-Trial Harmonization Approach)
- **Japanese name**: KOTHA method - Knowledge-driven observational research/clinical trial harmonization approach

### 1.2 Purpose

We will quantitatively clarify the structural causes of the disparity in results between meta-analyses of RCTs (randomized controlled trials) and meta-analyses of observational studies, and support more appropriate evidence evaluation and formulation of clinical recommendations.

### 1.3 Background issues

| Assignment | Explanation |
|---|---|
| Loss of representativeness of RCT | High-risk groups are excluded in the case selection process, resulting in a discrepancy with the actual clinical population |
| Insufficient number of events | Exclusion of high-risk groups reduces event rate and insufficient power |
| Inaccuracy of meta-analysis | Even when underpowered RCTs are combined, the total amount of information can be less than the OIS |
| Distortion of recommendations | “No significant difference” is misread as “no effect” and effective treatments are not recommended |

### 1.4 Framework configuration

KOTHA Framework consists of the following three modules:

````
┌──────────────────────────────────────────────────────────────┐
│ KOTHA Framework │
│ │
│ ┌──────────────────┐ ┌────────────────────┐ ┌────────────────┐ │
│ │ Module K │ │ Module T │ │ Module H │ │
│ │ Kontrafaktische │ │ Trial-Obs │ │ Hermeneutic │
│ │ Power │ │ Bayesian │ │ Guideline │
│ │ Simulation │ │ Integration │ │ Interpreter │
│ │ │ │ │ │ │ │
│ │ Counterfactual Hypothesis │ │ Hierarchical Bayes │ │ Interpretation Guidelines │
│ │ Power │ │ Evidence │ │ Module │
│ │ Simulation │ │ Integration │ │ │ │
│ └────────┬──────────┘ └────────┬──────────┘ └────────┬────────┘ │
│ │ │ │ │
│ └──────────────────────┼────────────────────┘ │
│                                 │                               │
│                    ┌────────────▼────────────┐                  │
│                    │  統合的推奨判断         │                  │
│                    │  Integrated Recommendation│                 │
│                    └─────────────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
````

- **Module K** (Kontrafaktische Power Simulation): Quantitatively verify the lack of information in RCTs
- **Module T** (Trial-Observational Bayesian Integration): Integrate RCTs and observational studies with hierarchical Bayesian integration
- **Module H** (Hermeneutic Guideline Interpreter): Provides interpretive guidelines for low-event meta-analysis

---

## 2. Module K: Counterfactual virtual power simulation

### 2.1 Purpose

Using retrospective data, we will quantitatively evaluate the lack of detection power of existing RCTs by constructing a hypothetical counterfactual scenario of ``what if RCTs were conducted with a risk distribution close to that of actual clinical practice.''

### 2.2 Input data specifications

| Data Item | Required/Optional | Description |
|---|---|---|
| Retrospective cohort data | Required | Baseline covariates (age, comorbidities, severity, etc.), follow-up period, event occurrence/time point |
| Baseline table of RCT | Recommended | Used to compare patient characteristics (equivalent to Table 1) and risk distribution of existing RCTs |
| Eligibility criteria for RCTs | Recommendations | To simulate an “RCT-like population” by applying to retrospective data |
| Expected treatment effect (HR, etc.) | Required | Multiple settings for sensitivity analysis (e.g. HR = 0.75, 0.80, 0.85) |

### 2.3 Processing flow

````
Step A: Define endpoints and timeframes
    ↓
Step B: Build a baseline risk model using retrospective data
│ ├── Binary outcome → Logistic regression P(event|X)
    │ └── time-to-event → Cox proportional hazard model hazard(t|X)
    ↓
Step C: Define risk distribution scenario
    │ ├── Scenario 1 (actual clinical practice): Entire population of retrospective data
    │ ├── Scenario 2 (RCT simulation): Population applying RCT eligibility criteria
    │ └── Scenario 3 (improvement proposal): Population that includes a certain percentage of high-risk groups
    ↓
Step D: Setting the treatment effect (sensitivity analysis)
    │ └── HR = 0.75 / 0.80 / 0.85 (or a reasonable range depending on the area)
    ↓
Step E: Monte Carlo simulation (1,000 to 10,000 times)
    │ ├── Sampling N people from the distribution of each scenario
    │ ├── 1:1 randomization
    │ ├── Event occurrence based on predicted risk (HR applied for treatment group)
    │ ├── Statistical test (log-rank / Cox / proportion difference)
    │ └── Proportion that satisfies p < α = estimated power
    ↓
Step F: Visualize and report results
````

### 2.4 Output specifications
| Output items | Format | Purpose |
|---|---|---|
| Risk score distribution by scenario | Histogram/density plot | Visualize deviations in risk distribution |
| Expected event rate by scenario | Table | Quantification of event rate reduction |
| Expected number of events by scenario | Table (N, fixed tracking period) | Quantification of lack of information |
| Estimated power by scenario x effect size | Table + heat map | Comprehensive evaluation of insufficient power |
| Required number of cases (N required to achieve 80% power) | Table | Suggestions for appropriate study design |

### 2.5 Validation

- Calibration of risk models (calibration plots, Hosmer-Lemeshow test)
- Evaluation of discrimination ability (C-statistic / AUC)
- External calibration with RCT baseline table (if available)
- Sensitivity analysis with multiple risk models (logistic regression, random forest, etc.)

---

## 3. Module T: Hierarchical Bayesian Evidence Integration

### 3.1 Purpose

It integrates RCTs (high internal validity, low information content) and observational studies (high information content, bias concerns) after explicitly modeling the bias structure to provide decision-proof effect estimates.

### 3.2 Basic model

Let y_i be the effect estimate reported by each study *i* (e.g. log(HR)), and let s_i be the standard error.
````
[Observation model]
    y_i ~ Normal(θ_i, s_i²)

[Structural model]
    θ_i = μ + u_i + b_i

    μ: Overall average treatment effect (estimated core parameter)
    u_i : true variation between studies (heterogeneity)
          u_i ~ Normal(0, τ²)
    b_i : Bias term derived from research design
          - RCT: b_i ~ Normal(0, σ_RCT²) [σ_RCT is small]
          - Observational study: b_i ~ Normal(δ, σ_OBS²) [δ, σ_OBS is large]
````

### 3.3 Discounting methods for observational studies

We will implement the following three methods and compare them in sensitivity analysis:

| Method | Overview | Parameters |
|---|---|---|
| **Bias distribution by evidence class** | Changing the prior distribution of b_i in RCTs and observational studies | δ, σ_RCT, σ_OBS |
| **Power prior / Discounting** | Assign weight α (0 to 1) to the likelihood of observational studies | α (ignored if α=0, equivalent if α=1) |
| **Robust mixture prior** | Incorporates information from observational studies, but automatically weakens influence in case of discrepancies | Mixture ratio, variance of each component |

### 3.4 Input data specifications

| Data item | Format | Description |
|---|---|---|
| RCT effect estimate | log(HR) or log(OR) + SE | Point estimate and standard error for each RCT |
| Observational study effect estimates | Same as above | Point estimates and standard errors for each observational study |
| Research design classification | Categories (RCT / Cohort / Case-control, etc.) | Used for prior distribution assignment of bias terms |
| (Optional) Risk of bias assessment | Score or category | Used to adjust the degree of discount for observational studies |

### 3.5 Output specifications

| Output items | Format | Purpose |
|---|---|---|
| Posterior distribution of μ | Distribution (median, 95% CrI) | Estimation of pooled treatment effect |
| P(HR < 1) | Probability value | Treatment effectiveness probability |
| P(HR < clinical threshold) | Probability value | Probability of clinically meaningful effect |
| Prediction distribution | Distribution | Prediction when new research comes out |
| Absolute effect by risk stratification | ARR / NNT | Absolute effect including baseline risk |
| Sensitivity analysis results | Comparison of estimates by discounting method | Robustness evaluation of conclusions |

### 3.6 Implementation specifications

- **Estimation method**: Markov Chain Monte Carlo (MCMC) - Stan / JAGS / PyMC
- **Convergence diagnostic**: Rhat < 1.05, effective sample size > 1000
- **Prior distribution selection**: Based on weak information prior distribution, informative prior distribution is also considered in sensitivity analysis
- **Model comparison**: Goodness of fit evaluation by WAIC / LOO-CV

---

## 4. Module H: Interpretation guidelines for low-event meta-analysis

### 4.1 Purpose

We provide guideline committees and systematic review authors with a checklist of guidelines for appropriately interpreting the results of low-event RCT meta-analyses.

### 4.2 Checklist specifications

````
CHECK 1: Evaluate the amount of information
├── Specify the total number of events
├── Calculate OIS (Optimal Information Size)
│ └── OIS = Calculate the required number of events (D) using the same formula as for normal RCT design
├── Total number of events < OIS → Downgraded as “imprecision”
└── Treat the conclusion as “unconfirmed”

CHECK 2: Clinical evaluation of confidence intervals
├── Evaluate whether CI straddles the line between “clinically important benefit” and “futility”
├── Example: RR 0.75~1.05 → Possibility of profit remains
└── The width of the CI itself indicates the certainty of the conclusion

CHECK 3: Evaluation of representativeness (indirectness)
├── Evaluate the discrepancy between the included patient group and the recommended target population
├── Check whether high-risk groups are excluded
├── You can refer to the results of Module K
└── If there is a discrepancy, clarify it as a directness issue

CHECK 4: Test sequential analysis (TSA)
├── Applying TSA boundaries to cumulative meta-analysis
├── Calculate information fraction
├── TSA border not reached → Judgment that “conclusion is premature”
└── Quantifying the risk of “no significant difference” in low events

CHECK 5: Standardization of recommended expressions
├── “Not recommended” → Avoid
├── Recommended phrase: “The current RCT is inconclusive due to insufficient information.
│ Possible benefit in high-risk groups; additional research required.”
├── At least leave room for conditional recommendations
└── Bayesian estimation results are also included if results of Module T are available.
````

### 4.3 GRADE cooperation

Consistency with existing GRADE framework:

| GRADE domain | Additional evaluation with KOTHA Module H |
|---|---|
| Imprecision | Quantifying lack of information using OIS evaluation + TSA |
| Indirectness | Quantitative basis of risk distribution deviation using Module K |
| Overall certainty | Combined estimation with Module T (auxiliary evidence) |

### 4.4 Output format

- For guideline committees: Structured Evidence Profile table (GRADE extension)
- For SR authors: Report template with checklist
- For clinicians: summary with certainty and conditions for recommendations

---

## 5. Cooperation between modules

### 5.1 Integrated Workflow

````
Phase 1: Data collection/preparation
├── Definition of the target clinical question
├── Systematic search of existing RCTs/observational studies
├── Retrospective cohort data acquisition
└── Risk of bias assessment for each study

Phase 2: Module K execution
├── Risk model construction
├── Scenario definition
├── Power simulation execution
└── Output: Quantitative basis for insufficient information in RCTs

Phase 3: Module T execution
├── Extraction of effect estimates
├── Construction and estimation of hierarchical Bayesian models
├── Sensitivity analysis
└── Output: Integrated effect estimation and treatment effectiveness probability
Phase 4: Module H application
├── Evaluation based on checklist
├── Combined results of Module K・T
├── Formulation of recommended expressions
└── Output: Evidence profile and recommendations

Phase 5: Integrated recommendation judgment
├── Combined results of 3 modules
├── Validity evaluation of conditional recommendations
└── Design proposal for additional research (suggestions for optimal design using Module K)
````

### 5.2 Data flow between modules

````
Module K ──→ Module H
 │ Quantitative basis for risk distribution deviation (used for CHECK 3)
 │ Quantitative basis for power shortage (used for CHECK 1, 4)
 │
Module T ──→ Module H
 │ Integrated effect estimation (used for CHECK 5 recommendation expression)
 │ Probability of treatment effectiveness (used as basis for conditional recommendation)
 │
Module K ──→ Module T
    Baseline event rate by risk stratification (used to calculate absolute effect)
````

---

## 6. Scope and restrictions

### 6.1 Clinical situations where application is expected

- Retrospective studies show significant treatment effects, but RCT meta-analyses show no significant difference
- When it is suspected that the target population of the RCT deviates from the actual clinical population
- If there are many RCTs with low event rates (rare outcomes, short follow-up period)
- Re-evaluation of treatments that are likely to be judged as having “insufficient evidence” in guideline creation

### 6.2 Restrictions

- Module K depends on the quality and accessibility of retrospective data
- Module T results are sensitive to bias structure assumptions of observational studies and sensitivity analysis is required
- Module H requires consensus building with existing guideline creation process
- This framework is not ``proof that the treatment is effective'' but ``verification of the lack of information in RCTs''

### 6.3 Ethical considerations

- To ensure that the use of this framework does not lead to inappropriate recommendations for treatments with low-quality evidence, we recommend a conservative stance when setting discount parameters for Module T.
- Transparent discussion at the guideline committee and disclosure of methodology is essential

---

## 7. Technical requirements

### 7.1 Software environment

| Components | Recommended tools |
|---|---|
| Risk model construction (Module K) | R (survival, rms) / Python (lifelines, scikit-learn) |
| Power simulation (Module K) | R / Python (NumPy, SciPy) |
| Hierarchical Bayesian Model (Module T) | Stan (rstan/cmdstanpy) / PyMC / JAGS |
| TSA (Module H) | R (rtsa) / TSA software |
| Meta-analysis (common) | R (meta, metafor) / Python (pymare) |
| Visualization | R (ggplot2) / Python (matplotlib, seaborn) |

### 7.2 Reproducibility requirements

- Keep all analysis code under version control
- Fixed random number seed to ensure reproducibility
- Document the basis for selecting prior distributions, discount parameters, etc.
- Full results of sensitivity analysis published as a supplement

---

## 8. Revision history

| Edition | Date | Changes |
|---|---|---|
| 0.1 | 2026-03-23 | First edition created (based on discussion) |
