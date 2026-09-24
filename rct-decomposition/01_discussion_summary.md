# 議論整理：RCT分解 ― 後ろ向き研究とRCTの乖離問題

## 1. 問題の全体像

### 1.1 出発点となる臨床的観察

ある治療法A（vs 標準治療B）について、以下の矛盾が生じている：

| エビデンスの種類 | 結果 |
|---|---|
| 後ろ向き研究（観察研究）のメタ解析 | 治療法Aが**有意に優れる** |
| RCTのメタ解析 | **有意差なし** |

この矛盾は臨床研究において珍しくなく、従来は「観察研究のバイアス」として片付けられてきた。しかし、本議論ではこの矛盾の構造的原因がRCT側の**設計上の情報量不足**にあるという仮説を提唱する。

### 1.2 因果連鎖の構造（5段階仮説）

```
①  RCTの症例選別過程で母集団の代表性が失われる
        ↓
②  イベント（主要アウトカム）は高リスク群（併存症等）に集中するが、
    これらの患者がスクリーニング・除外基準・同意取得の段階で排除される
        ↓
③  本来、RCT企画段階で②を見積もりに入れ、
    リスク階層の設定や症例数の増加が必要
        ↓
④  現状③が十分に行われていないため、
    パワー不足のRCTが量産され、そのメタ解析でも有意差が出ない
        ↓
⑤  結果として、本来推奨されるべき治療法Aが
    「エビデンス不十分」として推奨に至らない
```

---

## 2. 論点の整理

### 2.1 RCTの代表性喪失メカニズム（①②）

RCTが実臨床の母集団から乖離する主な経路：

- **除外基準による排除**: 安全性・均質性確保のため高リスク患者を除外
- **施設選択バイアス**: 参加施設が大学病院等に偏り、患者層が限定
- **同意取得バイアス**: 高齢・重症・認知機能低下患者は同意取得が困難
- **実施可能性フィルター**: プロトコル遵守が困難な患者の事前排除

結果として、RCT登録集団は「低〜中リスクのきれいな集団」になりやすい。

### 2.2 イベント率低下とパワー不足の関係（③④）

- time-to-event解析における必要イベント数（D）の公式：
  - **D ≈ 4 × (Z_{α/2} + Z_β)² / (log(HR))²**
- 例：HR=0.80、α=0.05（両側）、β=0.20 → **約630イベント必要**
- 例：HR=0.85 → **約1,190イベント必要**

高リスク群の排除により期待イベント率が下がると：
- 同一症例数での達成イベント数が減少
- 必要な追跡期間が延長
- 結果として**情報量（information size）不足**が生じる

### 2.3 メタ解析への波及（④⑤）

個々のRCTが情報量不足 → メタ解析で統合しても：
- 推定値は有利方向でもCIが広い
- 総イベント数がOIS（Optimal Information Size）に満たない
- 「有意差なし」が「効果なし」と誤読される

---

## 3. 既存の対策手法とその普及度

| 手法 | 概要 | ③への有効性 | 普及度 |
|---|---|---|---|
| 層別設計（Stratified design） | リスク因子で層別しランダム化 | 中 | 軽度な層別は一般的、イベント駆動の層別は稀 |
| 濃縮デザイン（Enrichment design） | 高リスク群を意図的に多く組み入れ | 高 | FDA/EMA推奨だが実臨床RCTでは限定的 |
| イベント駆動型（Event-driven design） | 必要イベント数到達を終了条件に | 高 | 循環器・腫瘍では一般的、他領域では稀 |
| 適応的デザイン（Adaptive design） | 中間解析でサンプルサイズ等を調整 | 高 | 理論的に有力だが複雑で普及不十分 |
| 外部データ活用（External data informed） | 後ろ向きデータで設計を定量化 | 非常に高 | 理想的だが実務では非常に稀 |
| 実用的試験（Pragmatic trial） | 除外基準最小化、実臨床に近い設計 | 高 | 方向性は推奨されるが標準とは言えない |

**共通の結論**: 方法論は存在するが、一般的には十分に行われていない。

---

## 4. 提案された3つのアプローチ

元の議論で提案された3本柱を以下に整理する：

### 柱1: Counterfactual Power Simulation（反実仮想パワーシミュレーション）
- 後ろ向きデータを用いて「もしRCTが実臨床のリスク分布だったら」を定量化
- RCTの情報量不足を事前計画・事後評価の両面で検証
- 出力：シナリオ別の期待イベント率・推定パワー・必要症例数

### 柱2: 階層ベイズモデルによるエビデンス統合
- RCT（高内的妥当性・低情報量）と観察研究（高情報量・バイアス懸念）を統合
- 観察研究にバイアス項・割引を導入し、意思決定に耐える推定を提供
- 出力：治療有効確率 P(HR<1)、予測分布、リスク層別絶対効果

### 柱3: 低イベントRCTメタ解析の解釈指針
- 「有意差なし ≠ 効果なし」を制度的に担保
- OIS評価、TSA（試験逐次解析）、推奨表現の改善
- ガイドライン作成委員会での運用型を提供

---

## 5. 議論の位置づけ

本議論は以下の学術的文脈に位置する：

- **Evidence-Based Medicine（EBM）の限界論**: エビデンス・ピラミッドの頂点にあるRCTメタ解析が、設計上の構造的バイアスにより不完全な情報を提供している問題
- **Evidence-Biased Medicine**: RCTへの過度な依存が、実臨床で有効な治療の推奨を妨げるという批判
- **Trial Design Methodology**: RCTの企画段階で外部データを定量的に活用する新しいパラダイム
- **Bayesian Evidence Synthesis**: 異なるエビデンス源を適切に重み付けして統合する統計的枠組み

---

## 6. 次のステップ

1. 上記3本柱を統合した方法論フレームワークの命名と定式化 → **仕様書**
2. 仮想的な臨床シナリオでの数値例の構築
3. 論文としての執筆 → **ドラフト**

---

# English Translation

---

# Arranging the discussion: RCT decomposition - Discrepancy between retrospective research and RCT

## 1. Big picture of the problem

### 1.1 Clinical observations as a starting point

The following discrepancies arise regarding treatment A (vs. standard treatment B):

| Type of evidence | Results |
|---|---|
| Meta-analysis of retrospective studies (observational studies) | Treatment A is **significantly superior** |
| Meta-analysis of RCTs | **No significant difference** |

This discrepancy is not uncommon in clinical research and has traditionally been dismissed as ``observational study bias.'' However, in this discussion, we propose the hypothesis that the structural cause of this discrepancy lies in the lack of information in the design of the RCT.

### 1.2 Structure of causal chain (5-step hypothesis)

````
① Representativeness of the population is lost during the RCT case selection process
        ↓
② Events (main outcomes) are concentrated in high-risk groups (comorbidities, etc.);
    These patients will be excluded at the screening, exclusion criteria, and consent stages.
        ↓
③ Originally, ② was included in the estimate at the RCT planning stage.
    It is necessary to establish risk stratification and increase the number of cases.
        ↓
④ Currently, ③ is not being carried out sufficiently.
    A large number of underpowered RCTs have been produced, and even their meta-analyses do not show significant differences.
        ↓
⑤ As a result, treatment A that should have been recommended was
Not recommended due to “insufficient evidence”
````

---

## 2. Organizing the points at issue

### 2.1 Mechanism of RCT loss of representativeness (①②)

Main ways RCTs deviate from real-world populations:

- **Exclusion based on exclusion criteria**: Exclude high-risk patients to ensure safety and homogeneity
- **Facility selection bias**: Participating facilities are biased toward university hospitals, etc., and the patient population is limited
- **Consent Obtaining Bias**: Obtaining consent is difficult for elderly, severely ill, and cognitively impaired patients.
- **Feasibility filter**: Preliminary exclusion of patients who have difficulty complying with the protocol

As a result, the RCT population tends to be a "clean population with low to moderate risk."

### 2.2 Relationship between event rate decline and power shortage (③④)

- Formula for required number of events (D) in time-to-event analysis:
  - **D ≈ 4 × (Z_{α/2} + Z_β)² / (log(HR))²**
- Example: HR=0.80, α=0.05 (both sides), β=0.20 → **Approximately 630 events required**
- Example: HR=0.85 → **Approximately 1,190 events required**

When the expected event rate decreases due to exclusion of high-risk groups:
- The number of events achieved with the same number of cases has decreased
- Extended follow-up period required
- As a result, **insufficient information size** occurs.
### 2.3 Impact on meta-analysis (④⑤)

Insufficient information from individual RCTs → Even if combined through meta-analysis:
- The estimated value has a wide CI even in the favorable direction
- Total number of events is less than OIS (Optimal Information Size)
- "No significant difference" is misread as "no effect"

---

## 3. Existing countermeasure methods and their prevalence

| Method | Overview | Effectiveness for ③ | Popularity |
|---|---|---|---|
| Stratified design | Stratification and randomization by risk factors | Medium | Mild stratification is common, event-driven stratification is rare |
| Enrichment design | Intentionally includes many high-risk groups | High | Recommended by FDA/EMA, but limited in real-world RCTs |
| Event-driven design | Reaching the required number of events as a termination condition | High | Common in cardiovascular systems and oncology, rare in other fields |
| Adaptive design | Adjust sample size, etc. through interim analysis | High | Theoretically powerful, but complex and not widely used |
| External data informed | Quantifying design with retrospective data | Very high | Ideal but extremely rare in practice |
| Pragmatic trial | Minimize exclusion criteria, design close to actual clinical practice | High | Direction is recommended but cannot be said to be the standard |

**Common conclusion**: Methodologies exist, but are generally not well-practiced.

---

## 4. Three proposed approaches

The three pillars proposed in the original discussion are summarized below:

### Pillar 1: Counterfactual Power Simulation
- Quantify "what if RCT was the actual clinical risk distribution" using retrospective data
- Verify the lack of information in RCTs through both pre-planning and post-evaluation
- Output: Expected event rate, estimated power, and required number of cases by scenario

### Pillar 2: Evidence synthesis with hierarchical Bayesian models
- Integrating RCT (high internal validity, low information content) and observational studies (high information content, concerns about bias)
- Introducing bias terms and discounting into observational studies to provide decision-proof estimates
- Output: Treatment effectiveness probability P(HR<1), predicted distribution, absolute effect by risk stratification

### Pillar 3: Interpretation guidelines for low-event RCT meta-analyses
- Systematically guarantees “no significant difference ≠ no effect”
- Improved OIS evaluation, TSA (Test Sequential Analysis), and recommendation expressions
- Provide operational format for guideline creation committee

---

## 5. Positioning of the discussion

This discussion is situated in the following academic context:
- **Limitations of Evidence-Based Medicine (EBM)**: The problem that RCT meta-analyses at the top of the evidence pyramid provide incomplete information due to structural biases in their design.
- **Evidence-Biased Medicine**: Criticism that over-reliance on RCTs hinders the recommendation of effective treatments in actual clinical practice.
- **Trial Design Methodology**: A new paradigm that quantitatively utilizes external data during the RCT planning stage
- **Bayesian Evidence Synthesis**: A statistical framework that appropriately weights and integrates different sources of evidence.

---

## 6. Next steps

1. Naming and formulation of a methodological framework that integrates the above three pillars → **Specification**
2. Construction of numerical examples in hypothetical clinical scenarios
3. Writing as a paper → **Draft**
