from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# ========== Admin ==========
from UserStory11_Admin_login import LoginController as AdminLoginController
from UserStory12_Admin_logout import LogOutPageController as AdminLogoutController
from UserStory6_Admin_CreateProfile import UserAccount as AdminUserAccount           # noqa: F401 (imported for parity)
from UserStory7_Admin_ViewUsrProfile import UserProfile as AdminUserProfile         # noqa: F401
from UserStory9_Admin_suspendUserProfile import UserProfile as AdminSuspendProfile  # noqa: F401
from UserStory10_Admin_SearchUsrProfile import UserProfile as AdminSearchProfile    # noqa: F401

# ========== CSR ==========
from UserStory18_CSR_Login import LoginController as CSRLoginController
from UserStory19_LogoutRequest import LogOutPageController as CSRLogoutController   # noqa: F401
from UserStory17_SearchRequest import SearchPrevRequestController as CSRSearchController  # noqa: F401

# ========== Platform Manager (PM) ==========
# We will prefer first-party validation for platform users (works with hashed + plaintext).
# We still import the controllers to keep parity / optional usage.
from UserStory41_PM_login import LoginController as PMLoginController
from UserStory42_PM_logout import LogOutPageController as PMLogoutController

# PM category controllers (legacy form pages)
from UserStory33_PM_createCategory import CreateCategoryController
from UserStory34_PM_viewSCategory import ViewCategoriesController
from UserStory37_PM_SearchCetegory import SearchCategoryController


# ========= App / Utilities =========
app = Flask(__name__)
app.secret_key = "super_secret_key"

BASE_DIR = Path(__file__).resolve().parent

USERS_FILE      = BASE_DIR / "users.json"
CATS_FILE       = BASE_DIR / "categories.json"
REQUESTS_FILE   = BASE_DIR / "requests.json"
MATCHES_FILE    = BASE_DIR / "matches.json"
SHORTLISTS_FILE = BASE_DIR / "shortlists.json"

# ---------- JSON helpers ----------
def _ensure_file(path: Path, default):
    if not path.exists():
        path.write_text(json.dumps(default, indent=2))

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def load_json(path: Path, default):
    _ensure_file(path, default)
    try:
        raw = path.read_text()
        return json.loads(raw) if raw.strip() else default
    except Exception:
        return default

def save_json(path: Path, data):
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)

def load_all_users():
    _ensure_file(USERS_FILE, {})
    raw = USERS_FILE.read_text() or "{}"
    return json.loads(raw)

def save_all_users(data):
    save_json(USERS_FILE, data)

def migrate_users_file():
    """Backfill id/uid/etc so Admin dashboard can list old accounts."""
    data = load_all_users()
    max_id = 0
    for bucket in data.values():
        for rec in bucket.values():
            try:
                max_id = max(max_id, int(rec.get("id", 0)))
            except Exception:
                pass

    changed = False
    next_id = max_id + 1
    for role, bucket in (data or {}).items():
        for uname, rec in bucket.items():
            if "id" not in rec:
                rec["id"] = next_id
                rec["uid"] = f"U-{next_id:03d}"
                rec.setdefault("fullName", uname)
                rec.setdefault("email", "")
                rec.setdefault("username", uname)
                rec.setdefault("role", role)
                rec.setdefault("status", "Active")
                rec.setdefault("createdAt", now_iso())
                rec["updatedAt"] = now_iso()
                next_id += 1
                changed = True

    if changed:
        save_all_users(data)

def verify_password(stored: str, provided: str) -> bool:
    if not stored:
        return False
    if isinstance(stored, str) and (stored.startswith("scrypt:") or stored.startswith("pbkdf2:")):
        return check_password_hash(stored, provided)
    return stored == provided

def normalize_role(role: str) -> str:
    role = (role or "").strip().lower()
    if role == "user":
        return "pin"
    return role

def ui_status_to_file(status_ui: str) -> str:
    s = (status_ui or "").strip().lower()
    if s == "active":
        return "Active"
    if s in ("inactive", "suspended"):
        return "Suspended"
    return "Active"

def file_status_to_ui(status_file: str) -> str:
    s = (status_file or "").strip().lower()
    if s == "active":
        return "active"
    if s in ("suspended", "inactive"):
        return "inactive"
    return "active"

def _find_by_id(data, user_id: int):
    for role, bucket in (data or {}).items():
        for uname, rec in bucket.items():
            if isinstance(rec, dict) and rec.get("id") == user_id:
                return role, uname, rec
    return None, None, None

def _flatten(all_users):
    flat = []
    for role_bucket, users in (all_users or {}).items():
        for uname, rec in users.items():
            rid = rec.get("id")
            if not rid:
                continue
            flat.append({
                "id": rid,
                "uid": rec.get("uid"),
                "fullName": rec.get("fullName") or uname,
                "name": rec.get("fullName") or uname,
                "email": rec.get("email") or "",
                "username": rec.get("username") or uname,
                "role": (rec.get("role") or role_bucket or "").lower(),  # admin|csr|pin|platform
                "status": file_status_to_ui(rec.get("status") or "Active"),  # active|inactive
                "createdAt": rec.get("createdAt"),
                "updatedAt": rec.get("updatedAt"),
            })
    flat.sort(key=lambda u: int(u["id"]))
    return flat

# --------- Platform login helper (first-party, hashed/legacy compatible) ---------
def _platform_login(username: str, password: str):
    data = load_all_users()
    platform_bucket = (data or {}).get("platform") or {}
    rec = platform_bucket.get(username or "")
    if not rec:
        return False, "Invalid PM credentials."
    # Block suspended
    if (rec.get("status") or "").lower() in ("suspended", "inactive"):
        return False, "Account is suspended."
    if not verify_password(rec.get("password", ""), password or ""):
        return False, "Invalid PM credentials."
    # OK
    return True, rec

# =========================================================
# HOME + LOGOUT (Shared)
# =========================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))

# =========================================================
# API LOGIN ENDPOINT (Handles All Roles) — sets session
# =========================================================
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    role = data.get('role')
    username = data.get('username')
    password = data.get('password')

    def _ok(redirect_path, role_key, name_val=None):
        session.clear()
        session['role'] = role_key        # 'admin' | 'csr' | 'platform' | 'pin'
        session['username'] = username or ""
        session['name'] = name_val or username or ""
        return jsonify({"status": "ok", "redirect": redirect_path})

    # --- ADMIN ---
    if role == 'admin':
        controller = AdminLoginController()
        result = controller.processLogin(username, password)
        if result == "Login successful!":
            return _ok("/user-admin-dashboard", "admin", username)
        return jsonify({"status": "error", "message": "Invalid admin credentials."})

    # --- CSR ---
    if role == 'csr':
        controller = CSRLoginController()
        result = controller.processLogin(username, password)
        if result == "Login successful!":
            return _ok("/csr/dashboard", "csr", username)
        return jsonify({"status": "error", "message": "Invalid CSR credentials."})

    # --- PM / Platform Manager ---
    if role == 'platform':
        # Prefer first-party verification (supports hashed + plaintext), fall back to controller if needed.
        ok, rec_or_msg = _platform_login(username, password)
        if ok:
            display = rec_or_msg.get("fullName") or username
            return _ok("/pm/dashboard", "platform", display)
        # Optional fallback to external controller (kept for compatibility)
        try:
            controller = PMLoginController()
            result = controller.processLogin(username, password) if hasattr(controller, "processLogin") else controller.login(username, password)
            if result == "Login successful!":
                return _ok("/pm/dashboard", "platform", username)
        except Exception:
            pass
        return jsonify({"status": "error", "message": rec_or_msg})

    return jsonify({"status": "error", "message": "Missing or unknown role."}), 400

# =========================================================
# SESSION HELPERS FOR DASHBOARD
# =========================================================
@app.get("/api/whoami")
def api_whoami():
    role = session.get("role")
    name = session.get("name") or session.get("username")
    if not role:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"role": role, "name": name or ""})

@app.post("/api/logout")
def api_logout():
    session.clear()  # <-- fixed: call the function
    return jsonify({"ok": True})

def _login_blocked(role_key: str, username: str) -> bool:
    """Return True if the user exists and is Suspended/Inactive."""
    data = load_all_users() or {}
    rec = ((data.get(role_key) or {}).get(username or "")) or {}
    status = (rec.get("status") or "").strip().lower()
    return status in ("suspended", "inactive")


# =========================================================
# ADMIN PAGES (existing)
# =========================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        controller = AdminLoginController()
        result = controller.processLogin(username, password)
        if "success" in result.lower():
            session['role'] = 'admin'
            session['username'] = username
            session['name'] = username
            flash("Welcome Admin!")
            return redirect(url_for('admin_dashboard'))
        flash(result)
    return render_template('signup.html')

@app.route("/user-admin-dashboard")
def admin_dashboard():
    return render_template("user-admin-dashboard.html")

@app.route('/admin/create-profile', methods=['GET', 'POST'])
def admin_create_profile():
    if request.method == 'POST':
        full_name = request.form['fullName'].strip()
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password']
        role = normalize_role(request.form['role'])  # admin|csr|pin|platform

        status = 'Active'
        data = load_all_users()
        data.setdefault(role, {})
        if username in data[role]:
            flash("Error: Username already exists for this role.")
            return redirect(url_for('admin_dashboard'))

        next_id = 1 + max(
            (rec.get("id", 0) for bucket in data.values() for rec in bucket.values()),
            default=0
        )

        rec = {
            "id": next_id,
            "uid": f"U-{next_id:03d}",
            "fullName": full_name,
            "email": email,
            "username": username,
            "password": generate_password_hash(password),
            "role": role,
            "status": status,
            "createdAt": now_iso(),
            "updatedAt": now_iso()
        }
        data[role][username] = rec
        save_all_users(data)
        flash("Profile created successfully.")
        return redirect(url_for('admin_dashboard'))

    return render_template('CreateUserForm.html')

@app.route('/admin/view-profile')
def admin_view_profile():
    user_id = request.args.get('id', type=int)
    data = load_all_users()
    result = None
    for bucket in data.values():
        for rec in bucket.values():
            if rec.get("id") == user_id:
                result = rec
                break
        if result:
            break
    return render_template('view-requests.html', result=result)

@app.route('/admin/suspend-profile', methods=['POST'])
def admin_suspend_profile():
    user_id = request.form.get('id', type=int)
    data = load_all_users()
    for bucket in data.values():
        for uname, rec in bucket.items():
            if rec.get("id") == user_id:
                rec["status"] = "Suspended"
                rec["updatedAt"] = now_iso()
                save_all_users(data)
                flash("User suspended.")
                return redirect(url_for('admin_dashboard'))
    flash("Error: User not found.")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search-profile')
def admin_search_profile():
    q = (request.args.get('name') or "").strip().lower()
    data = load_all_users()
    flat = [rec for bucket in data.values() for rec in bucket.values()]
    if not q:
        result = flat
    else:
        result = [
            u for u in flat
            if q in (u.get("fullName","").lower())
            or q in (u.get("email","").lower())
            or q in (u.get("username","").lower())
            or q == str(u.get("id","")).lower()
            or q == (u.get("uid","") or "").lower()
            or q == (u.get("role","") or "").lower()
        ]
    return render_template('search-requests.html', result=result)

# =========================================================
# JSON-backed Users API (existing)
# =========================================================
@app.get("/api/users")
def api_users_list():
    data = load_all_users()
    items = _flatten(data)
    q = (request.args.get('q') or '').strip().lower()
    if q:
        items = [
            u for u in items
            if q in (u.get("name","").lower())
            or q in (u.get("email","").lower())
            or q in (u.get("username","").lower())
            or q == (u.get("uid","") or "").lower()
            or q == (u.get("role","") or "").lower()
            or q == str(u.get("id","")).lower()
        ]
    return jsonify(items)

@app.route('/api/users/<int:user_id>', methods=['GET', 'PATCH', 'PUT'])
def api_user_detail(user_id):
    data = load_all_users()
    role, uname, rec = _find_by_id(data, user_id)
    if not rec:
        return jsonify({"error": "Not found"}), 404

    if request.method == 'GET':
        return jsonify(rec)

    payload = request.get_json(force=True, silent=True) or {}

    new_full = payload.get("fullName") or payload.get("name")
    new_email = payload.get("email")
    new_username = payload.get("username")
    new_role_input = payload.get("role")
    new_status_input = payload.get("status")
    new_password = payload.get("password")

    if new_full:
        rec["fullName"] = new_full.strip()
    if new_email:
        rec["email"] = new_email.strip()
    if new_username and new_username.strip() != uname:
        new_username = new_username.strip()
        data[role].pop(uname, None)
        uname = new_username
        rec["username"] = new_username
        data[role][uname] = rec
    elif new_username:
        rec["username"] = new_username.strip()

    if new_password:
        rec["password"] = generate_password_hash(new_password)

    if new_status_input:
        rec["status"] = ui_status_to_file(new_status_input)

    if new_role_input:
        new_bucket = normalize_role(new_role_input)
        if new_bucket and new_bucket != role:
            data.setdefault(new_bucket, {})
            if uname in data[new_bucket] and data[new_bucket][uname].get("id") != user_id:
                return jsonify({"error": "Username already exists in target role"}), 400
            data[role].pop(uname, None)
            role = new_bucket
            data[role][uname] = rec
        rec["role"] = role

    rec["updatedAt"] = now_iso()
    save_all_users(data)
    return jsonify(rec)

@app.post("/api/users/<int:user_id>/status")
def api_user_status(user_id):
    body = request.get_json(force=True, silent=True) or {}
    action = (body.get("action") or "").lower()
    status_ui = (body.get("status") or "").lower()

    data = load_all_users()
    role, uname, rec = _find_by_id(data, user_id)
    if not rec:
        return jsonify({"error": "Not found"}), 404

    if action in ("suspend", "activate"):
        rec["status"] = "Suspended" if action == "suspend" else "Active"
    elif status_ui in ("active", "inactive"):
        rec["status"] = ui_status_to_file(status_ui)
    else:
        return jsonify({"error": "Provide 'action' or 'status'"}), 400

    rec["updatedAt"] = now_iso()
    data[role][uname] = rec
    save_all_users(data)
    return jsonify({"ok": True, "status": rec["status"]})

# =========================================================
# PLATFORM MANAGER PAGES
# =========================================================
@app.route('/pm/login', methods=['GET', 'POST'])
def pm_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        ok, rec_or_msg = _platform_login(username, password)
        if ok:
            session['role'] = 'platform'
            session['username'] = username
            session['name'] = rec_or_msg.get("fullName") or username
            flash("Welcome Platform Manager!")
            return redirect(url_for('pm_dashboard'))

        # Fallback to external controller (optional)
        try:
            controller = PMLoginController()
            result = controller.processLogin(username, password)
            if "success" in (result or "").lower():
                session['role'] = 'platform'
                session['username'] = username
                session['name'] = username
                flash("Welcome Platform Manager!")
                return redirect(url_for('pm_dashboard'))
            flash(result or rec_or_msg)
        except Exception:
            flash(rec_or_msg)

    return render_template('signup.html')

@app.route('/pm/dashboard')
def pm_dashboard():
    return render_template('platform-dashboard.html')

# (Old form routes kept for compatibility)
@app.route('/pm/create-category', methods=['POST'])
def pm_create_category():
    name = request.form['category_name']
    controller = CreateCategoryController()
    result = controller.createCategory(name)
    flash(result)
    return redirect(url_for('pm_dashboard'))

@app.route('/pm/view-category')
def pm_view_category():
    controller = ViewCategoriesController()
    result = controller.viewAll()
    return render_template('view-requests.html', result=result)

@app.route('/pm/search-category')
def pm_search_category():
    name = request.args.get('name')
    controller = SearchCategoryController()
    result = controller.searchCategory(name)
    return render_template('search-requests.html', result=result)

@app.route('/pm/logout')
def pm_logout():
    controller = PMLogoutController()
    result = controller.submitLogout()
    session.clear()
    flash(result)
    return redirect(url_for('index'))

# =========================================================
# PLATFORM MANAGER JSON APIs (shared with CSR)
# =========================================================

# ---- Categories (single source of truth) ----
def _seed_categories_if_empty():
    cats = load_json(CATS_FILE, [])
    if cats:
        return cats
    seed = [
        { "id": "CAT-001", "name": "Transportation", "desc": "Rides to appointments and errands", "visibility": "public", "createdAt": now_iso(), "updatedAt": None },
        { "id": "CAT-002", "name": "Home Repair", "desc": "Minor household maintenance and repairs", "visibility": "public", "createdAt": now_iso(), "updatedAt": None },
        { "id": "CAT-003", "name": "Check-in / Companionship", "desc": "Calls or visits to check on wellbeing", "visibility": "hidden", "createdAt": now_iso(), "updatedAt": None },
    ]
    save_json(CATS_FILE, seed)
    return seed

def _load_categories():
    cats = load_json(CATS_FILE, [])
    if not cats:
        cats = _seed_categories_if_empty()
    return cats

def _save_categories(cats):
    save_json(CATS_FILE, cats)

def _next_cat_id(cats):
    max_num = 0
    for c in cats:
        try:
            part = str(c.get("id","")).split("-")[-1]
            num = int(part)
            if num > max_num:
                max_num = num
        except Exception:
            continue
    return f"CAT-{max_num+1:03d}"

@app.get("/api/categories")
def api_categories_list():
    cats = _load_categories()
    q = (request.args.get("q") or "").strip().lower()
    vis = (request.args.get("visibility") or "").strip().lower()  # public|hidden
    if q:
        cats = [c for c in cats if q in (c.get("name","").lower()) or q in (c.get("desc","").lower())]
    if vis in ("public", "hidden"):
        cats = [c for c in cats if (c.get("visibility") or "public").lower() == vis]
    return jsonify(cats)

@app.post("/api/categories")
def api_categories_create():
    body = request.get_json(force=True, silent=True) or {}
    name = (body.get("name") or "").strip()
    desc = (body.get("desc") or "").strip()
    visibility = (body.get("visibility") or "public").strip().lower()
    if not name:
        return jsonify({"error":"Category name is required"}), 400
    if visibility not in ("public","hidden"):
        visibility = "public"

    cats = _load_categories()
    if any(c for c in cats if (c.get("name") or "").lower() == name.lower()):
        return jsonify({"error":"Duplicate category name"}), 400

    new_cat = {
        "id": _next_cat_id(cats),
        "name": name,
        "desc": desc,
        "visibility": visibility,
        "createdAt": now_iso(),
        "updatedAt": None
    }
    cats.append(new_cat)
    _save_categories(cats)
    return jsonify(new_cat), 201

@app.put("/api/categories/<cat_id>")
def api_categories_update(cat_id):
    body = request.get_json(force=True, silent=True) or {}
    name = (body.get("name") or "").strip()
    desc = (body.get("desc") or "").strip()
    visibility = (body.get("visibility") or "").strip().lower() or None

    cats = _load_categories()
    idx = next((i for i, c in enumerate(cats) if str(c.get("id")) == str(cat_id)), -1)
    if idx == -1:
        return jsonify({"error":"Not found"}), 404

    if name:
        cats[idx]["name"] = name
    cats[idx]["desc"] = desc if desc is not None else cats[idx].get("desc","")
    if visibility in ("public","hidden"):
        cats[idx]["visibility"] = visibility
    cats[idx]["updatedAt"] = now_iso()
    _save_categories(cats)
    return jsonify(cats[idx])

@app.delete("/api/categories/<cat_id>")
def api_categories_delete(cat_id):
    cats = _load_categories()
    idx = next((i for i, c in enumerate(cats) if str(c.get("id")) == str(cat_id)), -1)
    if idx == -1:
        return jsonify({"error":"Not found"}), 404

    # Block deletion if any request references this category
    reqs = load_json(REQUESTS_FILE, [])
    in_use = [r for r in reqs if str(r.get("categoryId")) == str(cat_id)]
    if in_use:
        return jsonify({
            "error": "Category is in use by existing requests.",
            "usageCount": len(in_use)
        }), 409

    removed = cats.pop(idx)
    _save_categories(cats)
    return jsonify({"ok": True, "deleted": removed.get("id")})

# Optional CSR-friendly alias — same data
@app.get("/api/request-categories")
def api_request_categories():
    return jsonify(_load_categories())

# =========================================================
# CSR-FACING ENDPOINTS (compat with your CSR HTML)
# =========================================================

# ---- Requests (shared) ----
def _load_requests():
    return load_json(REQUESTS_FILE, [])

def _save_requests(reqs):
    save_json(REQUESTS_FILE, reqs)

def _next_req_id(reqs):
    return 1 + max([int(r.get("id", 0)) for r in reqs] or [0])

def _cat_by_id(cat_id, cats=None):
    cats = cats or _load_categories()
    return next((c for c in cats if str(c.get("id")) == str(cat_id)), None)

def _req_id_to_string(req_id):
    try:
        return f"REQ-{int(req_id)}"
    except Exception:
        return str(req_id)

def _req_string_to_int(sid):
    """Accept 'REQ-123' or '123'."""
    if isinstance(sid, int):
        return sid
    s = str(sid)
    if s.upper().startswith("REQ-"):
        s = s.split("-", 1)[1]
    try:
        return int(s)
    except Exception:
        return None

def _map_req_to_csr(rec, cats_index=None, shortlist_ids=None):
    """Map internal request record to the structure used by CSR UI."""
    rid = _req_id_to_string(rec.get("id"))
    cat_name = rec.get("categoryName")
    cat_id = rec.get("categoryId")
    if not cat_name and cats_index and cat_id:
        c = cats_index.get(str(cat_id))
        if c:
            cat_name = c.get("name")
    title = rec.get("title") or (cat_name or "Assistance")  # fallback title
    created = rec.get("createdAt") or now_iso()
    date_only = (created or now_iso())[:10]  # YYYY-MM-DD
    owner = rec.get("createdBy") or ""
    status = rec.get("status", "pending").strip().title()  # Pending/In Progress/Completed

    shortlist_count = 1 if (shortlist_ids and rid in shortlist_ids) else 0

    return {
        "id": rid,
        "title": title,
        "category": cat_name or "—",
        "date": date_only,
        "created": created,
        "status": status,
        "owner": owner,
        "description": rec.get("description") or "",
        "location": rec.get("location") or "",
        "viewCount": 0,
        "shortlistCount": shortlist_count,
        "assignedTo": rec.get("assignedTo"),
        "assignedAt": rec.get("assignedAt"),
    }

# Create/list requests (JSON)
@app.route("/api/requests", methods=["GET", "POST"])
def api_requests():
    if request.method == "GET":
        reqs = _load_requests()
        cats = _load_categories()
        cat_index = {str(c["id"]): c for c in cats}
        enriched = []
        for r in reqs:
            c = cat_index.get(str(r.get("categoryId")))
            enriched.append({
                **r,
                "expandedCategory": {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "visibility": c.get("visibility")
                } if c else None
            })
        return jsonify(enriched)

    # POST -> create request
    body = request.get_json(force=True, silent=True) or {}
    category_id = body.get("categoryId")
    description = (body.get("description") or "").strip()
    created_by  = body.get("createdBy")
    status      = (body.get("status") or "pending").lower()

    if not category_id:
        return jsonify({"error": "categoryId is required"}), 400

    cats = _load_categories()
    cat = _cat_by_id(category_id, cats)
    if not cat:
        return jsonify({"error": "Invalid categoryId"}), 400

    reqs = _load_requests()
    new_id = _next_req_id(reqs)
    rec = {
        "id": new_id,
        "categoryId": cat["id"],
        "categoryName": cat["name"],
        "description": description,
        "status": status,
        "createdBy": created_by,
        "createdAt": now_iso(),
        "updatedAt": now_iso()
    }
    reqs.append(rec)
    _save_requests(reqs)

    return jsonify({
        **rec,
        "expandedCategory": {
            "id": cat["id"], "name": cat["name"], "visibility": cat["visibility"]
        }
    }), 201

# Update/Delete a single request (JSON)
@app.route("/api/requests/<int:req_id>", methods=["PUT", "PATCH", "DELETE"])
def api_request_detail(req_id):
    reqs = _load_requests()
    idx = next((i for i, r in enumerate(reqs) if int(r.get("id", 0)) == int(req_id)), -1)
    if idx == -1:
        return jsonify({"error": "Not found"}), 404

    if request.method == "DELETE":
        removed = reqs.pop(idx)
        _save_requests(reqs)
        return jsonify({"ok": True, "deleted": removed.get("id")})

    body = request.get_json(force=True, silent=True) or {}
    if "description" in body:
        reqs[idx]["description"] = (body.get("description") or "").strip()
    if "status" in body:
        reqs[idx]["status"] = (body.get("status") or "").strip().lower()

    if "categoryId" in body and body.get("categoryId") is not None:
        cat = _cat_by_id(body.get("categoryId"))
        if not cat:
            return jsonify({"error": "Invalid categoryId"}), 400
        reqs[idx]["categoryId"] = cat["id"]
        reqs[idx]["categoryName"] = cat["name"]

    reqs[idx]["updatedAt"] = now_iso()
    _save_requests(reqs)

    cat = _cat_by_id(reqs[idx]["categoryId"])
    return jsonify({
        **reqs[idx],
        "expandedCategory": {
            "id": cat["id"], "name": cat["name"], "visibility": cat["visibility"]
        } if cat else None
    })

# ---------- CSR aliases used by your CSR HTML ----------

# --- CSR: assign / unassign a request ---
@app.post("/api/csr/requests/<rid>/assign")
def csr_assign_request(rid):
    # Must be logged in (ideally as CSR)
    me = session.get("name") or session.get("username") or "CSR"
    if not session.get("role"):
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    num = _req_string_to_int(rid)
    if num is None:
        return jsonify({"success": False, "message": "Invalid id"}), 400

    reqs = _load_requests()
    idx = next((i for i, r in enumerate(reqs) if int(r.get("id", 0)) == int(num)), -1)
    if idx == -1:
        return jsonify({"success": False, "message": "Not found"}), 404

    current = reqs[idx].get("assignedTo")
    if current and current != me:
        return jsonify({"success": False, "message": f"Already assigned to {current}"}), 409

    reqs[idx]["assignedTo"] = me
    reqs[idx]["assignedAt"] = now_iso()
    # Optional: reflect progress in status while preserving your UI logic
    reqs[idx]["status"] = (reqs[idx].get("status") or "pending").lower()
    _save_requests(reqs)
    return jsonify({"success": True, "assignedTo": me, "assignedAt": reqs[idx]["assignedAt"]})

@app.delete("/api/csr/requests/<rid>/assign")
def csr_unassign_request(rid):
    me = session.get("name") or session.get("username") or "CSR"
    if not session.get("role"):
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    num = _req_string_to_int(rid)
    if num is None:
        return jsonify({"success": False, "message": "Invalid id"}), 400

    reqs = _load_requests()
    idx = next((i for i, r in enumerate(reqs) if int(r.get("id", 0)) == int(num)), -1)
    if idx == -1:
        return jsonify({"success": False, "message": "Not found"}), 404

    # If someone else owns it, block unassign from here
    current = reqs[idx].get("assignedTo")
    if current and current != me:
        return jsonify({"success": False, "message": f"Assigned to {current}"}), 409

    reqs[idx]["assignedTo"] = None
    reqs[idx]["assignedAt"] = None
    _save_requests(reqs)
    return jsonify({"success": True})


# CSR list
@app.get("/api/csr/requests")
def csr_requests_list():
    reqs = _load_requests()
    cats = _load_categories()
    cat_index = {str(c["id"]): c for c in cats}
    shortlist_ids = set(load_json(SHORTLISTS_FILE, []))
    items = [_map_req_to_csr(r, cat_index, shortlist_ids) for r in reqs]
    return jsonify(items)

# CSR detail (with counts)
@app.get("/api/csr/requests/<rid>")
def csr_request_detail(rid):
    num = _req_string_to_int(rid)
    if num is None:
        return jsonify({"success": False, "message": "Invalid id"}), 404
    reqs = _load_requests()
    rec = next((r for r in reqs if int(r.get("id", 0)) == num), None)
    if not rec:
        return jsonify({"success": False, "message": "Not found"}), 404

    cats = _load_categories()
    cat_index = {str(c["id"]): c for c in cats}
    shortlist_ids = set(load_json(SHORTLISTS_FILE, []))
    mapped = _map_req_to_csr(rec, cat_index, shortlist_ids)
    return jsonify({"success": True, "request": mapped})

# CSR search
@app.route("/api/csr/requests/search", methods=["POST", "GET"])
def csr_requests_search():
    if request.method == "POST":
        body = request.get_json(silent=True, force=True) or {}
        kw = (body.get("keyword") or body.get("q") or "").strip().lower()
        cat = (body.get("category") or "").strip()
        status = (body.get("status") or "").strip().lower()
    else:
        kw = (request.args.get("keyword") or request.args.get("q") or "").strip().lower()
        cat = (request.args.get("category") or "").strip()
        status = (request.args.get("status") or "").strip().lower()

    reqs = _load_requests()
    cats = _load_categories()
    cat_index = {str(c["id"]): c for c in cats}
    shortlist_ids = set(load_json(SHORTLISTS_FILE, []))
    rows = [_map_req_to_csr(r, cat_index, shortlist_ids) for r in reqs]

    if kw:
        rows = [r for r in rows if kw in (r["title"] or "").lower()
                or kw in (r["description"] or "").lower()
                or kw in str(r["id"]).lower()]
    if cat:
        rows = [r for r in rows if r["category"] == cat]
    if status:
        rows = [r for r in rows if (r["status"] or "").lower() == status]

    return jsonify({"success": True, "requests": rows, "count": len(rows)})

# CSR shortlist list
@app.get("/api/csr/shortlist")
def csr_shortlist_list():
    ids = set(load_json(SHORTLISTS_FILE, []))
    reqs = _load_requests()
    cats = _load_categories()
    cat_index = {str(c["id"]): c for c in cats}
    rows = []
    for r in reqs:
        rid = _req_id_to_string(r.get("id"))
        if rid in ids:
            rows.append(_map_req_to_csr(r, cat_index, ids))
    return jsonify({"success": True, "requests": rows, "count": len(rows)})

# CSR shortlist save
@app.post("/api/csr/shortlist/save/<rid>")
def csr_shortlist_save(rid):
    rid_str = _req_id_to_string(_req_string_to_int(rid) or rid)
    ids = load_json(SHORTLISTS_FILE, [])
    if rid_str in ids:
        # Return a shaped error your front-end already understands
        return jsonify({"success": False, "message": f"Error: Request '{rid_str}' is already shortlisted."}), 409
    ids.append(rid_str)
    save_json(SHORTLISTS_FILE, ids)
    return jsonify({"success": True, "message": f"Request '{rid_str}' saved to shortlist."})


# --- UN-SHORTLIST (DELETE) ---

@app.delete("/api/csr/shortlist/<rid>")
def csr_shortlist_delete(rid):
    rid_num = _req_string_to_int(rid)
    rid_str = _req_id_to_string(rid_num) if rid_num is not None else _req_id_to_string(rid)
    ids = set(load_json(SHORTLISTS_FILE, []))
    if rid_str in ids:
        ids.remove(rid_str)
        save_json(SHORTLISTS_FILE, list(ids))
        return jsonify({"success": True, "message": f"Request '{rid_str}' removed from shortlist."})
    # idempotent OK if not present
    return jsonify({"success": True, "message": f"Request '{rid_str}' was not in shortlist."})




# =========================================================
# CSR & PM PAGES (HTML)
# =========================================================
@app.route('/csr/dashboard')
def csr_dashboard_page():
    return render_template('csr-dashboard.html')

# =========================================================
# Misc (matches existing JSON pages in your project)
# =========================================================
@app.get("/api/matches")
def api_matches_list():
    matches = load_json(MATCHES_FILE, [])
    return jsonify(matches)

@app.get("/api/shortlists")
def api_shortlists_list():
    short = load_json(SHORTLISTS_FILE, [])
    return jsonify(short)

# =========================================================
# RUN APP
# =========================================================
if __name__ == '__main__':
    _ensure_file(USERS_FILE, {})
    _seed_categories_if_empty()
    _ensure_file(REQUESTS_FILE, [])
    _ensure_file(MATCHES_FILE, [])
    _ensure_file(SHORTLISTS_FILE, [])
    migrate_users_file()
    app.run(debug=True)

