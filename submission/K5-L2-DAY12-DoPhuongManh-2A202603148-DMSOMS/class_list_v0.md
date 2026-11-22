# Danh sách lớp v0 — Đỗ Phương Mạnh · G04

Viết tiếp từ slide 54 bài giảng. Mỗi lớp trả lời câu hỏi: **model cần nhận ra cái này để làm gì?**

## DMS

| # | Lớp / thuộc tính | Giá trị | Để làm gì (chức năng DMS) | Nhìn thấy được trên IR? |
|---|---|---|---|---|
| 1 | `eye_state` (từng mắt) | open / closed / unknown | Phát hiện buồn ngủ: đo tỉ lệ thời gian mắt nhắm (PERCLOS), chớp mắt dài | Có, trừ khi tròng kính phản xạ đèn NIR (D05) hoặc mắt bị tay, tay áo che (D02) |
| 2 | `gaze_zone` | road, mirror_l/r/c, cluster, center, lap, other | Phát hiện mất tập trung: nhìn ngoài vùng `road` quá N giây thì cảnh báo | Một phần: suy từ hướng đầu và mắt; trên ảnh xoay 90° khó xác định, nên nhiều khung phải ghi `other` |
| 3 | `face13` (13 điểm mặt) | 13 điểm + cờ occluded/outside | Ước lượng tư thế đầu (yaw/pitch), độ mở mắt và miệng (ngáp) | Có với mặt rộng từ 60 px; điểm ở phía mặt quay đi phải đánh cờ `outside` |
| 4 | `hand.on_wheel` | yes / no / unknown, theo `side` | Kiểm tra tài xế còn giữ vô lăng, tiêu chí bàn giao quyền lái trên xe tự lái cấp 2–3 | Có (hình dạng tay); tay sát mép vô lăng thì khó phân biệt, ghi `unknown` (D04, D05) |
| 5 | `phone.state` | held / mounted / lap | Phát hiện dùng điện thoại khi lái (nghe gọi, nhắn tin) | Một phần: màn hình tối trên NIR, chỉ nhận được qua cạnh và góc máy; không thấy hình dạng thì không vẽ |
| 6 | `glasses` | none / clear / sun / unknown | Chọn cách đo mắt; báo độ tin cậy thấp khi đeo kính râm | Khó: kính râm có thể trông trong suốt trên NIR (D06) |
| 7 | `driver.seatbelt` | worn_correct / worn_incorrect / not_worn / unknown | Nhắc thắt dây an toàn; ghi nhận dây đeo sai cách | Có (dải tối chéo ngực); đang thắt dở thì ghi `unknown` (D06) |
| 8 | `drink_eat` (đề xuất mới) | none / drinking / eating | Phân loại mất tập trung do ăn uống (D05 uống chai nước); hiện bị gộp vào "không gán" | Có (chai, cốc có hình dạng rõ trên NIR) |

## OMS

| # | Lớp / thuộc tính | Giá trị | Để làm gì (chức năng OMS) | Nhìn thấy được trên IR? |
|---|---|---|---|---|
| 1 | `person` + `seat` | theo 5 ghế | Đếm người theo ghế: nhắc thắt dây ghế sau, điều chỉnh túi khí | Có (hình dạng người) |
| 2 | `person.seatbelt` | not_worn / worn_* / unknown | Nhắc thắt dây ghế sau (quy định mới về nhắc dây an toàn ghế sau) | Một phần: ban đêm RGB không thấy (S08_rgb); IR-sim thấy rõ hơn |
| 3 | `child_seat` + `occupied` | no / unknown / yes (bản coach cập nhật) | Phát hiện trẻ bị bỏ quên trong xe (CPD); nhắc cài ghế trẻ em | Có (tựa đầu, tai ghế) |
| 4 | `infant_seat` + `facing` | rear / front | Tắt túi khí ghế trước khi có nôi quay về sau; nhắc quên em bé | Có (quai xách, vỏ nôi) |
| 5 | `object.type` | bag / box / cup / other | Nhắc quên đồ khi rời xe; phân biệt vật với người để không báo nhầm chưa thắt dây | Có, nhưng mất màu nên phải nhận bằng hình dạng (S06, S07) |
| 6 | `frame_meta.camera_blocked` | yes / no | Biết khi camera bị che để không đưa ra quyết định sai (fail-safe) | Có |
| 7 | `child` (đề xuất mới) | có / không, theo ghế | Trẻ ngồi ghế trẻ em hiện chỉ được mã hóa gián tiếp qua `occupied`; CPD cần biết có trẻ thật hay chỉ có vật | Có (S01, S03, S04, S08 của G04 đều có trẻ ngồi) |

## 2 câu hỏi leo thang

1. Câu hỏi: GUIDE §3 ghi "bộ ảnh không có trẻ em ngồi", nhưng bộ G04 có trẻ ngồi trong ghế trẻ em ở 4 cảnh, và schema coach gửi đã thêm `occupied = yes`. Trẻ ngồi trong ghế có cần thêm box `person` (và `face`) không, hay chỉ ghi `child_seat.occupied = yes`?
   Khung ví dụ: G04 S04_rgb (ghế `rear_left`), G04 S01_rgb (ghế `rear_right`).
   Tạm gán thế nào và vì sao: chỉ vẽ `child_seat` với `occupied = yes`, không vẽ `person`, vì guideline §4.2 chỉ yêu cầu `person` cho người lớn. Thông tin có trẻ đã nằm trong `occupied`.

2. Câu hỏi: `infant_seat.facing` chỉ có `rear` và `front`, không có `unknown`. Với nôi xách trống, đặt nghiêng, không thấy rõ đầu nôi hướng về đâu thì gán thế nào?
   Khung ví dụ: G04 S02_rgb (nôi trống ở ghế `rear_right`).
   Tạm gán thế nào và vì sao: ghi `rear` vì nôi xách thường lắp quay về sau, nhưng như vậy là đoán, trái với quy tắc 4.4-1. Đề xuất thêm giá trị `unknown` cho `facing`.
