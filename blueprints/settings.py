from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import dbFetchAll, dbFetchOne, dbQuery
from utils import login_required, role_required, verify_csrf
import config

bp = Blueprint("settings", __name__)

SETTINGS_FIELDS = [
    "company_name", "company_email", "company_phone", "company_address",
    "currency", "currency_symbol", "tax_rate", "low_stock_threshold",
]


@bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("admin")
def index():
    if request.method == "POST" and verify_csrf(request.form.get("csrf_token", "")):
        try:
            low_stock_threshold = int(request.form.get("low_stock_threshold", "10"))
            if low_stock_threshold < 0:
                raise ValueError
        except (TypeError, ValueError):
            flash("Low stock threshold must be a whole number of 0 or more.", "error")
            return redirect(url_for("settings.index"))

        for key in SETTINGS_FIELDS:
            val = request.form.get(key, "").strip()
            if key == "low_stock_threshold":
                val = str(low_stock_threshold)
            existing = dbFetchOne("SELECT id FROM settings WHERE setting_key = ?", (key,))
            if existing:
                dbQuery("UPDATE settings SET setting_value = ? WHERE setting_key = ?", (val, key))
            else:
                dbQuery("INSERT INTO settings (setting_key, setting_value) VALUES (?, ?)", (key, val))
        flash("Settings saved successfully.", "success")
        return redirect(url_for("settings.index"))

    rows = dbFetchAll("SELECT setting_key, setting_value FROM settings")
    s = {r["setting_key"]: r["setting_value"] for r in rows}

    return render_template(
        "settings/index.html",
        page_title="Settings", active_menu="settings",
        s=s, server_time=datetime.now().strftime("%d %b %Y %H:%M:%S"),
    )
