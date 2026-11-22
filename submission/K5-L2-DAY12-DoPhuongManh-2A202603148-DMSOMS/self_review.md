# Tự đánh giá — Đỗ Phương Mạnh · G04

## 1. Tự rà soát 4 cảnh

| Ảnh | Đối tượng | Loại lỗi | Ghi chú | Đã sửa? |
|---|---|---|---|---|
| S01_rgb | vật xanh ở ghế `rear_left` | `wrong_class` | Lúc đầu gán `object`; so với S07 thì đây là ghế nâng trống (có tựa đầu, tai ghế), phải là `child_seat`, `occupied = no` | Có |
| S02_rgb | vật họa tiết ở ghế `rear_right` | `wrong_class` | Lúc đầu gán `object`; có vỏ nôi và quai giống nôi trong S05, phải là `infant_seat` | Có |
| D02 | `face13` hai mắt | `ok` | Script báo WARN trái/phải theo trục x; kiểm bằng trục y thì mắt trái có y lớn hơn, nên đúng | Không cần |
| D05 | `face13` điểm mắt | `ok` | Mắt sau tròng kính không thấy rõ, nên `eye_* = unknown` và 8 điểm mắt có cờ `occluded`, khớp với nhau | Không cần |

## 2. Lỗi mình lặp lại nhiều nhất hôm nay

Lỗi: `box`, vẽ box `face` ở OMS quá hẹp. Lỗi lặp lại ở 4 cảnh S02, S04, S05, S08: box chỉ ôm vùng mắt và mũi, thiếu phần từ má tới tai. Review chéo phát hiện ra (IoU với box của bạn chỉ 0.39–0.58). Lỗi thứ hai là `wrong_class` ở S01, S02 (ghế trẻ em, nôi trống gán thành `object`), mình đã tự phát hiện khi soát lại.

Vì sao mình mắc: đặt box theo vùng sáng, dễ thấy nhất của mặt, quên định nghĩa 4.1 là "trán đến cằm, tai đến tai".

Lần sau tránh bằng cách: sau khi vẽ box `face`, kiểm lại bốn mép: mép trái và phải phải chạm tai (hoặc mép má nếu tai bị che), mép trên ở chân tóc, mép dưới ở cằm. Với vật ở OMS, trước khi chọn `object` thì kiểm tra tựa đầu, tai ghế, quai xách.

## 3. Ghi chú về disagreement_log

Một dòng bạn đúng và mình sai: D02 `hand.side`. Mình gán tay là `left` vì tay nằm phía y lớn. Bạn chỉ ra tay đó nối với cánh tay phải đang giơ qua đầu rồi vòng xuống. Mình học được: `side` phải lần theo cánh tay về tới vai, không xét theo vị trí bàn tay trong ảnh (GUIDE 4.4-2, 4.7).

Tổng kết 94 dòng: 64 dòng mình đúng, 28 dòng bạn đúng, 2 dòng cả hai cùng sai (tay phải ở D03 không nhìn thấy nên bỏ box). Các chỗ sửa nằm trong `export_final_v2.zip`. Không hỏi được coach, nên các ca mơ hồ (trẻ ngồi trong ghế, `phone` ở D04, kính ở D03) được phân xử theo guideline và schema coach cập nhật.
