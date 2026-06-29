from flask import Flask, jsonify, request, send_from_directory
import json
import os
import tempfile
from datetime import datetime


app = Flask(__name__, static_folder="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resolve_data_dir():
    configured_dir = os.environ.get("DATA_DIR", "").strip()
    if configured_dir:
        return os.path.abspath(configured_dir)
    render_disk_path = os.environ.get("RENDER_DISK_PATH", "").strip()
    if render_disk_path:
        return os.path.join(os.path.abspath(render_disk_path), "Boletas_de_Pago")
    return os.path.join(tempfile.gettempdir(), "Boletas_de_Pago")


DATA_DIR = resolve_data_dir()
JSON_DB_PATH = os.path.join(DATA_DIR, "payroll_records.json")


def ensure_storage_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json_records():
    ensure_storage_dir()
    if not os.path.exists(JSON_DB_PATH):
        return []
    with open(JSON_DB_PATH, "r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    return [
        item for item in data
        if isinstance(item, dict)
        and isinstance(item.get("payload"), dict)
        and item.get("id") is not None
    ]


def save_json_records(records):
    ensure_storage_dir()
    with open(JSON_DB_PATH, "w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=True, indent=2)


def save_payroll_record_json(payload, employee_code, employee_dni, employee_name, year, month):
    records = load_json_records()
    updated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    record = {
        "id": None,
        "employee_code": employee_code,
        "employee_dni": employee_dni,
        "year": year,
        "month": month,
        "employee_name": employee_name,
        "payload": payload,
        "updated_at": updated_at,
    }
    match_index = next(
        (
            idx
            for idx, item in enumerate(records)
            if item.get("employee_code") == employee_code
            and item.get("employee_dni") == employee_dni
            and item.get("year") == year
            and item.get("month") == month
        ),
        None,
    )
    if match_index is None:
        record["id"] = (max((item.get("id", 0) for item in records), default=0) + 1)
        records.append(record)
    else:
        record["id"] = records[match_index].get("id")
        records[match_index] = record
    save_json_records(records)
    return record


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    return jsonify(
        {
            "ok": True,
            "project": "Boletas de Pago",
            "message": "Base inicial lista para continuar el desarrollo.",
            "storage_path": JSON_DB_PATH,
        }
    )


@app.route("/api/payroll-record", methods=["PUT"])
def save_payroll_record():
    try:
        payload = request.get_json(silent=True) or {}
        worker = payload.get("worker") or {}
        period = payload.get("period") or {}

        try:
            year = int(period.get("year"))
            month = int(period.get("month"))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "Periodo invalido"}), 400

        employee_code = str(worker.get("code") or "").strip()
        employee_dni = str(worker.get("dni") or "").strip()
        employee_name = str(worker.get("name") or "").strip()
        record = save_payroll_record_json(payload, employee_code, employee_dni, employee_name, year, month)
        return jsonify(
            {
                "ok": True,
                "message": "Registro guardado correctamente.",
                "storage": "file",
                "record_id": record["id"],
                "updated_at": record["updated_at"],
            }
        )
    except Exception as exc:
        return jsonify(
            {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
        ), 500


@app.route("/api/payroll-records", methods=["GET"])
def list_payroll_records():
    records = load_json_records()
    summaries = []
    for item in records:
        payload = item.get("payload") or {}
        worker = payload.get("worker") or {}
        period = payload.get("period") or {}
        payroll = payload.get("payroll") or {}
        totals = payroll.get("totals") or {}
        summaries.append(
            {
                "id": item.get("id"),
                "employee_code": item.get("employee_code") or worker.get("code", ""),
                "employee_dni": item.get("employee_dni") or worker.get("dni", ""),
                "employee_name": item.get("employee_name") or worker.get("name", ""),
                "year": item.get("year") or period.get("year"),
                "month": item.get("month") or period.get("month"),
                "updated_at": item.get("updated_at", ""),
                "net_total": totals.get("totalNeto"),
            }
        )
    summaries.sort(key=lambda item: ((item.get("year") or 0), (item.get("month") or 0), item.get("updated_at") or ""), reverse=True)
    return jsonify({"ok": True, "records": summaries, "storage_path": JSON_DB_PATH})


@app.route("/api/payroll-record/<int:record_id>", methods=["GET"])
def get_payroll_record(record_id):
    records = load_json_records()
    record = next((item for item in records if item.get("id") == record_id), None)
    if not record:
        return jsonify({"ok": False, "error": "Registro no encontrado"}), 404
    return jsonify({"ok": True, "record": record})


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0").strip() or "0.0.0.0"
    try:
        port = int(os.environ.get("PORT", "5001"))
    except ValueError:
        port = 5001
    app.run(host=host, port=port, debug=False, use_reloader=False)
