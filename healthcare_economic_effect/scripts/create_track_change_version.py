import argparse
import os
import shutil
import subprocess
import sys
import time
import zipfile
from lxml import etree

import uno
from com.sun.star.beans import PropertyValue
from unohelper import systemPathToFileUrl


def start_soffice():
    cmd = [
        "/usr/bin/soffice",
        "--headless",
        "--norestore",
        "--nologo",
        "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def connect(max_wait=20):
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", localContext
    )
    last_err = None
    for _ in range(max_wait * 2):
        try:
            ctx = resolver.resolve(
                "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
            )
            return ctx
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise RuntimeError(f"Could not connect to soffice: {last_err}")


def make_prop(name, value):
    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


def lo_compare(new_doc, old_doc, out_doc):
    proc = start_soffice()
    try:
        ctx = connect()
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

        load_props = (
            make_prop("Hidden", True),
            make_prop("ReadOnly", False),
        )
        doc = desktop.loadComponentFromURL(systemPathToFileUrl(new_doc), "_blank", 0, load_props)

        compare_props = (make_prop("URL", systemPathToFileUrl(old_doc)),)
        dispatch_helper = smgr.createInstanceWithContext("com.sun.star.frame.DispatchHelper", ctx)
        dispatch_helper.executeDispatch(
            doc.getCurrentController().getFrame(), ".uno:CompareDocuments", "", 0, compare_props
        )

        save_props = (
            make_prop("FilterName", "MS Word 2007 XML"),
            make_prop("Overwrite", True),
        )
        doc.storeToURL(systemPathToFileUrl(out_doc), save_props)
        doc.dispose()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=15)
        except Exception:
            proc.kill()


def apply_track_change_colors(src_docx, dst_docx):
    NS = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }

    def ensure_rpr(run):
        rpr = run.find("w:rPr", NS)
        if rpr is None:
            rpr = etree.SubElement(
                run,
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr",
            )
        return rpr

    def set_color(rpr, val):
        for c in list(rpr.findall("w:color", NS)):
            rpr.remove(c)
        color = etree.SubElement(
            rpr,
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color",
        )
        color.set(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val",
            val,
        )

    def add_strike(rpr):
        if rpr.find("w:strike", NS) is None:
            etree.SubElement(
                rpr,
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}strike",
            )

    def process_change(change, color, strike=False):
        for run in change.iter(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r"
        ):
            rpr = ensure_rpr(run)
            set_color(rpr, color)
            if strike:
                add_strike(rpr)

    tmpdir = dst_docx + ".tmp_unzip"
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)

    with zipfile.ZipFile(src_docx, "r") as z:
        z.extractall(tmpdir)

    doc_path = os.path.join(tmpdir, "word", "document.xml")
    tree = etree.parse(doc_path)
    root = tree.getroot()

    for ins in root.iter(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ins"
    ):
        process_change(ins, "FF0000", strike=False)
    for del_ in root.iter(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}del"
    ):
        process_change(del_, "0000FF", strike=True)

    tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)

    with zipfile.ZipFile(dst_docx, "w", zipfile.ZIP_DEFLATED) as zout:
        for dirpath, _, filenames in os.walk(tmpdir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                arcname = os.path.relpath(fp, tmpdir)
                zout.write(fp, arcname)
    shutil.rmtree(tmpdir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, help="Previous version .docx")
    parser.add_argument("--new", required=True, help="Revised version .docx")
    parser.add_argument("--output", required=True, help="Output track-change .docx")
    args = parser.parse_args()

    lo_out = args.output + "_LO.docx"
    try:
        lo_compare(os.path.abspath(args.new), os.path.abspath(args.old), os.path.abspath(lo_out))
        apply_track_change_colors(lo_out, args.output)
        print(f"Created {args.output}")
    finally:
        if os.path.exists(lo_out):
            os.remove(lo_out)


if __name__ == "__main__":
    main()
