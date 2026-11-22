"""Build a CVAT for images 1.1 annotations.xml for task Day12-G04 (22 core frames).

usage: python work/build_annotations.py OUT_DIR
Writes OUT_DIR/annotations.xml and export zips (part_A, part_B, export_final) with only annotations.xml.
Coordinates were read off gridded copies of the frames; review them in CVAT after import.
"""
import os
import sys
import zipfile
from xml.sax.saxutils import escape

FACE13 = ["left_eye_outer", "left_eye_inner", "left_eye_upper", "left_eye_lower",
          "right_eye_outer", "right_eye_inner", "right_eye_upper", "right_eye_lower",
          "nose_tip", "mouth_left", "mouth_right", "lip_upper", "lip_lower"]

OMS_W, OMS_H, D_W, D_H = 960, 640, 1280, 1024


def meta(modality, light="unknown", blocked="no"):
    return {"modality": modality, "light": light, "camera_blocked": blocked}


def face(box, el="unknown", er="unknown", glasses="unknown", gaze="other"):
    return ("face", box, {"eye_left": el, "eye_right": er, "glasses": glasses, "gaze_zone": gaze})


# ---------- OMS (SVIRO X5, camera looks rearward: image-left = rear_right) ----------
# per scene: list of shapes for RGB; IR overrides where visibility differs
OMS = {
    "S01": dict(
        rgb=[("child_seat", (15, 165, 388, 635), {"seat": "rear_right", "occupied": "yes"}),
             ("object", (378, 322, 556, 562), {"seat": "rear_middle", "type": "bag"}),
             ("child_seat", (562, 198, 846, 615), {"seat": "rear_left", "occupied": "no"})]),
    "S02": dict(
        rgb=[("person", (518, 30, 960, 640), {"seat": "rear_left", "seatbelt": "not_worn"}),
             face((652, 60, 778, 145), "open", "open", "none", "other"),
             ("infant_seat", (0, 352, 388, 610), {"seat": "rear_right", "facing": "rear"})]),
    "S03": dict(  # night: RGB almost black, IR-sim shows the scene
        rgb=[("child_seat", (95, 200, 400, 625), {"seat": "rear_right", "occupied": "yes"}),
             ("infant_seat", (572, 318, 862, 610), {"seat": "rear_left", "facing": "front"})],
        ir=[("child_seat", (95, 200, 400, 625), {"seat": "rear_right", "occupied": "yes"}),
            ("infant_seat", (572, 318, 862, 610), {"seat": "rear_left", "facing": "front"}),
            ("object", (456, 396, 496, 450), {"seat": "rear_middle", "type": "cup"})]),
    "S04": dict(
        rgb=[("person", (62, 85, 400, 640), {"seat": "rear_right", "seatbelt": "not_worn"}),
             face((76, 138, 194, 232), "open", "open", "none", "other"),
             ("child_seat", (555, 195, 848, 615), {"seat": "rear_left", "occupied": "yes"})]),
    "S05": dict(
        rgb=[("person", (30, 18, 435, 640), {"seat": "rear_right", "seatbelt": "not_worn"}),
             face((170, 63, 315, 209), "open", "open", "none", "other"),
             ("infant_seat", (563, 315, 958, 612), {"seat": "rear_left", "facing": "rear"})]),
    "S06": dict(  # face cut by top edge: eyes hidden, nose tip + mouth visible -> face box, attrs unknown (review v2)
        rgb=[("person", (28, 0, 450, 640), {"seat": "rear_right", "seatbelt": "not_worn"}),
             face((97, 0, 257, 109), "unknown", "unknown", "unknown", "other"),
             ("object", (395, 355, 548, 570), {"seat": "rear_middle", "type": "box"})]),
    "S07": dict(
        rgb=[("object", (172, 325, 375, 555), {"seat": "rear_right", "type": "bag"}),
             ("child_seat", (362, 203, 588, 590), {"seat": "rear_middle", "occupied": "no"})]),
    "S08": dict(  # night: RGB too dark to see a belt; IR-sim shows clearly no belt
        rgb=[("person", (0, 70, 415, 640), {"seat": "rear_right", "seatbelt": "unknown"}),
             face((186, 131, 317, 252), "open", "open", "none", "other"),
             ("child_seat", (560, 160, 950, 640), {"seat": "rear_left", "occupied": "yes"})],
        ir=[("person", (0, 70, 415, 640), {"seat": "rear_right", "seatbelt": "not_worn"}),
            face((186, 131, 317, 252), "open", "open", "none", "other"),
            ("child_seat", (560, 160, 950, 640), {"seat": "rear_left", "occupied": "yes"})]),
}

# ---------- DMS (Drive&Act NIR, rotated ~90 deg: head to image right, driver's left eye = larger y) ----------
V, O, X = "v", "occ", "out"  # visible, occluded (position confident), outside (cannot place)


def pts(**kw):
    out = {}
    for name in FACE13:
        x, y, flag = kw[name]
        out[name] = (x, y, flag)
    return out


DMS = {
    "D01": dict(  # taking glasses off, head turned away; only profile visible
        person=((280, 270, 1210, 900), "worn_correct"),
        face=face((935, 395, 1090, 600), "unknown", "unknown", "none", "other"),
        face13=pts(left_eye_outer=(985, 442, O), left_eye_inner=(980, 415, O), left_eye_upper=(995, 428, O),
                   left_eye_lower=(975, 428, O), right_eye_outer=(985, 370, X), right_eye_inner=(980, 395, X),
                   right_eye_upper=(992, 383, X), right_eye_lower=(972, 383, X), nose_tip=(948, 452, V),
                   mouth_left=(960, 505, X), mouth_right=(958, 470, X), lip_upper=(955, 482, X),
                   lip_lower=(946, 490, X)),
        hands=[((625, 400, 705, 455), "right", "no"), ((525, 550, 645, 705), "left", "no")],
        phone=None),
    "D02": dict(  # arm raised over head (hoodie), clear glasses
        person=((280, 320, 1240, 950), "worn_correct"),
        face=face((740, 480, 1220, 900), "unknown", "unknown", "clear", "other"),
        face13=pts(left_eye_outer=(965, 860, O), left_eye_inner=(965, 750, O), left_eye_upper=(990, 805, O),
                   left_eye_lower=(945, 805, O), right_eye_outer=(975, 530, O), right_eye_inner=(975, 600, O),
                   right_eye_upper=(995, 565, O), right_eye_lower=(955, 565, O), nose_tip=(830, 665, V),
                   mouth_left=(775, 715, X), mouth_right=(775, 625, X), lip_upper=(790, 670, X),
                   lip_lower=(765, 670, X)),
        hands=[((460, 730, 592, 924), "right", "no")],
        phone=None),
    "D03": dict(  # head tilted, hand raised near face; no phone shape visible -> no phone box
        person=((280, 180, 1240, 1000), "unknown"),
        face=face((950, 390, 1200, 710), "unknown", "unknown", "unknown", "other"),
        face13=pts(left_eye_outer=(1140, 505, O), left_eye_inner=(1090, 500, O), left_eye_upper=(1115, 488, O),
                   left_eye_lower=(1115, 512, O), right_eye_outer=(995, 490, O), right_eye_inner=(1040, 495, O),
                   right_eye_upper=(1017, 480, O), right_eye_lower=(1017, 502, O), nose_tip=(1065, 585, V),
                   mouth_left=(1130, 665, V), mouth_right=(1050, 660, V), lip_upper=(1090, 645, V),
                   lip_lower=(1090, 685, V)),
        hands=[((355, 850, 525, 965), "left", "no")],  # right hand not visible (only sleeve cuff) -> no box (review v2)
        phone=None),
    "D04": dict(  # hand at mouth, belt worn
        person=((300, 300, 1200, 880), "worn_correct"),
        face=face((860, 310, 1110, 600), "unknown", "unknown", "none", "other"),
        face13=pts(left_eye_outer=(1020, 465, O), left_eye_inner=(1012, 425, O), left_eye_upper=(1027, 445, O),
                   left_eye_lower=(1003, 445, O), right_eye_outer=(1000, 330, X), right_eye_inner=(1000, 360, X),
                   right_eye_upper=(1012, 345, X), right_eye_lower=(990, 345, X), nose_tip=(935, 375, V),
                   mouth_left=(905, 430, O), mouth_right=(905, 365, X), lip_upper=(915, 397, O),
                   lip_lower=(895, 397, O)),
        hands=[((765, 335, 932, 480), "right", "no"), ((298, 647, 411, 756), "left", "no")],
        phone=None),
    "D05": dict(  # drinking from a bottle (bottle not labelled in DMS), clear glasses
        person=((300, 200, 1240, 960), "worn_correct"),
        face=face((925, 400, 1235, 700), "unknown", "unknown", "clear", "other"),
        face13=pts(left_eye_outer=(1070, 610, O), left_eye_inner=(1070, 545, O), left_eye_upper=(1085, 575, O),
                   left_eye_lower=(1055, 575, O), right_eye_outer=(1070, 440, O), right_eye_inner=(1070, 485, O),
                   right_eye_upper=(1085, 460, O), right_eye_lower=(1055, 460, O), nose_tip=(985, 520, V),
                   mouth_left=(940, 615, O), mouth_right=(940, 555, O), lip_upper=(950, 585, O),
                   lip_lower=(930, 585, O)),
        hands=[((350, 218, 450, 310), "right", "yes"), ((595, 560, 760, 890), "left", "no")],
        phone=None),
    "D06": dict(  # both hands on the belt (fastening) -> seatbelt unknown
        person=((420, 260, 1240, 960), "worn_correct"),
        face=face((1000, 300, 1230, 620), "unknown", "unknown", "clear", "other"),
        face13=pts(left_eye_outer=(1095, 440, O), left_eye_inner=(1095, 405, O), left_eye_upper=(1110, 422, O),
                   left_eye_lower=(1080, 422, O), right_eye_outer=(1090, 330, X), right_eye_inner=(1090, 365, X),
                   right_eye_upper=(1105, 348, X), right_eye_lower=(1075, 348, X), nose_tip=(1030, 402, V),
                   mouth_left=(1020, 480, V), mouth_right=(1025, 435, X), lip_upper=(1030, 455, V),
                   lip_lower=(1010, 460, V)),
        hands=[((635, 415, 750, 485), "right", "no"), ((610, 460, 750, 610), "left", "no")],
        phone=None),
}


def attr_xml(attrs, ind):
    return "".join(f'{ind}<attribute name="{k}">{escape(v)}</attribute>\n' for k, v in attrs.items())


def box_xml(label, b, attrs):
    x1, y1, x2, y2 = b
    return (f'    <box label="{label}" source="manual" occluded="0" xtl="{x1:.2f}" ytl="{y1:.2f}" '
            f'xbr="{x2:.2f}" ybr="{y2:.2f}" z_order="0">\n' + attr_xml(attrs, "      ") + "    </box>\n")


def image_xml(iid, name, w, h, frame_meta, shapes, skeleton=None):
    s = f'  <image id="{iid}" name="{name}" width="{w}" height="{h}">\n'
    s += '    <tag label="frame_meta" source="manual">\n' + attr_xml(frame_meta, "      ") + "    </tag>\n"
    for label, b, attrs in shapes:
        s += box_xml(label, b, attrs)
    if skeleton:
        s += '    <skeleton label="face13" source="manual" z_order="0">\n'
        for n in FACE13:
            x, y, f = skeleton[n]
            s += (f'      <points label="{n}" source="manual" outside="{int(f == X)}" occluded="{int(f == O)}" '
                  f'points="{x:.2f},{y:.2f}">\n      </points>\n')
        s += "    </skeleton>\n"
    return s + "  </image>\n"


def build():
    frames = []
    for code, d in DMS.items():
        shapes = [("person", d["person"][0], {"seat": "driver", "seatbelt": d["person"][1]}), d["face"]]
        for b, side, wheel in d["hands"]:
            shapes.append(("hand", b, {"whose": "driver", "side": side, "on_wheel": wheel}))
        if d["phone"]:
            shapes.append(("phone", d["phone"][0], {"state": d["phone"][1]}))
        frames.append((f"{code}.png", D_W, D_H, meta("ir"), shapes, d["face13"]))
    for code, d in OMS.items():
        frames.append((f"{code}_ir.png", OMS_W, OMS_H, meta("ir"), d.get("ir", d["rgb"]), None))
        frames.append((f"{code}_rgb.png", OMS_W, OMS_H, meta("rgb"), d["rgb"], None))
    frames.sort(key=lambda f: f[0])
    body = "".join(image_xml(i, *f) for i, f in enumerate(frames))
    return '<?xml version="1.0" encoding="utf-8"?>\n<annotations>\n  <version>1.1</version>\n' + body + "</annotations>\n"


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    xml = build()
    with open(os.path.join(out, "annotations.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    for name in ("part_A.zip", "part_B.zip", "export_final.zip"):
        with zipfile.ZipFile(os.path.join(out, name), "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("annotations.xml", xml)
    print("wrote", out)
