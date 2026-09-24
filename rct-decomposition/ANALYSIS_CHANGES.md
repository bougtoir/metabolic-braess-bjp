# KOTHA Framework — 解析パイプラインの変更点

## 1. データ管理：ハードコードから CSV へ

- `validation/run_validation.py` に埋め込まれていたマグネシウム・AMI とスタチン・HF の研究データを
  `data/magnesium_ami.csv`、`data/statins_hf_obs.csv`、`data/statins_hf_rct.csv` に移行。
- 各 CSV の出典は `data/SOURCES.md` に集約。
- これにより、原稿・図表に使用される数値がコード内の手打ち配列ではなく、外部ファイルから読み込まれるようになった。

## 2. 解析スクリプトの再構成

- `run_validation.py` のパスを絶対パスからリポジトリ相対パスに変更（`BASE_DIR` / `DATA_DIR` / `OUTDIR`）。
- `compute_results()` 関数を新設し、Module K / Module T / Module H の計算結果を辞書で返すようにした。
  - `build_paper.py` や他のスクリプトから直接呼び出せる。
  - `main()` は `compute_results()` を呼び出して表示・図生成を行うのみ。
- `results_summary.txt` の出力パスも相対パス化。

## 3. 原稿生成の自動化

- `paper_template.md` を新設。動的に書き換える箇所を `<!-- DYNAMIC: ... -->` マーカーと `<<...>>` プレースホルダーで管理。
- `build_paper.py` を新設：
  - `run_validation.compute_results()` の結果からすべての数値（OR / HR / CI / I² / Z / power / events / OIS など）を計算。
  - `paper_template.md` のマーカーを解析結果で置換し、`04_paper_rsm.md` を生成。
  - 続けて `generate_rsm_docx_final.py` を呼び出し、`KOTHA_Framework_RSM.docx` を生成。
- これにより、原稿本文・表・図のすべての数値がコードとデータから再現可能になった。

## 4. 数値の再現性・一貫性

- 主要な数値は前回と同一（例：Mg pre-ISIS-4 OR 0.54、all-trials OR 0.56、statin obs HR 0.72、RCT HR 0.97、TSA Z = -2.90 / -0.74）。
- ただし、これらがすべて計算から導出され、マニュスクリプトや DOCX 生成スクリプトにリテラルで埋め込まれていないことを保証。
- `KOTHA_Framework_RSM.docx` の作成日時・ZIP タイムスタンプを固定し、再実行してもバイナリ差分が出ないようにした。

## 5. ビルド・同期

- `Makefile` を追加：`make all` で `run_validation.py` + `build_paper.py` を一括実行。
- 公開リポジトリ `bougtoir/kotha-rct-decomposition` でも `make clean && make all` 後に `git status` がクリーンになることを確認。
- wip ブランチと公開ミラーを push 済み。

## 6. 汎用フォーマット用ファイル

- `make generic` で `04_paper_generic.md` と `KOTHA_Framework_generic.docx` を生成。
- 内容は `04_paper_rsm.md` / `KOTHA_Framework_RSM.docx` と同一だが、ジャーナル名を含まないファイル名で提供可能。
