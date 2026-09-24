# 査読者目線レビュー（Pattern Recognition 投稿前）と対応状況

対象: `manuscript_pattern_recognition.docx`（PR #431 マージ時点）と支持ファイル一式。
5 領域（原稿・統計・図表・再現性・主張強度）で評価し、各指摘に致命度／修正効果／実行可能性を付け、
優先度別に整理した。「対応」列は本リビジョン（`devin/*-pr-reviewer-revision`）での実装状況。
本ファイルは手書きであり、数値は一切含めない（数値はすべて `results/*.json` → 生成スクリプト経由）。

凡例 — 致命度: A = desk reject / major revision 直結, B = major revision で確実に指摘, C = minor。
実行可能性: 既存 = 既存データ・コードで対応可, 追加 = 追加解析が必要, 外部 = 著者・外部リソースが必要。

## 最優先（投稿前に必須）

| # | 領域 | 指摘 | 致命度 | 修正効果 | 実行可能性 | 対応 |
|---|------|------|--------|----------|------------|------|
| R1 | 再現性 / 主張 | 結論・貢献・Data availability で「公開リポから全数値が再現可能」と無条件に記述しているが、公開ミラー `bougtoir/dvs-noise-inverse-pattern-recognition` は本セッション時点でアクセス確認できず、EBSSA 生データも Google Drive 制限で再取得不可。記載と実態の不一致は方法の虚偽記載と見なされ得る。 | A | 高 | 既存（文言）＋外部（ミラー確認） | **文言修正済**: 結論・貢献(6)・Data availability を「結果ファイルから全数値を再生成できる／DND21 は公開データから end-to-end で再実行／EBSSA 結果は凍結出力として checksum 付きで同梱」に変更。REPRODUCIBILITY.md に環境バージョン・SHA-256・クリーンクローン手順を追加。**残作業（著者）**: 公開ミラーが populate された後に同手順を実行し原稿テキスト一致を確認する。 |
| R2 | 統計 | p 値のみで効果量・区間推定がない（Table 2, Table 8[旧]）。ジャーナル方針・査読慣行上、ΔAUC の不確実性が示されていないのは確実に指摘される。 | B | 高 | 追加（既存 per-recording JSON から算出可） | **実装済**: `pr_effect_sizes.py` → `results/pr_effect_sizes.json`。記録単位の percentile bootstrap 95% CI、matched-pairs rank-biserial r、提案が優位な記録数。Table 2 に 95% CI 列、本文に主要比較の CI、Supplementary Table S4 に全手法の効果量。 |
| R3 | 統計 | DND21 の混合物 80 件は 16 信号セグメント×5 ノイズ条件で構成され独立ではないのに、混合物単位の Wilcoxon を独立標本として扱っている（有効 n の過大評価、p 値の過小評価）。 | A | 高 | 追加（既存 JSON から算出可） | **実装済**: (i) 信号セグメントをクラスタとする cluster bootstrap CI、(ii) セグメント単位（条件平均）の対比較 Wilcoxon を感度分析として報告、(iii) 信号源 4 群の符号は記述のみ（検定しない）。Methods 4.4 に依存構造と対処を明記。Table 5（DND21）に CI・セグメント p・ソース優位数を追加。ハンドオーバー vs 既定値の差は混合物単位では有意でもセグメント単位では有意でないことを本文で明示。 |
| R4 | 再現性 | DND21 の再開可能キャッシュのフィンガープリントがセンサ形状・ノイズ条件・入力ファイル・信号源・特徴量パラメータ（PATCH_R, TAU_US）を含まず、これらを変更しても古いキャッシュが再利用され得る（誤った結果を再現可能に見せるリスク）。 | B | 中 | 既存 | **実装済**: フィンガープリント schema 2 に上記を追加。古い pass-1 キャッシュが「settings changed」で破棄されることをログで確認し、再計算値が旧結果と一致することを確認（変更は識別子のみで、数値には影響なし）。 |

## 高優先

| # | 領域 | 指摘 | 致命度 | 修正効果 | 実行可能性 | 対応 |
|---|------|------|--------|----------|------------|------|
| R5 | 図表 | 本文の表 8 点・図 9 点は Pattern Recognition の Regular paper としては過多で、Table 3（センサ／レート層別＝探索的）、Table 4（コスト指数＝Fig. 4 と重複）、Table 6（zero-knowledge 転移＝Fig. 6 と重複）、Fig. 8（定性例）は主張を直接支持する主表ではない。 | B | 中 | 既存 | **実装済**: 上記を `supplementary_material.docx`（Table S1–S3, Fig. S1）へ移動し、本文は Table 1–5・Fig. 1–8 に再番号付け。本文中の参照はすべて「Supplementary Table Sx / Fig. S1」に更新。Supplementary Table S4/S5 に効果量・依存性感度分析を追加。その後、著者判断で定性例を本文 Fig. 8 に戻し、DND21 図を Fig. 9 に再番号付け（本文 Fig. 1–9、補足は表のみ）。図表はすべて初出段落直後にインライン配置、英語のみ、`.dot` なし。 |
| R6 | 原稿 | 投稿規定の分量目安（single-column, double-spaced で 20–35 ページ）を超過（39 ページ）。 | B | 中 | 既存 | **概ね対応**: 補足資料への移動、キャプション・表セル単行間隔、図幅調整、参考文献 10 pt、Introduction/Discussion の重複文削減で LibreOffice 換算 36 ページ（Word ではレイアウト差で ±1 ページ）。**残作業（任意）**: 著者確認後に更に 1 ページ程度の圧縮が必要なら 5.7/5.8 節の重複記述を削る。 |
| R7 | 統計 | センサ別・イベントレート別層別（旧 Table 3）が事前登録された解析か探索的解析か不明。 | B | 中 | 既存 | **実装済**: Methods 4.4 に「事前規定なし・探索的」と明記し、表を補足資料へ。 |
| R8 | 主張 | Abstract/Conclusion の「hands its parameters」「recovers X% of label-tuned accuracy」は EBSSA の結果であり、DND21 では再現しない。DND21 の混合結果を主張の限定に用いていることを Conclusion で更に明確化する必要。 | B | 中 | 既存 | **対応済**（前版から継続、本版で CI を伴う記述に強化）: ハンドオーバーの DND21 効果は「CI が 0 を含み、セグメント単位で有意でない」と明記。 |
| R9 | 再現性 | 結果ファイルの checksum が 16 桁に切り詰められ、環境（Python・主要パッケージのバージョン）が記載されていない。 | C | 中 | 既存 | **実装済**: SHA-256 全桁、環境バージョン、frozen/re-run の区別を `data_and_code_statement.md`・`REPRODUCIBILITY.md`・`package_manifest.json` に出力。 |

## 中優先

| # | 領域 | 指摘 | 致命度 | 修正効果 | 実行可能性 | 対応 |
|---|------|------|--------|----------|------------|------|
| R10 | 原稿 | 比較手法のうち MLPF/EDnCNN は「style-compatible 再実装」、PFD は「PFD-A の局所近似（DND21 のみ）」であり、原著実装・公開重みではない。Table 1 と 4.3 節で明示されているが、Table 2/5 のラベルにも "-style"／"approximation" を保つこと。 | C | 中 | 既存 | **確認済**: ラベルは結果 JSON の `label` から供給され "-style" / "approximation" を含む。変更なし。 |
| R11 | 統計 | Holm 補正の「比較ファミリー」の定義（EBSSA: 提案 vs 各手法、DND21: tuned 群 / label-free 群）が Methods に明示されているか。 | C | 低 | 既存 | **確認済**（前版で記載）。Table 5 キャプションにファミリーを再記載。 |
| R12 | 図表 | Table 2 に 95% CI 列を追加すると 9 列となり幅が厳しい。 | C | 低 | 既存 | **対応済**: 列幅再配分・8 pt・単行間隔。編集可能 DOCX/PPTX でも同じ列構成。 |
| R13 | 再現性 | EBSSA 結果は「凍結出力」であることが Data availability に無い。 | B | 中 | 既存 | **実装済**（R1 に統合）。 |

## 任意

| # | 領域 | 指摘 | 対応 |
|---|------|------|------|
| R14 | 再現性 | 入力 AEDAT ファイルのチェックサムをキャッシュ鍵に含める（現状はファイル名）。Drive 配布物は固定 ID で内容不変のため優先度は低い。 | 未対応（ファイル名＋Drive ID で識別。内容 checksum は `dnd21_evaluation.py` 読み込み時に計算すると初回ロードが数分伸びるため保留）。 |
| R15 | 原稿 | 著者名・所属・資金・日付・先行投稿の結果・推薦査読者のプレースホルダ。 | 著者入力待ち（`title_page.docx`, `cover_letter.docx`, 原稿 CRediT/Acknowledgements）。 |
| R16 | 再現性 | EBSSA を Drive 制限解除後に `sp_evaluation.py` で再実行し、凍結 JSON と checksum 一致を確認する。 | 外部要因待ち。 |
| R17 | 投稿規定 | Highlights（3–5 項目・各 85 字以内）、Graphical abstract、CRediT、AI 利用宣言、COI 宣言は実装済。Abstract ≤ 200 語は生成時にアサート。動的レンダリングで取得できなかった規定項目（例: キーワード数の上限）は著者が Guide for Authors で最終確認する。 | 著者確認。 |

## 機械的最終チェック（レビュー後に実施）

* Abstract 語数アサート（≤ 200）、未引用参考文献の検出（RuntimeError）、Vancouver 順は生成時に自動。
* 図表: 本文 Fig. 1–9 / Table 1–5、補足 Table S1–S6 がすべて本文で初出前に引用され、直後に配置されること（`check_pr_manuscript.py` 相当の走査で確認）。
* 図・表内テキストは英語のみ。`.dot` ファイルなし。
* 経験的数値は `pr_numbers.py`（results/*.json ローダ）以外にリテラルで存在しない（`n_pub = 7` のみ 4.3 節の列挙数で、結果値ではない）。
* `pytest tests/` 通過、`ruff check --select F,E9` 通過。
