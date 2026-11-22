"""Fill verdict / guideline_rule / action in disagreement_log.csv (rules decided in peer review with G04 peer).
usage: python work/fill_disagreements.py disagreement_log.csv
"""
import csv
import sys

CHILD = ("mine", "4.1 object (đồ vật mang theo) + schema coach có occupied=yes",
         "Trẻ không phải đồ vật nên không vẽ object; schema coach thêm occupied=yes chính là để ghi ghế có trẻ -> giữ occupied=yes")


def decide(img, label, field, issue, mine, peer):
    code = img.split(".")[0]
    if field == "light":
        return ("mine", "4.4-1", "Giữ unknown: không có bằng chứng ngày/đêm trên ảnh NIR (đèn IR làm sáng như nhau)")
    if label == "face" and field == "box" and code.startswith("S0"):
        if code.startswith("S06"):
            return ("peer", "4.5", "Thêm box face (thấy chóp mũi + miệng), thuộc tính mắt/kính unknown")
        return ("peer", "4.1 face (tai đến tai)", "Box face của mình quá hẹp; nới theo box của bạn")
    if label == "face" and field == "eye_right" and code.startswith("S04"):
        return ("peer", "4.5", "Thấy khe mắt phải mở -> open")
    if code == "S08_rgb" and label == "face":
        return ("peer", "4.5", f"Mặt S08_rgb vẫn đủ sáng để thấy -> {field}={peer}")
    if code == "S08_rgb" and field == "seatbelt":
        return ("mine", "4.4-1; 4.7", "Giữ unknown: áo tối trên RGB đêm, không thấy rõ có/không dây; không suy từ S08_ir")
    if field == "occupied" or (label == "object" and code[:3] in ("S01", "S04", "S05", "S08")):
        return CHILD
    if code.startswith("S03") and label == "object":
        if code == "S03_rgb":
            return ("mine", "4.4-1", "Cốc và trẻ: không gán cốc trên RGB vì không thấy, không suy từ ảnh IR; trẻ -> hỏi coach")
        return ("mine", "4.4-5; 4.1 object", "Box cốc sát vật (box bạn gồm cả khóa dây an toàn); trẻ không phải object")
    if field == "facing":
        return ("mine", "4.1 infant_seat", "Đầu bé ở phía tựa ghế sau, chân về phía camera -> quay về trước xe (front)")
    if field == "gaze_zone":
        return ("mine", "4.5 gaze_zone", "Không thấy mắt rõ -> other (không chắc), không ghi road")
    if code == "D02" and field == "side":
        return ("peer", "4.4-2; 4.7", "Tay này nối với cánh tay phải giơ qua đầu -> side=right")
    if code == "D04" and label == "phone":
        return ("mine", "4.7 phone", "Phóng to chỉ thấy ngón tay và một chấm sáng, không có cạnh/góc/màn hình điện thoại -> không vẽ phone")
    if code == "D04" and label == "hand":
        return ("peer", "4.1 hand; 4.7", "Box tay phải nới tới cổ tay; tay trái đặt trên đùi -> on_wheel=no")
    if code == "D05" and label == "hand":
        return ("peer", "4.7 hand", "Tay phải đang nắm vành vô lăng -> sửa box, on_wheel=yes")
    if code == "D06" and field == "seatbelt":
        return ("peer", "4.7 seatbelt", "Dây đã chéo vai xuống hông, tay chỉ cầm dây -> worn_correct")
    if code == "D03" and field == "seatbelt":
        return ("mine", "4.7 seatbelt", "Áo khoác tối che dải chéo, không thấy dây sai cách -> unknown, không ghi worn_incorrect")
    if code == "D03" and field == "glasses":
        return ("mine", "4.5 glasses", "Vùng mắt tối, không chắc có gọng; guideline: không chắc thì unknown, không chọn none")
    if code == "D03" and label == "hand":
        return ("both_wrong", "4.1 hand; 4.4-1", "Phóng to: chỗ của mình là cổ tay áo, chỗ của bạn là vùng tối, đều không thấy bàn tay phải -> bỏ box")
    if code == "D01" and label == "face13":
        return ("peer", "4.6", "Mặt quay đi, không đoán chắc vị trí miệng -> outside")
    if label == "face13":
        return ("mine", "4.6", "Giữ cờ của mình: occluded khi đoán chắc vị trí (bị tay/chai che), outside khi không đặt được")
    return ("ambiguous", "", "Cần xem lại cùng bạn")


def main(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    for r in rows:
        r["verdict"], r["guideline_rule"], r["action"] = decide(
            r["image"], r["label"], r["field"], r["issue"], r["mine"], r["peer"])
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r["verdict"] for r in rows))


if __name__ == "__main__":
    main(sys.argv[1])
