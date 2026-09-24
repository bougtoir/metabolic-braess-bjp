"""
Shared helpers for the Blood Pressure Monitoring manuscript generators.

Provides:
  * a citation manager that numbers references in order of first
    appearance (so the reference list can never contain orphans and the
    numbering always matches the text);
  * loading of the machine-readable results (results/summary.json) so that
    no numerical result is hard-coded in the manuscript text.
"""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results", "summary.json")


def load_summary():
    with open(RESULTS) as f:
        return json.load(f)


class Citations:
    """Assigns numbers to references on first use."""

    def __init__(self, refdb: dict, collapse_ranges: bool = True):
        self.refdb = refdb
        self.order = []      # keys in order of first appearance
        self.collapse_ranges = collapse_ranges

    def cite(self, *keys) -> str:
        nums = []
        for k in keys:
            if k not in self.refdb:
                raise KeyError(f"unknown reference key: {k}")
            if k not in self.order:
                self.order.append(k)
            nums.append(self.order.index(k) + 1)
        # collapse consecutive runs (e.g. 1,2,3 -> 1-3)
        return "{" + _fmt_nums(sorted(set(nums)), collapse=self.collapse_ranges) + "}"

    def ordered_references(self):
        """Return the reference strings in citation order."""
        return [self.refdb[k] for k in self.order]

    def check_all_cited(self):
        missing = [k for k in self.refdb if k not in self.order]
        return missing


def _fmt_nums(nums, collapse: bool = True):
    """Return numbers as a comma-separated string, optionally collapsing ranges."""
    if not nums:
        return ""
    nums = sorted(set(nums))
    if not collapse:
        return "}, {".join(str(n) for n in nums)
    parts = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
        else:
            parts.append(f"{start}" if start == prev else f"{start}-{prev}")
            start = prev = n
    parts.append(f"{start}" if start == prev else f"{start}-{prev}")
    return "}, {".join(parts)


# ----------------------------------------------------------------------
# Reference database, formatted in IEEE Transactions style:
# "A. B. Author, "Title of Article," *Abbrev. Journal*, vol. x, no. y,
#  pp. z, Month Year."  All entries correspond to real, citable sources.
# The citation manager numbers them in order of first appearance.
# ----------------------------------------------------------------------
REFDB = {
    "saugel2020": "B. Saugel, K. Kouz, A. S. Meidert, L. Schulte-Uentrop, and S. Romagnoli, \"How to measure blood pressure using an arterial catheter: A systematic 5-step approach,\" Crit. Care, vol. 24, p. 172, 2020.",
    "saugelsessler2021": "B. Saugel and D. I. Sessler, \"Perioperative blood pressure management,\" Anesthesiology, vol. 134, pp. 250-261, 2021.",
    "gupta2025": "D. Gupta, A. Jain, and M. Ismaeil, \"Zero arterial catheters with every change in the height difference of pressure transducer and catheter insertion site,\" Ann. Card. Anaesth., vol. 28, p. 205, 2025.",
    "mark1998": "J. B. Mark, Atlas of Cardiovascular Monitoring. New York, NY, USA: Churchill Livingstone, 1998.",
    "mcghee2002": "B. H. McGhee and M. E. J. Bridges, \"Monitoring arterial blood pressure: What you may not know,\" Crit. Care Nurse, vol. 22, pp. 60-79, 2002.",
    "blandaltman1986": "J. M. Bland and D. G. Altman, \"Statistical methods for assessing agreement between two methods of clinical measurement,\" Lancet, vol. 327, pp. 307-310, 1986.",
    "blandaltman1999": "J. M. Bland and D. G. Altman, \"Measuring agreement in method comparison studies,\" Stat. Methods Med. Res., vol. 8, pp. 135-160, 1999.",
    "critchley1999": "L. A. H. Critchley and J. A. J. H. Critchley, \"A meta-analysis of studies using bias and precision statistics to compare cardiac output measurement techniques,\" J. Clin. Monit. Comput., vol. 15, pp. 85-91, 1999.",
    "cecconi2009": "M. Cecconi, A. Rhodes, J. Poloniecki, G. Della Rocca, and R. M. Grounds, \"Bench-to-bedside review: The importance of the precision of the reference technique in method comparison studies,\" Crit. Care, vol. 13, p. 201, 2009.",
    "lin1989": "L. I. Lin, \"A concordance correlation coefficient to evaluate reproducibility,\" Biometrics, vol. 45, pp. 255-268, 1989.",
    "lin2000": "L. I. Lin, \"A note on the concordance correlation coefficient,\" Biometrics, vol. 56, pp. 324-325, 2000.",
    "mcbride2005": "G. B. McBride, \"A proposal for strength-of-agreement criteria for Lin's concordance correlation coefficient,\" NIWA, Hamilton, New Zealand, Client Rep. HAM2005-062, 2005.",
    "gardner1981": "R. M. Gardner, \"Direct blood pressure measurement—dynamic response requirements,\" Anesthesiology, vol. 54, pp. 227-236, 1981.",
    "romagnoli2014": "S. Romagnoli et al., \"Accuracy of invasive arterial pressure monitoring in cardiovascular patients: An observational study,\" Crit. Care, vol. 18, p. 644, 2014.",
    "kleinman1992": "B. Kleinman, S. Powell, P. Kumar, and R. M. Gardner, \"The fast flush test measures the dynamic response of the entire blood pressure monitoring system,\" Anesthesiology, vol. 77, pp. 1215-1220, 1992.",
    "linnet1990": "K. Linnet, \"Estimation of the linear relationship between the measurements of two methods with proportional errors,\" Stat. Med., vol. 9, pp. 1463-1473, 1990.",
    "passingbablok1983": "H. Passing and W. Bablok, \"A new biometrical procedure for testing the equality of measurements from two different analytical methods,\" J. Clin. Chem. Clin. Biochem., vol. 21, pp. 709-720, 1983.",
    "nickerson1997": "C. A. Nickerson, \"A note on 'A concordance correlation coefficient to evaluate reproducibility',\" Biometrics, vol. 53, pp. 1503-1507, 1997.",
    "barnhart2007": "H. X. Barnhart, M. J. Haber, and L. I. Lin, \"An overview on assessing agreement with continuous measurements,\" J. Biopharm. Stat., vol. 17, pp. 529-569, 2007.",
    "hasenkamp2012": "W. Hasenkamp et al., \"Polyimide/SU-8 catheter-tip MEMS gauge pressure sensor,\" Biomed. Microdevices, vol. 14, pp. 819-828, 2012.",
    "song2020": "P. Song et al., \"Recent progress of miniature MEMS pressure sensors,\" Micromachines, vol. 11, no. 1, p. 56, 2020.",
    "kang2022": "Y. Kang et al., \"Development of a flexible integrated self-calibrating MEMS pressure sensor using a liquid-to-vapor phase change,\" Sensors, vol. 22, no. 24, p. 9737, 2022.",
    "barlian2009": "A. A. Barlian, W. T. Park, J. R. Mallon, A. J. Rastegar, and B. L. Pruitt, \"Review: Semiconductor piezoresistance for microsystems,\" Proc. IEEE, vol. 97, no. 3, pp. 513-552, Mar. 2009.",
    "scalia2023": "A. Scalia et al., \"High fidelity pressure wires provide accurate validation of non-invasive central blood pressure and pulse wave velocity measurements,\" Biomedicines, vol. 11, no. 4, p. 1235, 2023.",
    "odor2017": "P. M. Odor, S. Bampoe, and M. Cecconi, \"Cardiac output monitoring: Validation studies—how results should be presented,\" Curr. Anesthesiol. Rep., vol. 7, pp. 410-415, 2017.",
    "kim2014": "S. H. Kim et al., \"Accuracy and precision of continuous noninvasive arterial pressure monitoring compared with invasive arterial pressure: A systematic review and meta-analysis,\" Anesthesiology, vol. 120, pp. 1080-1097, 2014.",
    "joosten2017": "A. Joosten et al., \"Accuracy and precision of non-invasive cardiac output monitoring devices in perioperative medicine: A systematic review and meta-analysis,\" Br. J. Anaesth., vol. 118, pp. 298-310, 2017.",
    "chatterjee2009": "K. Chatterjee, \"The Swan–Ganz catheters: Past, present, and future,\" Circulation, vol. 119, pp. 147-152, 2009.",
    "ameloot2015": "K. Ameloot, P. J. Palmers, and M. L. N. G. Malbrain, \"The accuracy of noninvasive cardiac output and pressure measurements with finger cuff: A concise review,\" Curr. Opin. Crit. Care, vol. 21, pp. 232-239, 2015.",
    "squara2007": "P. Squara, D. Denjean, P. Estagnasie, A. Brusset, J. C. Dib, and C. Dubois, \"Noninvasive cardiac output monitoring (NICOM): A clinical validation,\" Intensive Care Med., vol. 33, pp. 1191-1194, 2007.",
    "manecke2005": "G. R. Manecke, \"Edwards FloTrac sensor and Vigileo monitor: Easy, accurate, reliable cardiac output assessment using the arterial pulse wave,\" Expert Rev. Med. Devices, vol. 2, pp. 523-527, 2005.",
    "vitaldb2022": "H. C. Lee, Y. Park, S. B. Yoon, S. M. Yang, D. Park, and C. W. Jung, \"VitalDB, a high-fidelity multi-parameter vital signs database in surgical patients,\" Sci. Data, vol. 9, p. 279, 2022.",
    # instrumentation-and-measurement additions
    "aami1994": "ANSI/AAMI BP22:1994 (R2016), Blood Pressure Transducers. Arlington, VA, USA: AAMI, 2016.",
    "gum2008": "JCGM 100:2008, Evaluation of Measurement Data—Guide to the Expression of Uncertainty in Measurement. Sèvres, France: BIPM, 2008.",
    "shirmohammadi2016": "S. Shirmohammadi, K. Barbé, D. Grimaldi, S. Rapuano, and S. Grassini, \"Instrumentation and measurement in medical, biomedical, and healthcare systems,\" IEEE Instrum. Meas. Mag., vol. 19, no. 5, pp. 6-12, Oct. 2016.",
    # IEEE Transactions on Instrumentation and Measurement (primary I&M venue)
    "balestrieri2010": "E. Balestrieri and S. Rapuano, \"Instruments and methods for calibration of oscillometric blood pressure measurement devices,\" IEEE Trans. Instrum. Meas., vol. 59, no. 9, pp. 2391-2404, Sep. 2010.",
    "zakrzewski2002": "J. Zakrzewski and K. Wrobel, \"Dynamic calibration of low-range silicon pressure sensors,\" IEEE Trans. Instrum. Meas., vol. 51, no. 6, pp. 1358-1362, Dec. 2002.",
    "koohi2017": "I. Koohi, I. Batkin, V. Z. Groza, S. Shirmohammadi, H. R. Dajani, and S. Ahmad, \"Metrological characterization of a method for blood pressure estimation based on arterial lumen area model,\" IEEE Trans. Instrum. Meas., vol. 66, no. 4, pp. 734-745, Apr. 2017.",
    "forouzanfar2015": "M. Forouzanfar, S. Ahmad, I. Batkin, H. R. Dajani, V. Z. Groza, and M. Bolic, \"Model-based mean arterial pressure estimation using simultaneous electrocardiogram and oscillometric blood pressure measurements,\" IEEE Trans. Instrum. Meas., vol. 64, no. 9, pp. 2443-2452, Sep. 2015.",
    "bogatu2021": "L. I. Bogatu, S. Turco, M. Mischi, J. Muehlsteff, and P. Woerlee, \"An experimental study on the blood pressure cuff as a transducer for oscillometric blood pressure measurements,\" IEEE Trans. Instrum. Meas., vol. 70, pp. 1-11, 2021.",
    "alvarez2022": "E. Alvarez Vazquez, D. Ewert, D. Jorgenson, and M. Sand, \"Assessment of the uncertainty associated with two consecutive blood pressure measurements using the auscultatory method,\" IEEE Trans. Instrum. Meas., vol. 71, pp. 1-11, 2022.",
    "cosoli2021": "G. Cosoli, L. Verdenelli, and L. Scalise, \"Metrological characterization of therapeutic devices for pressure wave therapy: Force, energy density, and waveform evaluation,\" IEEE Trans. Instrum. Meas., vol. 70, pp. 1-8, 2021.",
    "gubian2009": "M. Gubian, A. Marconato, A. Boni, and D. Petri, \"A study on uncertainty-complexity tradeoffs for dynamic nonlinear sensor compensation,\" IEEE Trans. Instrum. Meas., vol. 58, no. 1, pp. 26-32, Jan. 2009.",
    "jafaripanah2005": "M. Jafaripanah, B. M. Al-Hashimi, and N. M. White, \"Application of analog adaptive filters for dynamic sensor compensation,\" IEEE Trans. Instrum. Meas., vol. 54, no. 1, pp. 245-251, Feb. 2005.",
    "tirupathi2021": "R. Tirupathi and S. K. Kar, \"On-chip implementable autocalibration of sensor offset for differential capacitive sensor interfaces,\" IEEE Trans. Instrum. Meas., vol. 70, pp. 1-9, 2021.",
    "morello2020": "R. Morello, \"GUM-based decisional criteria to make decisions in presence of measurement uncertainty,\" IEEE Trans. Instrum. Meas., vol. 69, no. 8, pp. 5511-5522, Aug. 2020.",
    "ruan2021": "Y. Ruan, L. Yuan, W. Yuan, Y. He, and L. Lu, \"Temperature compensation and pressure bias estimation for piezoresistive pressure sensor based on machine learning approach,\" IEEE Trans. Instrum. Meas., vol. 70, pp. 1-10, 2021.",
    "alegria2007": "F. Correa Alegria and A. Cruz Serra, \"Standard histogram test precision of ADC gain and offset error estimation,\" IEEE Trans. Instrum. Meas., vol. 56, no. 5, pp. 1527-1531, Oct. 2007.",
}


# ----------------------------------------------------------------------
# Reference database for the Japanese BPM manuscript, formatted in
# Vancouver / Blood Pressure Monitoring style:
# "Authors. Title. Journal-MEDLINE-abbrev Year; Volume: pages." All authors
# are listed when six or fewer; when seven or more, the first six are listed
# followed by "et al." Author lists, journal abbreviations, volumes and pages
# were verified against the original documents (Crossref/DOI). References are
# numbered in order of first appearance by the Citations manager.
# ----------------------------------------------------------------------
REFDB_JA = {
    'saugel2020': 'Saugel B, Kouz K, Meidert AS, Schulte-Uentrop L, Romagnoli S. How to measure blood pressure using an arterial catheter: a systematic 5-step approach. Crit Care 2020; 24: 172.',
    'saugelsessler2021': 'Saugel B, Sessler DI. Perioperative blood pressure management. Anesthesiology 2021; 134: 250-261.',
    'gupta2025': 'Gupta D, Jain A, Ismaeil M. Zero arterial catheters with every change in the height difference of pressure transducer and catheter insertion site. Ann Card Anaesth 2025; 28: 205.',
    'mark1998': 'Mark JB. Atlas of Cardiovascular Monitoring. New York: Churchill Livingstone; 1998.',
    'mcghee2002': 'McGhee BH, Bridges MEJ. Monitoring arterial blood pressure: what you may not know. Crit Care Nurse 2002; 22: 60-79.',
    'blandaltman1986': 'Bland JM, Altman DG. Statistical methods for assessing agreement between two methods of clinical measurement. Lancet 1986; 327: 307-310.',
    'blandaltman1999': 'Bland JM, Altman DG. Measuring agreement in method comparison studies. Stat Methods Med Res 1999; 8: 135-160.',
    'critchley1999': 'Critchley LAH, Critchley JAJH. A meta-analysis of studies using bias and precision statistics to compare cardiac output measurement techniques. J Clin Monit Comput 1999; 15: 85-91.',
    'cecconi2009': 'Cecconi M, Rhodes A, Poloniecki J, Della Rocca G, Grounds RM. Bench-to-bedside review: the importance of the precision of the reference technique in method comparison studies. Crit Care 2009; 13: 201.',
    'lin1989': 'Lin LI. A concordance correlation coefficient to evaluate reproducibility. Biometrics 1989; 45: 255-268.',
    'lin2000': 'Lin LI. A note on the concordance correlation coefficient. Biometrics 2000; 56: 324-325.',
    'mcbride2005': "McBride GB. A proposal for strength-of-agreement criteria for Lin's concordance correlation coefficient. NIWA Client Report HAM2005-062. Hamilton: National Institute of Water and Atmospheric Research; 2005.",
    'gardner1981': 'Gardner RM. Direct blood pressure measurement—dynamic response requirements. Anesthesiology 1981; 54: 227-236.',
    'romagnoli2014': 'Romagnoli S, Ricci Z, Quattrone D, Tofani L, Tujjar O, Villa G, et al. Accuracy of invasive arterial pressure monitoring in cardiovascular patients: an observational study. Crit Care 2014; 18: 644.',
    'kleinman1992': 'Kleinman B, Powell S, Kumar P, Gardner RM. The fast flush test measures the dynamic response of the entire blood pressure monitoring system. Anesthesiology 1992; 77: 1215-1220.',
    'linnet1990': 'Linnet K. Estimation of the linear relationship between the measurements of two methods with proportional errors. Stat Med 1990; 9: 1463-1473.',
    'passingbablok1983': 'Passing H, Bablok W. A new biometrical procedure for testing the equality of measurements from two different analytical methods. J Clin Chem Clin Biochem 1983; 21: 709-720.',
    'nickerson1997': 'Nickerson CA. A note on “A concordance correlation coefficient to evaluate reproducibility”. Biometrics 1997; 53: 1503-1507.',
    'barnhart2007': 'Barnhart HX, Haber MJ, Lin LI. An overview on assessing agreement with continuous measurements. J Biopharm Stat 2007; 17: 529-569.',
    'hasenkamp2012': 'Hasenkamp W, Forchelet D, Pataky K, Villard J, van Lintel H, Bertsch A, et al. Polyimide/SU-8 catheter-tip MEMS gauge pressure sensor. Biomed Microdevices 2012; 14: 819-828.',
    'song2020': 'Song P, Ma Z, Ma J, Yang L, Wei J, Zhao Y, et al. Recent progress of miniature MEMS pressure sensors. Micromachines (Basel) 2020; 11: 56.',
    'kang2022': 'Kang Y, Mouring S, de Clerck A, Mao S, Ng W, Ruan H. Development of a flexible integrated self-calibrating MEMS pressure sensor using a liquid-to-vapor phase change. Sensors (Basel) 2022; 22: 9737.',
    'barlian2009': 'Barlian AA, Park WT, Mallon JR, Rastegar AJ, Pruitt BL. Review: semiconductor piezoresistance for microsystems. Proc IEEE 2009; 97: 513-552.',
    'scalia2023': 'Scalia A, Ghafari C, Navarre W, Delmotte P, Phillips R, Carlier S. High fidelity pressure wires provide accurate validation of non-invasive central blood pressure and pulse wave velocity measurements. Biomedicines 2023; 11: 1235.',
    'odor2017': 'Odor PM, Bampoe S, Cecconi M. Cardiac output monitoring: validation studies—how results should be presented. Curr Anesthesiol Rep 2017; 7: 410-415.',
    'kim2014': 'Kim SH, Lilot M, Sidhu KS, Rinehart J, Yu Z, Canales C, et al. Accuracy and precision of continuous noninvasive arterial pressure monitoring compared with invasive arterial pressure: a systematic review and meta-analysis. Anesthesiology 2014; 120: 1080-1097.',
    'joosten2017': 'Joosten A, Desebbe O, Suehiro K, Murphy L, Essiet M, Alexander B, et al. Accuracy and precision of non-invasive cardiac output monitoring devices in perioperative medicine: a systematic review and meta-analysis. Br J Anaesth 2017; 118: 298-310.',
    'chatterjee2009': 'Chatterjee K. The Swan–Ganz catheters: past, present, and future. Circulation 2009; 119: 147-152.',
    'ameloot2015': 'Ameloot K, Palmers PJ, Malbrain MLNG. The accuracy of noninvasive cardiac output and pressure measurements with finger cuff: a concise review. Curr Opin Crit Care 2015; 21: 232-239.',
    'squara2007': 'Squara P, Denjean D, Estagnasie P, Brusset A, Dib JC, Dubois C. Noninvasive cardiac output monitoring (NICOM): a clinical validation. Intensive Care Med 2007; 33: 1191-1194.',
    'manecke2005': 'Manecke GR. Edwards FloTrac sensor and Vigileo monitor: easy, accurate, reliable cardiac output assessment using the arterial pulse wave. Expert Rev Med Devices 2005; 2: 523-527.',
    'vitaldb2022': 'Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW. VitalDB, a high-fidelity multi-parameter vital signs database in surgical patients. Sci Data 2022; 9: 279.',
}
