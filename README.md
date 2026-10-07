# Bài tập tổng hợp Chương 3: Sổ điểm

- Họ tên: Phan Thị Hương Diệu
- MSSV: 23T1020098
- Lớp: K47E

Ứng dụng Flask quản lý sổ điểm lớp học: giao diện web (danh sách, chi tiết, tìm kiếm, xuất CSV) và API JSON (đọc, thêm, sửa, xoá điểm từng học phần).

## Cách chạy

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app sodiem run --debug --port 8000
```

## 1. Kết quả `flask --app sodiem routes`

```
Endpoint            Methods           Rule
------------------  ----------------  ------------------------------------
api_student_detail  GET               /api/students/<mssv>
api_students        GET               /api/students
course_score        DELETE, GET, PUT  /api/students/<mssv>/scores/<course>
home                GET               /
search              GET               /search
short_link          GET               /sv/<mssv>
static              GET               /static/<path:filename>
student_detail      GET               /students/<mssv>
student_export      GET               /students/<mssv>/export
student_list        GET               /students
```

Đủ 10 dòng (kể cả `static`).

## 2. Kết quả các lệnh curl

Khai báo biến: `B=http://127.0.0.1:8000` và `S=$B/api/students/23T1020005/scores`.

### 2.1. `curl -i $B/sv/23T1020001`

```
HTTP/1.1 301 MOVED PERMANENTLY
Content-Type: text/html; charset=utf-8
Location: /students/23T1020001
```

### 2.2. `curl -i $B/students/23T1020001/export`

```
HTTP/1.1 200 OK
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename=diem_23T1020001.csv

hoc_phan,diem
PMMNM,8.5
CSDL,7.0
MMT,9.0
```

### 2.3. `curl "$B/api/students?lop=k47a&min_avg=7"`

```
[
  {
    "average": 8.17,
    "lop": "K47A",
    "mssv": "23T1020001",
    "name": "Nguyễn Văn An",
    "rank": "Khá",
    "scores": {
      "CSDL": 7.0,
      "MMT": 9.0,
      "PMMNM": 8.5
    }
  }
]
```

### 2.4. `curl -i "$B/api/students?min_avg=abc"`

```
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json

{
  "detail": "min_avg phải là một số.",
  "error": "Dữ liệu không hợp lệ"
}
```

### 2.5. `curl -i $B/api/students/999`

```
HTTP/1.1 404 NOT FOUND
Content-Type: application/json

{
  "detail": "Không có sinh viên với MSSV = 999.",
  "error": "Không tìm thấy"
}
```

### 2.6. `curl -i -X PUT "$S/web?score=9"`

```
HTTP/1.1 201 CREATED
Content-Type: application/json
Location: /api/students/23T1020005/scores/WEB

{
  "average": 9.0,
  "course": "WEB",
  "mssv": "23T1020005",
  "score": 9.0
}
```

### 2.7. `curl -X PUT "$S/WEB?score=7.5"`

```
{
  "average": 7.5,
  "course": "WEB",
  "mssv": "23T1020005",
  "score": 7.5
}
```

(Trạng thái 200, không có header `Location`.)

### 2.8. `curl -i -X PUT "$S/WEB?score=11"`

```
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json

{
  "detail": "score phải nằm trong khoảng 0 đến 10.",
  "error": "Dữ liệu không hợp lệ"
}
```

### 2.9. `curl -i -X DELETE $S/WEB`

```
HTTP/1.1 204 NO CONTENT
```

Body rỗng.

### 2.10. `curl -i -X POST $S/WEB`

```
HTTP/1.1 405 METHOD NOT ALLOWED
Content-Type: application/json

{
  "detail": "The method is not allowed for the requested URL.",
  "error": "Phương thức không được hỗ trợ"
}
```

### 2.11. `curl -i -X POST $B/students`

```
HTTP/1.1 405 METHOD NOT ALLOWED
Content-Type: text/html; charset=utf-8

<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Phương thức không được hỗ trợ - Sổ điểm</title>
</head>
...
  <h1>Phương thức không được hỗ trợ</h1>
  <p>Mã lỗi: 405</p>
  <p>The method is not allowed for the requested URL.</p>
...
```

## 3. Trả lời câu hỏi

**Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?**

Hai mã này nói hai chuyện khác nhau. Mã 301 là chuyển hướng vĩnh viễn: `/sv/<mssv>` chỉ là địa chỉ rút gọn, nội dung thật nằm ở `/students/<mssv>`, nên server bảo client đi sang địa chỉ kia (trong header `Location`). Mã 201 nghĩa là server vừa tạo mới một tài nguyên, ở đây là điểm của một học phần chưa có; header `Location` cho client biết địa chỉ của tài nguyên vừa tạo. Một bên là "chỗ này đã dời sang chỗ kia", một bên là "tôi vừa tạo ra thứ mới, nó nằm ở đây".

**Thêm điểm cho 23T1020005 rồi khởi động lại server, điểm đó còn không? Vì sao?**

Không còn. Dữ liệu nằm trong dict `STUDENTS` ở bộ nhớ (RAM) của tiến trình Flask. Khi khởi động lại, file `sodiem.py` được chạy lại từ đầu và dict được tạo lại từ dữ liệu mẫu trong mã nguồn, nên điểm vừa thêm mất. Muốn giữ lại thì phải lưu ra nơi bền vững như file hoặc cơ sở dữ liệu.

**Vì sao dùng được `request` trong hàm xử lý lỗi dù nó không phải view function? (Câu 9)**

Khi Flask nhận một request, nó đẩy request context vào trước khi xử lý và chỉ gỡ ra khi xử lý xong. Hàm xử lý lỗi được gọi bên trong khoảng thời gian đó, nên `request` vẫn truy cập được. Điều kiện để dùng `request` là đang xử lý một request, không phải đang ở trong view function.