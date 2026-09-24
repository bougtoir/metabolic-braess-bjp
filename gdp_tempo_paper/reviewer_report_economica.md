# Economica 査読者目線レビュー報告

> **Post-implementation note (final submission).** The issues below were addressed in the `devin/1786994614-economica-submission` branch and the public mirror `bougtoir/gdp-tempo-paper`. Final package: manuscript ≈ 8,450 words / 33 pages, **5 main figures + 13 supplementary figures**, **2 main tables + 10 supplementary tables**, `table12_monte_carlo.csv` uses `n_rep_valid = 500` with SE/95 % CI columns, and all Economica format checks pass.
>
> **Round-2 reviewer-perspective fixes.** A second pass tightened (1) reference list alphabetical order and Harvard ALL CAPS formatting for institutional authors, (2) cover-letter wording from “revalues national wealth” to “revalues produced capital by up to 1.1 per cent (total wealth by up to 0.3 per cent)”, (3) abstract/highlights/cover-letter direction of the 1.7 pp TFP/labour-share adjustment to “TFP falls / labour share rises”, and (4) introduction wording on Goldstein, Lutz, and Scherbov (2003) for consistency with the demographic-tempo literature section.

**査読対象**: `manuscript_en.md` / 生成済み `manuscript_en.pdf`（33 ページ、5 main figures + 13 supplementary figures、2 main tables + 10 supplementary tables）  
**提出先想定**: Economica（Wiley / LSE、一般経済学誌、abstract ≤100 語、PDF のみ）  
**評価軸**: 致命度（desk reject / major revision リスク）、修正効果（採択可能性向上）、実行可能性（現有データ・コードで対応可能か）

---

## 全体的所見

テーマ自体は成長会計・計測の一般経済学誌として成立するが、現稿は（1）**本文・図表が過剰に技術的**（33 ページ、5 主図 + 13 補助図、2 主表 + 10 補助表）で Economica の一般読者向け体裁を超過しうる、（2）**アブストラクト・カバーレター・本文の数値主張にデータと食い違う箇所がある**、（3）**PWT 資本ストックと無形資本（R&D）の重複計上リスクが説明不足**、という 3 点が目立つ。機械的フォーマット（Roman 見出し、ALL CAPS 参考文献、ページ番号、font 埋め込み、縦線なし表など）は合格している。投稿前に「substantial revise & resubmit」を見越した構造再編が必要。

---

## 最優先（投稿前に必須）

### 1. アブストラクト・ハイライト・カバーレターの数値主張をデータと一致させる
- **領域**: 原稿 / 主張の強さ
- **致命度**: 高 / **修正効果**: 高 / **実行可能性**: 高
- **根拠**:
  - Abstract (`manuscript_en.md:35`)、Highlights (`:45`)、Cover letter (`cover_letter/cover_letter_en.md:18`) に「revalues national wealth by up to one per cent」とある。
  - Table 8 (`tables/table8_counterfactual_narrative.csv`) の total wealth 調整幅 `tow_gap_pct` の最大値は **0.3%**（Netherlands）。Produced capital 調整幅 `pca_gap_pct` の最大値は **1.1%**（Netherlands）。
  - したがって「national wealth」で 1% は **誤り**。正しくは「produced capital by up to 1%」または「total wealth by up to 0.3%」。
  - また Introduction (`manuscript_en.md:59`) に「tempo drift alone accounts for up to 30% of TFP-growth variance」とあるが、Table 6 (`tables/table6_tempo_artifact.csv`) の `Tempo share %` 最大値は **13.8%**（New Zealand）、`Joint share %` 最大値は **29.7%**（France）。「tempo drift alone」で 30% は誤り。joint correction で 30% か、tempo alone で 14% に修正。
- **修正案**: 上記箇所を Table 6 / Table 8 の実数値に置換。可能であれば「produced capital」のみを主張に使い、total wealth は 0.3% と注記。

### 2. PWT `rnna` と無形資本 `K_I`（R&D）の重複計上リスクを解消する
- **領域**: 統計設計 / 主張の強さ
- **致命度**: 高 / **修正効果**: 高 / **実行可能性**: 中
- **根拠**:
  - Methods (`manuscript_en.md:141`) で tangible stock として PWT `rnna` を使用し、`K_I` は WDI の R&D 支出から構築。
  - World Bank CWON 文書によれば produced capital には intellectual property products を含む (`asset_composition` 参照: https://www.worldbank.org/en/publication/the-changing-wealth-of-nations)。
  - PWT `rnna` も produced capital 全体を含む構成（capital detail の 4 asset クラスに「other assets」として IPP を含む可能性）。
  - `K_I` を R&D ベースで `rnna` に足し、さらに CWON produced capital との一致を目標にしている場合、**PWT / CWON 双方ですでに R&D/IPP が含まれているなら二重計上**となる。
- **修正案**: Data section において、`rnna` の資産範囲と CWON `NW.PCA.TO` の資産範囲を明確に比較。`K_I` が「PWT / CWON に未含まれる無形資本の追加シェア」であることを実証または仮定として提示。二重計上の可能性を排除できない場合、推定値の解釈を「CWON-PWT 間のカバレッジ差の代理」に留める。

### 3. 本文を Economica 向けに圧縮・再構成する
- **領域**: 原稿 / 図表
- **致命度**: 高 / **修正効果**: 高 / **実行可能性**: 中〜高
- **根拠**:
  - 現稿は **12,125 語・66 ページ・18 図・12 表**で、Economica の「一般読者向け」の体裁を大きく超過。典型的な Economica 論文は 25〜40 ページ、5〜8 図表程度。
  - 第 V 章のサブセクション（V.1〜V.17）がモデル比較・頑健性・将来シミュレーション・クラスター・Monte Carlo など技術的要素を網羅し、経済学的問いが埋もれている。
- **修正案**:
  - 目標: **本文 8,000 語前後、図表 5〜7 点**に圧縮。
  - 本文に残す: Abstract, Introduction, 最簡の理論（M0, M2, M4 / M_obs）, Data, Table 2（M0-M4 比較）, Figure 3（PIM-CWON 軌跡）, Figure 10-12（K 水準・TFP・労働分配率への帰結）, Figure 13（6 カ国の Solow 残差分解）, Table 7（歴史的エピソード）, Discussion, Conclusion。
  - Appendix / Supporting Information へ移す: M1/M3 の詳細、Figure 4 γ_price、Figure 5 concept（本文ではテキストで簡潔に説明）、Figure 6-9 RPIM / conditional OOS / R&D 回帰、Table 3-4 RPIM / extended OOS、Figure 14-18 counterfactual wealth / future scenarios / clusters / δ robustness / Monte Carlo、Table 8-12。Wiley 系は Supporting Information を受け付ける。受け付けない場合は更に選別。

### 4. カバーレターの図表カウントと主張を修正する
- **領域**: 原稿
- **致命度**: 中〜高 / **修正効果**: 高 / **実行可能性**: 高
- **根拠**: Cover letter (`cover_letter/cover_letter_en.md:30`) は「fourteen figures and six tables」とあるが、実際は 18 figures / 12 tables。編集者が数えれば即座に不審。
- **修正案**: 実数に直すか、再構成後のカウントに直す。

---

## 高優先

### 5. Monte Carlo の反復回数を増やし精度を報告する
- **領域**: 統計設計
- **致命度**: 中 / **修正効果**: 高 / **実行可能性**: 中
- **根拠**:
  - `scripts/additional_analyses_economica.py:669` の `n_rep=30` で Table 12 (`table12_monte_carlo.csv`) が作成されている。各パラメータセルあたり 30 回は少なく、RMSE や bias の推定変動が大きい。
  - Section V.17 は「joint identification is statistically sharp in the empirically relevant region」と結論づけているが、その根拠が 30 回では薄い。
- **修正案**: `n_rep` を 500〜1000 に増やし、Table 12 における `n_rep_valid` の列を SE または 95% CI で補完。Figure 18 に誤差バーを追加。

### 6. M_obs（zero free parameter）の資産別ラグ仮定に対する頑健性を主張に組み込む
- **領域**: 統計設計 / 主張の強さ
- **致命度**: 中 / **修正効果**: 高 / **実行可能性**: 中
- **根拠**:
  - M_obs の gestation lag は `asset_specific_tempo.py:61` の `ASSET_MU`（Dwellings 2.0、ICT 0.3、IPP 3.0 等）に依存。コードコメントには出典が書かれているが、本文 (`manuscript_en.md:154`) では「literature-based gestation lags」で済まされている。
  - 同コードには既に `±50%` の lag uncertainty テスト (`asset_specific_tempo.py:477` 付近) があるが、主稿には結果が入っていない。
- **修正案**: Methods で資産別ラグの根拠文献を明示。M_obs の K-gap / TFP shift が `ASSET_MU` の `±50%` 変動でどれだけ変わるかを Appendix Figure / Table に追加。

### 7. Table 5 の計測帰結に不確実性区間を加える
- **領域**: 統計設計 / 図表
- **致命度**: 中 / **修正効果**: 中 / **実行可能性**: 中
- **根拠**:
  - Table 5 (`tables/table5_k_level.csv`) は K-gap、TFP shift、労働分配率シフトを国別点推定で報告。M_obs は free parameter がないため点推定に見えるが、資産ラグの仮定誤りや PWT/CWON の測定誤差を無視していない。
  - Section V.10 (`manuscript_en.md:276`) の「median TFP shift is −1.7 pp」の符号が直感的でない（K_obs < K_M0 なら TFP_obs > TFP_M0、つまり TFP は **上昇** する）。Table 5 は `TFP shift` を負としているが、定義を明示していない。
- **修正案**: Table 5 の `TFP shift` を `TFP_M0 − TFP_obs` として定義し、caption に明記。可能であれば bootstrap または lag uncertainty から 95% CI を Appendix Table に追加。

### 8. M4 の out-of-sample 予渤力が M0 と同等であることを正直に論じる
- **領域**: 主張の強さ / 原稿
- **致命度**: 中 / **修正効果**: 中 / **実行可能性**: 高
- **根拠**:
  - Table 1 (`table1_model_metrics.csv`) では M4 の OOS MAPE median = **4.606%**、M0 = **4.605%**。M4 は予渤面で M0 を改善していない。
  - Section V.7 (`manuscript_en.md:236-240`) は interior-solution 国のみの conditional OOS で M2 の改善を議論しており、これは正しいが、M4 を over-sell していないか注意。
- **修正案**: Abstract / Introduction では「M2 / M_obs が OOS 予渤を改善し、M4 は財富側制約でパラメータを識別する」という役割分担を明確化。M4 の価値は「予渤」ではなく「flow-stock consistency」にあることを強調。

### 9. 労働分配率低下の主張を緩める、または実データとの比較を追加する
- **領域**: 主張の強さ
- **致命度**: 中 / **修正効果**: 中 / **実行可能性**: 中
- **根拠**:
  - Conclusion (`manuscript_en.md:402`) は「suggesting that a non-trivial part of the measured decline in labour shares is an artefact...」と結論づけている。
  - しかし、論文は機械的な労働分配率シフト（median +1.7 pp）を示すだけで、**実際の労働分配率トレンドとテンポ補正後のトレンドを比較していない**。したがって「non-trivial part」とは言えない。
- **修正案**: 「テンポ補正は労働分配率を 1.7 pp 上方へ機械的にシフトさせ、これは Karabarbounis-Neiman の下降トレンドと同次元的である」に留め、「non-trivial part of the decline」は「could account for up to」に緩める。もしくは Figure 12 に実際の労働分配率トレンドと補正後のトレンドを重ねる。

---

## 中優先

### 10. 国別截面回帰（ρ₂ vs R&D）の頑健性を高める
- **領域**: 統計設計
- **致命度**: 低〜中 / **修正効果**: 中 / **実行可能性**: 高
- **根拠**: Section V.9 (`manuscript_en.md:256-260`) は `ρ̂₂` の R&D 強度回帰を報告（slope=0.068、R²=0.129）。OLS の標準誤差が homoskedastic かどうか、外れ値の影響（USA, ISR 等）を確認していない。
- **修正案**: robust SE、leave-one-out、または non-parametric Spearman 相関を追加。R²=13% は弱いので「suggestive」としている点は良い。

### 11. M1 と M3 を主稿から縮小し、M2 / M4 / M_obs に集中する
- **領域**: 原稿 / 図表
- **致命度**: 中 / **修正効果**: 中 / **実行可能性**: 高
- **根拠**: M1（constant lag）と M3（instant + intangible）は M2 / M4 に包含される特殊化モデルであり、本文に独立セクションを持つ必要が薄い。現在 V.1-5 は細かいモデル比較で読者を迷わせる。
- **修正案**: M1/M3 は Methods または footnote で説明。主稿の Results は M0（baseline）→ M2（tempo）→ M4（joint）→ M_obs（observable）のストーリーに整理。

### 12. 将来シナリオ（A.3）を単純な機械的投影として位置づける
- **領域**: 主張の強さ / 図表
- **致命度**: 中 / **修正効果**: 中 / **実行可能性**: 高
- **根拠**: Section V.14 (`manuscript_en.md:314-320`) は 2020-2040 年の GDP シナリオを提示。Table 9 には 39 カ国の指数が並び、Ireland の M0 baseline が 2019=100 に対して 1263.7 等極端な値も含まれる。これは 2010-2019 の平均成長を単純外挿した結果だが、読者は「予測」と誤解しやすい。
- **修正案**: 「純粋に機械的な投影であり、政策予測ではない」ことを Section V.14 初めに強調。Table 9 / Figure 15 は Appendix へ移すか、代表国のみに限定。

### 13. 「contribution」段落を Introduction 冒頭に置く
- **領域**: 原稿
- **致命度**: 低〜中 / **修正効果**: 中 / **実行可能性**: 高
- **根拠**: 現稿の novelties は Related literature 末尾 (`manuscript_en.md:77`) にまとまっている。Economica の一般読者は最初の 1-2 ページで「何が新しく、なぜ重要か」を掴みたい。
- **修正案**: Introduction 第 1 段落か第 2 段落に「本研究は（1）時変 gestation lag、（2）無形資本シェア β、（3）wealth-side 制約を同時に用いる初めての成長会計である」と明記。

---

## 任意

### 14. 図の解像度を 300 dpi に上げる
- **領域**: 図表 / 再現性
- **致命度**: 低 / **修正効果**: 低 / **実行可能性**: 高
- **根拠**: 全 PNG は `plt.savefig(..., dpi=180)` で生成。印刷品質には 300 dpi が望ましい。Economica は「普通のジャーナル基準」だが、高精細は印象を良くする。
- **修正案**: `build_docx_pptx.py` / 各 `plt.savefig` の `dpi=180` を `300` に変更して再ビルド。

### 15. M2 vs M0 の OOS MAPE 改善の統計的有意性を検定する
- **領域**: 統計設計
- **致命度**: 低 / **修正効果**: 中 / **実行可能性**: 中
- **根拠**: median OOS MAPE が 4.605% → 3.986% と改善しているが、これが 39 カ国で統計的に有意か不明。Diebold-Mariano や paired bootstrap で検定。

### 16. 日本などの特異な国を RPIM / γ_price 議論で過度に強調しない
- **領域**: 主張の強さ
- **致命度**: 低 / **修正効果**: 低 / **実行可能性**: 高
- **根拠**: Section V.3-V.4 (`manuscript_en.md:196-214`) で Japan の CWON-PIM 乖離を γ_price によって「land-price revaluation artefact」と説明。これは妥当だが、1 カ国の特異例を過度に一般化しないよう注意。

---

## 強み（査読者に評価される点）

- **再現性**: 公開リポジトリ `https://github.com/bougtoir/gdp-tempo-paper` に frozen source data、checksums、コード、中間結果が揃い、`make reproduce-analysis` と `python scripts/build_docx_pptx.py` で原稿・図表が再生成できる。Data/Code Availability は強い。
- **Mechanical format**: Roman/ALL CAPS 見出し、Roman 小見出し、Harvard ALL CAPS 参考文献、JEL 3 コード、keywords 5 語、ページ番号中央、表の縦線なし、font 埋め込みは確認済み。
- **M_obs のアイデア**: OECD 資産構成から gestation lag を parameter-free で構築する点は、識別戦略として強力。
- **Limitations section**: Section VI.7 (`manuscript_en.md:396`) は CWON の質、δ(t) の confounding、資産価格再評価などを適切に認めている。

---

## 実行優先順位まとめ

| 順位 | 対応 | 主な効果 |
|------|------|----------|
| 1 | Abstract / Highlights / Cover letter の数値修正 | desk reject 回避 |
| 2 | PWT rnna と R&D/IPP の資産範囲を明確化 | 概念的信頼性確保 |
| 3 | 本文を 8,000 語・5-7 図表に再編（残り Appendix） | Economica 体裁適合 |
| 4 | Cover letter 更新 | 編集者信頼 |
| 5 | Monte Carlo 反復回数増 | 統計的信頼性 |
| 6 | M_obs 資産ラグ頑健性を本文/Appendix に追加 | 主張の頑健性 |
| 7 | Table 5 に定義・不確実性を追加 | 解釈の明快化 |
| 8 | M4 の OOS 限界を正直に議論 | 過大主張回避 |
| 9 | 労働分配率主張を緩める | 論理的整合 |

---

## 補足: 確認したデータ値

- Table 5 K-gap median: −4.29%（Ireland −9.17%）
- Table 5 TFP shift median: −1.74 pp（Ireland −4.64 pp）
- Table 5 Labour-share shift median: +1.74 pp（Korea +3.10 pp）
- Table 6 Tempo share % max: 13.8%（New Zealand）; Joint share % max: 29.7%（France）
- Table 8 Produced capital gap max: 1.1%（Netherlands）; Total wealth gap max: 0.3%（Netherlands）
- Table 1 OOS MAPE: M0 4.605%, M2 3.986%, M4 4.606%
- Table 12 `n_rep_valid`: 500 for all parameter cells

