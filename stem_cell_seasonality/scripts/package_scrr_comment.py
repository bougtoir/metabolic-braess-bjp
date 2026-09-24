#!/usr/bin/env python3
"""Bundle the SCRR Comment submission package into a ZIP archive."""

import os
import zipfile
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

FILES = [
    "StemCellReviewsAndReports_Comment_InvisibleVariables.docx",
    "SCRR_CoverLetter_Comment_InvisibleVariables.docx",
    "SCRR_PointByPointResponse_Comment_InvisibleVariables.docx",
    "SCRR_Comment_Figure1_Clonal_Environmental_Variance.png",
    "SCRR_Comment_Figures_InvisibleVariables.pptx",
    "SCRR_Comment_SelfCriticalReview.md",
    "create_scrr_comment_reference_audit_report.md",
    "comment_summary.json",
]


def main():
    out_zip = os.path.join(OUTPUT_DIR, "SCRR_Comment_Submission_Package.zip")
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for fname in FILES:
            fpath = os.path.join(OUTPUT_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)
            else:
                print(f"Warning: {fpath} not found, skipping")
    print(f"Submission package saved to: {out_zip}")


if __name__ == "__main__":
    main()
