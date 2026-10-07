from flask import Flask, request, abort, redirect, url_for, jsonify, make_response
from markupsafe import escape

app = Flask(__name__)
app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {"name": "Phan Thị Hương Diệu", "lop": "K47E",
                   "scores": {"PMMNM": 8.5, "CSDL": 9.0, "MMT": 9.0}},
    "23T1020002": {"name": "Huỳnh Nguyễn Minh Trí", "lop": "K47E",
                   "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Thảo Vy", "lop": "K47B",
                   "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Ngô Võ Kiều Tâm", "lop": "K47B",
                   "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Nguyễn Thị Bảo Trâm", "lop": "K47A",
                   "scores": {}},
    "23T1020006": {"name": "Trần Thị Thanh Thảo", "lop": "K47C",
                   "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}


from flask import Flask, request, abort, redirect, url_for, jsonify, make_response
from markupsafe import escape

app = Flask(__name__)
app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A",
                   "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A",
                   "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B",
                   "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B",
                   "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A",
                   "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C",
                   "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}


def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)


def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"


def student_summary(mssv):
    s = STUDENTS[mssv]
    avg = average(s["scores"])
    return {
        "mssv": mssv,
        "name": s["name"],
        "lop": s["lop"],
        "scores": s["scores"],
        "average": avg,
        "rank": rank(avg),
    }


def layout(title, body):
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>{escape(title)} - Sổ điểm</title>
</head>
<body>
  <nav>
    <a href="{url_for('home')}">Trang chủ</a> ·
    <a href="{url_for('student_list')}">Sinh viên</a> ·
    <a href="{url_for('search')}">Tìm kiếm</a>
  </nav>
  <h1>{escape(title)}</h1>
  {body}
</body>
</html>"""


def class_names():
    return sorted({s["lop"] for s in STUDENTS.values()})


@app.route("/")
def home():
    body = f"""
  <p>Tổng số sinh viên: {len(STUDENTS)}</p>
  <p>Số lớp: {len(class_names())}</p>
  <ul>
    <li><a href="{url_for('student_list')}">Danh sách sinh viên</a></li>
    <li><a href="{url_for('api_students')}">API JSON sinh viên</a></li>
  </ul>"""
    return layout("Trang chủ", body)


@app.route("/students")
def student_list():
    lop = request.args.get("lop", "")

    filters = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for name in class_names():
        filters.append(
            f'<a href="{url_for("student_list", lop=name)}">{escape(name)}</a>'
        )
    filter_bar = "<p>" + " | ".join(filters) + "</p>"

    rows = ""
    for mssv, s in STUDENTS.items():
        if lop and s["lop"].lower() != lop.lower():
            continue
        info = student_summary(mssv)
        avg = "—" if info["average"] is None else info["average"]
        rows += f"""
    <tr>
      <td><a href="{url_for('student_detail', mssv=mssv)}">{escape(mssv)}</a></td>
      <td>{escape(info['name'])}</td>
      <td>{escape(info['lop'])}</td>
      <td>{escape(avg)}</td>
      <td>{escape(info['rank'])}</td>
    </tr>"""

    if rows:
        table = f"""
  <table border="1" cellpadding="6">
    <tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr>{rows}
  </table>"""
    else:
        table = "<p>Không có sinh viên phù hợp.</p>"

    return layout("Danh sách sinh viên", filter_bar + table)


@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    info = student_summary(mssv)
    avg = "—" if info["average"] is None else info["average"]

    rows = "".join(
        f"<tr><td>{escape(course)}</td><td>{escape(score)}</td></tr>"
        for course, score in info["scores"].items()
    )
    if rows:
        table = f"""
  <table border="1" cellpadding="6">
    <tr><th>Học phần</th><th>Điểm</th></tr>{rows}
  </table>"""
    else:
        table = "<p>Chưa có điểm học phần nào.</p>"

    short = url_for("short_link", mssv=mssv)
    body = f"""
  <p>Họ tên: {escape(info['name'])}</p>
  <p>MSSV: {escape(mssv)}</p>
  <p>Lớp: <a href="{url_for('student_list', lop=info['lop'])}">{escape(info['lop'])}</a></p>
  <p>Điểm TB: {escape(avg)} · Xếp loại: {escape(info['rank'])}</p>
  {table}
  <p><a href="{url_for('student_export', mssv=mssv)}">Tải bảng điểm (CSV)</a></p>
  <p>Link rút gọn: <a href="{short}">{escape(short)}</a></p>"""
    return layout(info["name"], body)


@app.route("/sv/<mssv>")
def short_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)


@app.route("/students/<mssv>/export")
def student_export(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    lines = ["hoc_phan,diem"]
    for course, score in STUDENTS[mssv]["scores"].items():
        lines.append(f"{course},{score}")
    resp = make_response("\n".join(lines) + "\n")
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return resp


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()

    results = []
    if q:
        for mssv, s in STUDENTS.items():
            if q.lower() in s["name"].lower() or q.lower() in mssv.lower():
                results.append(mssv)

    form = f"""
  <form method="get" action="{url_for('search')}">
    <input type="text" name="q" value="{escape(q)}">
    <button type="submit">Tìm</button>
  </form>"""

    summary = ""
    items = ""
    if q:
        summary = f"<p>Tìm thấy {len(results)} kết quả cho “{escape(q)}”</p>"
        for mssv in results:
            name = STUDENTS[mssv]["name"]
            items += (
                f'<li><a href="{url_for("student_detail", mssv=mssv)}">'
                f"{escape(mssv)} - {escape(name)}</a></li>"
            )
        items = f"<ul>{items}</ul>"

    return layout("Tìm kiếm", form + summary + items)


@app.route("/api/students")
def api_students():
    lop = request.args.get("lop")
    raw = request.args.get("min_avg")

    min_avg = None
    if raw is not None:
        try:
            min_avg = float(raw)
        except ValueError:
            abort(400, description="min_avg phải là một số.")

    result = []
    for mssv in STUDENTS:
        info = student_summary(mssv)
        if lop and info["lop"].lower() != lop.lower():
            continue
        if min_avg is not None and (info["average"] is None or info["average"] < min_avg):
            continue
        result.append(info)
    return jsonify(result)


@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return jsonify(student_summary(mssv))


@app.route("/api/students/<mssv>/scores/<course>",
           methods=["GET", "PUT", "DELETE"])
def course_score(mssv, course):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    course = course.upper()
    scores = STUDENTS[mssv]["scores"]

    if request.method == "GET":
        if course not in scores:
            abort(404, description=f"Sinh viên {mssv} chưa có điểm học phần {course}.")
        return jsonify({"mssv": mssv, "course": course, "score": scores[course]})

    if request.method == "DELETE":
        if course not in scores:
            abort(404, description=f"Sinh viên {mssv} chưa có điểm học phần {course}.")
        del scores[course]
        return "", 204

    raw = request.args.get("score")
    if raw is None:
        abort(400, description="Thiếu tham số score.")
    try:
        score = float(raw)
    except ValueError:
        abort(400, description="score phải là một số.")
    if score < 0 or score > 10:
        abort(400, description="score phải nằm trong khoảng 0 đến 10.")

    existed = course in scores
    scores[course] = score

    body = {
        "mssv": mssv,
        "course": course,
        "score": score,
        "average": average(scores),
    }
    location = url_for("course_score", mssv=mssv, course=course)
    if not existed:
        return jsonify(body), 201, {"Location": location}
    return jsonify(body), 200


ERROR_TITLES = {
    400: "Dữ liệu không hợp lệ",
    404: "Không tìm thấy",
    405: "Phương thức không được hỗ trợ",
}


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    title = ERROR_TITLES[error.code]

    if request.path.startswith("/api/"):
        return jsonify({"error": title, "detail": error.description}), error.code

    body = f"""
  <p>Mã lỗi: {error.code}</p>
  <p>{escape(error.description)}</p>"""
    return layout(title, body), error.code