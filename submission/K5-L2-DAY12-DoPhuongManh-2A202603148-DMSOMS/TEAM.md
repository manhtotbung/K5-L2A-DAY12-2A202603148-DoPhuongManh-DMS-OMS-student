# TEAM — Ngày 12

Mã bộ ảnh: **G04** · Hình thức: cá nhân

| Họ tên | MSSV | Đã gán đủ 22 ảnh? | Review chéo với (peer diff) | Số dòng disagreement đã xử lý |
|---|---|---|---|---|
| Đỗ Phương Mạnh | 2A202603148 | có | Nguyễn Thị Minh Trang (2A202603107) | 94 (mine 64 · peer 28 · both_wrong 2) |

Ca hai bạn vẫn không thống nhất và đã hỏi coach (ghi tên ảnh + đối tượng):

- Không còn ca nào. Không hỏi được coach, nên 24 dòng ban đầu chưa thống nhất được phân xử theo guideline:
  - Trẻ ngồi trong ghế (S01, S03, S04, S05, S08): trẻ không phải `object` (4.1 định nghĩa object là đồ vật mang theo); schema coach thêm `occupied = yes` để ghi ghế có trẻ, nên ghi `yes`.
  - D04 `phone`: phóng to không thấy cạnh, góc hay màn hình nên không vẽ (4.7).
  - D03 `glasses`: không chắc nên `unknown` (4.5). D03 tay phải: cả hai cùng sai, không thấy bàn tay nên bỏ box (4.4-1).

## Cá nhân

### DoPhuongManh-2A202603148
- Phần mình làm: gán 22 ảnh cốt lõi của G04, tự kiểm ở checkpoint A, B và lần cuối, viết ir_log và class_list_v0.
- Điều mình học được hôm nay: ghế gọi theo xe (trái ảnh là `rear_right`), trái/phải mặt theo người kể cả khi ảnh xoay 90°, và trên ảnh IR phải nhận vật bằng hình dạng chứ không bằng màu.
