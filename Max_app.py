# maxapp.py — unified backend for CSR, Platform, User Admin, and PIN pages

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import json, os
from datetime import datetime, timezone

# ---- BCE imports (as in your code) ----
from UserStory13_PIN_CreateRequest import CreateRequestPage, CreateRequestController, Request
from UserStory14_PIN_ViewRequest import ViewRequestPage, ViewRequestController, ViewRequestEntity
from UserStory15_PIN_UpdateRequest import UpdateRequestPage, UpdateRequestController, Request as UpdateRequestEntity
from UserStory16_PIN_DeleteRequest import DeleteRequestPage, DeleteRequestController, Request as DeleteRequestEntity
from UserStory17_PIN_SearchRequest import SearchRequestPage, SearchRequestController, Request as SearchRequestEntity
from UserStory18_CSR_Login import LoginPage, LoginController, UserAccount as CSRUserAccount
from UserStory19_PIN_Logout import LogoutPage, LogoutPageController, UserAccount as LogoutUserAccount
from UserStory20_CSR_ViewRequest import ViewRequestPage as CSRViewRequestPage, ViewRequestController as CSRViewRequestController, Request as CSRViewRequestEntity
from UserStory21_CSR_ViewShortlist import ViewShortlistPage as CSRViewShortlistPage, ViewShortlistController as CSRViewShortlistController, Request as CSRViewShortlistEntity
from UserStory22_CSR_SearchRequest import SearchRequestPage as CSRSearchRequestPage, SearchRequestController as CSRSearchRequestController, Request as CSRSearchRequestEntity
from UserStory23_CSR_SearchShortlist import SearchSLRequestPage as CSRSearchSLRequestPage, SearchSLRequestController as CSRSearchSLRequestController, Request as CSRSearchSLRequestEntity
from UserStory24_CSR_SaveRequestShortlist import SaveRequestPage as CSRSaveRequestPage, SaveRequestSLController as CSRSaveRequestSLController, Request as CSRSaveRequestEntity
from UserStory27_PIN_ViewRequestViewCount import ViewCountPage, ViewCountController, Request as ViewCountRequestEntity
from UserStory28_PIN_ViewShortlistCount import ShortlistCountPage, ShortlistCountController, Request as ShortlistCountRequestEntity
from UserStory29_PIN_SearchPreviousRequest import SearchPrevRequestPage, SearchPrevRequestController, Request as SearchPrevRequestEntity
from UserStory30_PIN_ViewPreviousRequest import ViewPrevRequestPage, ViewPrevRequestController, Request as ViewPrevRequestEntity
from UserStory31_CSR_SearchPreviousRequest import SearchPrevRequestPage as CSRSearchPrevRequestPage, SearchPrevRequestController as CSRSearchPrevRequestController, Request as CSRSearchPrevRequestEntity
from UserStory32_CSR_ViewPreviousRequest import ViewPrevRequestPage as CSRViewPrevRequestPage, ViewPrevRequestController as CSRViewPrevRequestController, Request as CSRViewPrevRequestEntity

# --------------------------------------------------------------------
app = Flask(__name__, static_folder='static', static_url_path='/static')

app.config['SECRET_KEY'] = 'super_secret_key'

USERS_FILE = 'users.json'
REQUESTS_FILE = 'requests.json'
SHORTLISTS_FILE = 'shortlists.json'  # per-CSR shortlist store
_in_memory_form_requests = []   # legacy WTForms demo page only

# -----------------------------
# Utilities / persistence
# -----------------------------
def _normalize_role(raw: str) -> str:
    """Accept UI labels like 'CSR Representative' and normalize to 'csr'."""
    if not raw:
        return 'csr'
    r = str(raw).strip().lower()
    if r in ('csr representative', 'csr rep'):
        return 'csr'
    return r

def _ensure_file(path: str, default):
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default, f, indent=2)

def init_users_file():
    _ensure_file(USERS_FILE, {})

def load_users():
    """Load users.json into a dict shaped like { 'admin': {...}, 'csr': {...}, 'pin': {...} }"""
    init_users_file()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def init_requests_file():
    _ensure_file(REQUESTS_FILE, [])

def load_requests():
    init_requests_file()
    with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_requests(requests_data):
    with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(requests_data, f, indent=2)

# -- per-CSR shortlist persistence --
def _ensure_shortlists_file():
    if not os.path.exists(SHORTLISTS_FILE):
        with open(SHORTLISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)

def load_shortlists():
    _ensure_shortlists_file()
    try:
        with open(SHORTLISTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_shortlists(data):
    with open(SHORTLISTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def verify_password(stored: str, provided: str) -> bool:
    """
    Accept both Werkzeug-hashed (scrypt/pbkdf2) and legacy plaintext passwords,
    so existing accounts in users.json continue to work.
    """
    if not isinstance(stored, str):
        return False
    prefix = stored.split(':', 1)[0].lower() if ':' in stored else ''
    if prefix in ('scrypt', 'pbkdf2'):
        try:
            return check_password_hash(stored, provided)
        except Exception:
            return False
    # plaintext fallback
    return stored == provided

def _require_role(role_name: str) -> bool:
    return (session.get('role') or '').lower() == role_name.lower()

def _pin_identity():
    """Return (username_to_stamp, display_name) for the logged-in PIN user, or (None, None)."""
    if not _require_role('pin'):
        return None, None
    uname = session.get('username') or session.get('name') or ''
    disp = session.get('name') or session.get('username') or ''
    return uname, disp

# -----------------------------
# BCE component wiring
# -----------------------------
csr_login_controller = LoginController(
    entity=CSRUserAccount(),
    load_users_func=lambda: load_users(),
    password_checker=verify_password
)
csr_login_page = LoginPage(controller=csr_login_controller)

pin_logout_controller = LogoutPageController(
    entity=LogoutUserAccount(),
    session_manager=lambda: session.clear()
)
pin_logout_page = LogoutPage(controller=pin_logout_controller)

create_request_controller = CreateRequestController(
    entity=Request(),
    load_requests_func=lambda: load_requests(),
    save_requests_func=lambda requests_data: save_requests(requests_data)
)
create_request_page = CreateRequestPage(controller=create_request_controller)

view_request_controller = ViewRequestController(
    entity=ViewRequestEntity(),
    load_requests_func=lambda: load_requests()
)
view_request_page = ViewRequestPage(controller=view_request_controller)

view_count_controller = ViewCountController(
    entity=ViewCountRequestEntity(),
    load_requests_func=lambda: load_requests()
)
view_count_page = ViewCountPage(controller=view_count_controller)

shortlist_count_controller = ShortlistCountController(
    entity=ShortlistCountRequestEntity(),
    load_requests_func=lambda: load_requests()
)
shortlist_count_page = ShortlistCountPage(controller=shortlist_count_controller)

search_prev_request_controller = SearchPrevRequestController(
    entity=SearchPrevRequestEntity(),
    load_requests_func=lambda: load_requests()
)
search_prev_request_page = SearchPrevRequestPage(controller=search_prev_request_controller)

view_prev_request_controller = ViewPrevRequestController(
    entity=ViewPrevRequestEntity(),
    load_requests_func=lambda: load_requests()
)
view_prev_request_page = ViewPrevRequestPage(controller=view_prev_request_controller)

csr_search_prev_request_controller = CSRSearchPrevRequestController(
    entity=CSRSearchPrevRequestEntity(),
    load_requests_func=lambda: load_requests()
)
csr_search_prev_request_page = CSRSearchPrevRequestPage(controller=csr_search_prev_request_controller)

csr_view_prev_request_controller = CSRViewPrevRequestController(
    entity=CSRViewPrevRequestEntity(),
    load_requests_func=lambda: load_requests()
)
csr_view_prev_request_page = CSRViewPrevRequestPage(controller=csr_view_prev_request_controller)

csr_view_request_controller = CSRViewRequestController(
    entity=CSRViewRequestEntity(),
    load_requests_func=lambda: load_requests()
)
csr_view_request_page = CSRViewRequestPage(controller=csr_view_request_controller)

csr_view_shortlist_controller = CSRViewShortlistController(
    entity=CSRViewShortlistEntity(),
    load_requests_func=lambda: load_requests()
)
csr_view_shortlist_page = CSRViewShortlistPage(controller=csr_view_shortlist_controller)

csr_search_shortlist_controller = CSRSearchSLRequestController(
    entity=CSRSearchSLRequestEntity(),
    load_requests_func=lambda: load_requests()
)
csr_search_shortlist_page = CSRSearchSLRequestPage(controller=csr_search_shortlist_controller)

csr_save_shortlist_controller = CSRSaveRequestSLController(
    entity=CSRSaveRequestEntity(),
    load_requests_func=lambda: load_requests(),
    save_requests_func=lambda requests_data: save_requests(requests_data)
)
csr_save_shortlist_page = CSRSaveRequestPage(controller=csr_save_shortlist_controller)

update_request_controller = UpdateRequestController(
    entity=UpdateRequestEntity(),
    load_requests_func=lambda: load_requests(),
    save_requests_func=lambda requests_data: save_requests(requests_data)
)
update_request_page = UpdateRequestPage(controller=update_request_controller)

delete_request_controller = DeleteRequestController(
    entity=DeleteRequestEntity(),
    load_requests_func=lambda: load_requests(),
    save_requests_func=lambda requests_data: save_requests(requests_data)
)
delete_request_page = DeleteRequestPage(controller=delete_request_controller)

search_request_controller = SearchRequestController(
    entity=SearchRequestEntity(),
    load_requests_func=lambda: load_requests()
)
search_request_page = SearchRequestPage(controller=search_request_controller)

csr_search_request_controller = CSRSearchRequestController(
    entity=CSRSearchRequestEntity(),
    load_requests_func=lambda: load_requests()
)
csr_search_request_page = CSRSearchRequestPage(controller=csr_search_request_controller)

# -----------------------------
# Forms (legacy sample page)
# -----------------------------
class CreateRequestForm(FlaskForm):
    service_title = StringField('service title', validators=[DataRequired(), Length(min=1, max=100)])
    category = SelectField('category', choices=[('transport', 'transport'), ('wheelchair', 'wheelchair'), ('repair', 'repair'), ('other', 'other')], validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired(), Length(min=10)])
    location = StringField('position', validators=[DataRequired()])
    date_time = DateTimeField('date/time', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('submitting the request')

# -----------------------------
# HTML pages (render_template)
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/csr-dashboard.html')
def csr_dashboard():
    return render_template('csr-dashboard.html')

@app.route('/user-admin-dashboard.html')
def user_admin_dashboard():
    return render_template('user-admin-dashboard.html')

@app.route('/platform-dashboard.html')
def platform_dashboard():
    return render_template('platform-dashboard.html')

# PIN pages
@app.route('/view-requests.html')
def view_requests_html():
    return render_template('view-requests.html')

@app.route('/search-requests.html')
def search_requests_html():
    return render_template('search-requests.html')

@app.route('/request-detail.html')
def request_detail_html():
    return render_template('request-detail.html')

@app.route('/update-request.html')
def update_request_html():
    return render_template('update-request.html')

@app.route('/create-request.html')
def create_request_html():
    return render_template('create-request.html')

@app.route('/forgot-password.html')
def forgot_password_html():
    return render_template('forgot-password.html')

# Friendly aliases used in some front-ends
@app.route('/csr/dashboard')
def csr_dashboard_alias():
    return redirect('/csr-dashboard.html')

@app.route('/view-requests')
def view_requests_alias():
    return redirect('/view-requests.html')

# -----------------------------
# Auth
# -----------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    role = _normalize_role(data.get('role'))
    if not all([username, password, role]):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    users = load_users()
    users.setdefault(role, {})
    if username in users[role]:
        return jsonify({'success': False, 'message': 'Username already exists for this role.'}), 400

    users[role][username] = {
        'password': generate_password_hash(password),
        'username': username
    }
    save_users(users)
    return jsonify({'success': True, 'message': 'Account created successfully!'})

# Front-end (index.html) expects /api/login
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    role = _normalize_role(data.get('role'))

    if not all([username, password, role]):
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    # block suspended CSR or PIN before checking password
    if role in ('csr', 'pin') and _is_suspended(role, username):
        return jsonify({'status': 'error', 'message': 'Account is suspended.'}), 403

    login_result = csr_login_page.enterCredentials(username, password, role)
    if isinstance(login_result, str):
        return jsonify({'status': 'error', 'message': login_result}), 400

    if login_result.get('success'):
        session['username'] = username
        session['role'] = login_result.get('role', role)
        session['name'] = username
        redirect_to = '/csr/dashboard' if session['role'] == 'csr' else '/view-requests'
        return jsonify({'status': 'ok', 'redirect': redirect_to})

    return jsonify({'status': 'error', 'message': login_result.get('message', 'Invalid credentials.')}), 401

# Optional: raw /login also works
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    role = _normalize_role(data.get('role'))
    if not all([username, password, role]):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    login_result = csr_login_page.enterCredentials(username, password, role)
    if isinstance(login_result, str):
        return jsonify({'success': False, 'message': login_result}), 400

    if login_result.get('success'):
        session['username'] = username
        session['role'] = login_result.get('role', role)
        session['name'] = username
        return jsonify({'success': True, 'message': login_result.get('message', 'Login successful!'), 'role': session['role']})
    return jsonify({'success': False, 'message': login_result.get('message', 'Invalid credentials.')}), 401

# JSON logout used by CSR/PIN dashboards
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'ok': True})

# Form/old logout kept for compatibility
@app.route('/logout', methods=['POST'])
def logout():
    username = session.get('username')
    role = session.get('role', 'pin')
    result = pin_logout_page.submitLogout(username=username, role=role)
    session.clear()
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 400
    if isinstance(result, dict):
        return jsonify(result)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Who am I (used by CSR/PIN dashboards)
@app.route('/api/whoami', methods=['GET'])
def whoami():
    return jsonify({
        'username': session.get('username'),
        'name': session.get('name') or session.get('username') or '',
        'role': session.get('role')
    })

# -----------------------------
# APIs consumed by CSR pages (unchanged)
# -----------------------------
@app.route('/api/csr/requests', methods=['GET'])
def get_all_requests():
    all_requests = load_requests()
    formatted = []
    for req in all_requests:
        formatted.append({
            'id': req.get('id'),
            'title': req.get('title'),
            'category': req.get('category'),
            'date': req.get('date'),
            'created': req.get('created', req.get('date')),
            'status': req.get('status', 'Pending'),
            'owner': req.get('owner'),
            'owner_name': req.get('owner'),
            'description': req.get('description', ''),
            'location': req.get('location', ''),
            'address': req.get('location', ''),
            'assignedTo': req.get('assignedTo'),
            'assignedAt': req.get('assignedAt'),
            'viewCount': req.get('viewCount', 0),
            'shortlistCount': req.get('shortlistCount', 0),
        })
    return jsonify(formatted)

def _inject_counts_and_assignment(result, request_id):
    vc = view_count_page.showViewCount(request_id)
    if isinstance(vc, int):
        result['viewCount'] = vc
    sc = shortlist_count_page.showShortlistCount(request_id)
    if isinstance(sc, int):
        result['shortlistCount'] = sc
    # Pull assignment from storage
    for r in load_requests():
        if str(r.get('id')) == str(request_id):
            result['assignedTo'] = r.get('assignedTo')
            result['assignedAt'] = r.get('assignedAt')
            break
    return result

@app.route('/api/requests/search', methods=['POST', 'GET'])
def search_requests_api():
    # Collect incoming filters (title/category/status/keyword…)
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = {
            'id': request.args.get('id'),
            'title': request.args.get('title'),
            'category': request.args.get('category'),
            'date': request.args.get('date'),
            'status': request.args.get('status'),
            'keyword': request.args.get('keyword') or request.args.get('q')
        }
        data = {k: v for k, v in data.items() if v is not None}

    # Run your existing search controller
    result = search_request_page.submitSearch(data)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 400
    if not isinstance(result, list):
        return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

    # 🔒 If this is a PIN user, ONLY return their own requests
    role = (session.get('role') or '').lower()
    if role == 'pin':
        me = (session.get('username') or session.get('name') or '').strip().lower()
        owned = [
            r for r in result
            if (str(r.get('owner') or r.get('owner_name') or '').strip().lower() == me)
        ]
        return jsonify({'success': True, 'requests': owned, 'count': len(owned)})

    # Non-PIN roles (CSR/Admin/etc.) keep existing behavior
    return jsonify({'success': True, 'requests': result, 'count': len(result)})

@app.route('/api/csr/requests/search', methods=['POST', 'GET'])
def csr_search_requests_api():
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = {
            'id': request.args.get('id'),
            'title': request.args.get('title'),
            'category': request.args.get('category'),
            'date': request.args.get('date'),
            'status': request.args.get('status'),
            'keyword': request.args.get('keyword') or request.args.get('q')
        }
        data = {k: v for k, v in data.items() if v is not None}
    result = csr_search_request_page.submitSearch(data)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 400
    if isinstance(result, list):
        return jsonify({'success': True, 'requests': result, 'count': len(result)})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

# ---------- per-CSR shortlist (these replace the old global shortlist routes) ----------
@app.route('/api/csr/shortlist', methods=['GET'])
def csr_shortlist_get():
    if not _require_role('csr'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    me = session.get('name') or session.get('username') or ''
    all_reqs = load_requests()
    sl = load_shortlists()
    my_ids = set(sl.get(me, []))

    by_id = {str(r.get('id')): r for r in all_reqs}
    results = []
    for rid in my_ids:
        r = by_id.get(str(rid)) or by_id.get(str(rid).replace('REQ-',''))
        if r:
            results.append(r)

    payload = []
    for r in results:
        payload.append({
            'id': r.get('id'),
            'title': r.get('title'),
            'category': r.get('category'),
            'date': r.get('date'),
            'created': r.get('created', r.get('date')),
            'status': r.get('status', 'Pending'),
            'owner': r.get('owner'),
            'description': r.get('description', ''),
            'location': r.get('location', ''),
            'assignedTo': r.get('assignedTo'),
            'assignedAt': r.get('assignedAt'),
            'viewCount': r.get('viewCount', 0),
            'shortlistCount': r.get('shortlistCount', 0),
        })
    return jsonify({'success': True, 'requests': payload, 'count': len(payload)})

@app.route('/api/csr/shortlist/save/<request_id>', methods=['POST'])
def csr_shortlist_save(request_id):
    if not _require_role('csr'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    me = session.get('name') or session.get('username') or ''
    rid = str(request_id if str(request_id).upper().startswith('REQ-') else f'REQ-{request_id}')

    sl = load_shortlists()
    current = sl.get(me, [])
    if rid in current:
        return jsonify({'success': True, 'message': 'Already shortlisted'}), 200

    current.append(rid)
    sl[me] = current
    save_shortlists(sl)

    # optional: keep per-request 'shortlisted_by' compatible for analytics
    reqs = load_requests()
    for r in reqs:
        if str(r.get('id')) == rid or str(r.get('id')) == rid.replace('REQ-',''):
            by = set(r.get('shortlisted_by') or [])
            by.add(me)
            r['shortlisted_by'] = sorted(by)
            r['shortlisted'] = True  # legacy flag (means shortlisted by at least one person)
            break
    save_requests(reqs)

    return jsonify({'success': True, 'message': 'Saved to your shortlist'})

@app.route('/api/csr/shortlist/<request_id>', methods=['DELETE'])
def csr_shortlist_remove(request_id):
    if not _require_role('csr'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    me = session.get('name') or session.get('username') or ''
    rid = str(request_id if str(request_id).upper().startswith('REQ-') else f'REQ-{request_id}')

    sl = load_shortlists()
    current = sl.get(me, [])
    if rid in current:
        current = [x for x in current if x != rid]
        sl[me] = current
        save_shortlists(sl)
        # remove my mark from per-request metadata (not others')
        reqs = load_requests()
        for r in reqs:
            if str(r.get('id')) == rid or str(r.get('id')) == rid.replace('REQ-',''):
                arr = list(r.get('shortlisted_by') or [])
                if me in arr:
                    arr.remove(me)
                r['shortlisted_by'] = arr
                r['shortlisted'] = bool(arr)  # keep true if others still have it
                break
        save_requests(reqs)
        return jsonify({'success': True, 'message': 'Removed from your shortlist'})
    return jsonify({'success': True, 'message': 'Already not in your shortlist'}), 200

# ----- Helper function to block suspended user

def _is_suspended(role_key: str, username: str) -> bool:
    """
    Return True if the user exists and is Suspended/Inactive in users.json.
    Works with your shared users.json produced by the admin app.
    """
    data = load_users() or {}
    rec = ((data.get(role_key) or {}).get(username or "")) or {}
    status = (rec.get("status") or "").strip().lower()
    return status in ("suspended", "inactive")


# ---------- View Count (read) ----------
@app.route('/api/requests/<request_id>/views', methods=['GET'])
def get_request_view_count(request_id):
    result = view_count_page.showViewCount(request_id)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    return jsonify({'success': True, 'viewCount': result})

# ---------- View Count (increment & persist) ----------
def _canon_req_id(rid):
    s = str(rid).strip()
    if s.upper().startswith("REQ-"):
        s = s.split("-", 1)[1]
    return f"REQ-{s}"

def _req_plain_id(s):
    if isinstance(s, int):
        return str(s)
    s = str(s)
    return s.split('-', 1)[1] if s.upper().startswith('REQ-') else s

def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def _increment_view_count(request_id: str, by: int = 1) -> int:
    """Persistently increment viewCount on the request and return new count."""
    cid = _canon_req_id(request_id)
    reqs = load_requests()
    new_val = None
    for r in reqs:
        if _canon_req_id(r.get('id')) == cid:
            r['viewCount'] = int(r.get('viewCount', 0) or 0) + by
            r['lastViewedAt'] = _now_iso()
            new_val = r['viewCount']
            break
    if new_val is None:
        return 0
    save_requests(reqs)
    return new_val

@app.route('/api/requests/<request_id>/views', methods=['POST'])
def increment_request_view_count(request_id):
    new_count = _increment_view_count(request_id, by=1)
    return jsonify({'success': True, 'viewCount': new_count})

@app.route('/api/requests/<request_id>/shortlist-count', methods=['GET'])
def get_request_shortlist_count(request_id):
    result = shortlist_count_page.showShortlistCount(request_id)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    return jsonify({'success': True, 'shortlistCount': result})

@app.route('/api/requests/completed/<request_id>', methods=['GET'])
def get_completed_request_detail(request_id):
    result = view_prev_request_page.getRequestDetail(request_id, requestStatus='Completed')
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    if isinstance(result, dict):
        # ensure we return persisted viewCount
        reqs = load_requests()
        vc = 0
        for r in reqs:
            if _canon_req_id(r.get('id')) == _canon_req_id(request_id):
                vc = int(r.get('viewCount', 0) or 0)
                break
        result['viewCount'] = vc
        sc = shortlist_count_page.showShortlistCount(request_id)
        if isinstance(sc, int):
            result['shortlistCount'] = sc
        return jsonify({'success': True, 'request': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

@app.route('/api/csr/requests/completed/<request_id>', methods=['GET'])
def csr_get_completed_request_detail(request_id):
    result = csr_view_prev_request_page.getRequestDetail(request_id, requestStatus='Completed')
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    if isinstance(result, dict):
        reqs = load_requests()
        vc = 0
        for r in reqs:
            if _canon_req_id(r.get('id')) == _canon_req_id(request_id):
                vc = int(r.get('viewCount', 0) or 0)
                break
        result['viewCount'] = vc
        sc = shortlist_count_page.showShortlistCount(request_id)
        if isinstance(sc, int):
            result['shortlistCount'] = sc
        return jsonify({'success': True, 'request': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

# -------------- CSR: assign / unassign / complete (Max_app) --------------
@app.route('/api/csr/requests/<request_id>/assign', methods=['POST'])
def max_csr_assign_request(request_id):
    if not session.get('role'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    me = session.get('name') or session.get('username') or 'CSR'

    rid = _req_plain_id(request_id)
    reqs = load_requests()
    found = next((r for r in reqs if _req_plain_id(r.get('id')) == rid), None)
    if not found:
        return jsonify({'success': False, 'message': 'Not found'}), 404

    found['assignedTo'] = me
    found['assignedAt'] = _now_iso()
    if (found.get('status') or '').lower() != 'completed':
        found['status'] = 'in progress'
    save_requests(reqs)
    return jsonify({'success': True, 'request': found})

@app.route('/api/csr/requests/<request_id>/assign', methods=['DELETE'])
def max_csr_unassign_request(request_id):
    if not session.get('role'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    rid = _req_plain_id(request_id)
    reqs = load_requests()
    found = next((r for r in reqs if _req_plain_id(r.get('id')) == rid), None)
    if not found:
        return jsonify({'success': False, 'message': 'Not found'}), 404

    found['assignedTo'] = None
    found['assignedAt'] = None
    if (found.get('status') or '').lower() != 'completed':
        found['status'] = 'pending'
    save_requests(reqs)
    return jsonify({'success': True, 'request': found})

@app.route('/api/csr/requests/<request_id>/complete', methods=['POST'])
def max_csr_complete_request(request_id):
    if not session.get('role'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    me = session.get('name') or session.get('username') or 'CSR'

    rid = _req_plain_id(request_id)
    reqs = load_requests()
    found = next((r for r in reqs if _req_plain_id(r.get('id')) == rid), None)
    if not found:
        return jsonify({'success': False, 'message': 'Not found'}), 404

    found['status'] = 'Completed'
    found['completedAt'] = _now_iso()
    if not found.get('assignedTo'):
        found['assignedTo'] = me
        found['assignedAt'] = _now_iso()
    save_requests(reqs)
    return jsonify({'success': True, 'request': found})

# ---- CRUD for PIN requests ----
@app.route('/api/requests', methods=['POST'])
def create_request_api():
    # Stamp the owner from the logged-in PIN user (front-end doesn’t send owner).
    data = request.get_json() or {}
    owner_username, _owner_disp = _pin_identity()
    # If a PIN is logged in, force-owner to that user; otherwise keep whatever came (CSR/admin tools).
    owner_to_use = owner_username or data.get('owner', '')

    result = create_request_page.submitCreateRequest(
        requestTitle=data.get('title', ''),
        requestDescription=data.get('description', ''),
        requestCategory=data.get('category', ''),
        requestDate=data.get('date', ''),
        requestLocation=data.get('location', ''),
        owner=owner_to_use,
        time=data.get('time', ''),
        request_id=data.get('id')
    )
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 400
    if isinstance(result, dict):
        # normalize the created field if caller provided it
        if 'created' in data:
            result['created'] = data.get('created')
        # also persist owner if BCE didn’t set it
        if owner_to_use and not result.get('owner'):
            result['owner'] = owner_to_use
            reqs = load_requests()
            for r in reqs:
                if str(r.get('id')) == str(result.get('id')):
                    r['owner'] = owner_to_use
                    break
            save_requests(reqs)
        return jsonify({'success': True, 'request': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

@app.route('/api/requests/<request_id>', methods=['GET'])
def get_request_detail(request_id):
    # optional auto-increment: /api/requests/<id>?inc=1
    if (request.args.get('inc') or '').strip() == '1':
        _increment_view_count(request_id)

    result = view_request_page.getRequestDetail(request_id)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    if isinstance(result, dict):
        # return persisted viewCount (after optional increment above)
        reqs = load_requests()
        vc = 0
        for r in reqs:
            if _canon_req_id(r.get('id')) == _canon_req_id(request_id):
                vc = int(r.get('viewCount', 0) or 0)
                break
        result['viewCount'] = vc

        sc = shortlist_count_page.showShortlistCount(request_id)
        if isinstance(sc, int):
            result['shortlistCount'] = sc
        return jsonify({'success': True, 'request': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

# in Max_app.py (or app.py), CSR detail route
@app.get("/api/csr/requests/<request_id>")
def csr_get_request_detail(request_id):
    # ✅ increment if requested
    if (request.args.get("inc") or "").strip() == "1":
        _increment_view_count(request_id)

    result = csr_view_request_page.getRequestDetail(request_id)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404

    if isinstance(result, dict):
        # return persisted viewCount
        reqs = load_requests()
        vc = 0
        for r in reqs:
            if _canon_req_id(r.get('id')) == _canon_req_id(request_id):
                vc = int(r.get('viewCount', 0) or 0)
                break
        result['viewCount'] = vc
        sc = shortlist_count_page.showShortlistCount(request_id)
        if isinstance(sc, int):
            result['shortlistCount'] = sc
        return jsonify({'success': True, 'request': result})

    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500


# ===== NEW: PIN-only endpoints used by your PIN HTML =====

def _owns(rec, me: str) -> bool:
    if not me:
        return False
    owner = (rec.get('owner') or '').strip()
    # accept exact username; if you also store display names, match either
    return owner.lower() == me.lower()

@app.route('/api/pin/requests', methods=['GET'])
def pin_list_my_requests():
    """List only the logged-in PIN user's own requests."""
    uname, _ = _pin_identity()
    if not uname:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    rows = []
    for r in load_requests():
        if _owns(r, uname):
            rows.append({
                'id': r.get('id'),
                'title': r.get('title'),
                'category': r.get('category'),
                'date': r.get('date'),
                'created': r.get('created', r.get('date')),
                'status': r.get('status', 'Pending'),
                'owner': r.get('owner'),
                'description': r.get('description', ''),
                'location': r.get('location', ''),
            })
    return jsonify({'success': True, 'requests': rows, 'count': len(rows)})

@app.route('/api/pin/requests/<request_id>', methods=['GET'])
def pin_get_request_detail(request_id):
    """Return details only if the request belongs to the logged-in PIN user."""
    uname, _ = _pin_identity()
    if not uname:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    reqs = load_requests()
    rec = next((r for r in reqs if str(r.get('id')) == str(request_id) or _canon_req_id(r.get('id')) == _canon_req_id(request_id)), None)
    if not rec or not _owns(rec, uname):
        return jsonify({'success': False, 'message': 'Not found'}), 404

    # include persisted counts
    rec_copy = dict(rec)
    rec_copy['viewCount'] = int(rec.get('viewCount', 0) or 0)
    sc = shortlist_count_page.showShortlistCount(request_id)
    if isinstance(sc, int):
        rec_copy['shortlistCount'] = sc
    return jsonify({'success': True, 'request': rec_copy})

@app.route('/api/pin/requests/search', methods=['POST', 'GET'])
def pin_search_my_requests():
    """Search only within the logged-in PIN user's requests."""
    uname, _ = _pin_identity()
    if not uname:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    # Reuse your existing search, then filter by owner
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = {
            'id': request.args.get('id'),
            'title': request.args.get('title'),
            'category': request.args.get('category'),
            'date': request.args.get('date'),
            'status': request.args.get('status'),
            'keyword': request.args.get('keyword') or request.args.get('q')
        }
        data = {k: v for k, v in data.items() if v is not None}

    result = search_request_page.submitSearch(data)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 400

    rows = [r for r in (result or []) if _owns(r, uname)]
    return jsonify({'success': True, 'requests': rows, 'count': len(rows)})

# -----------------------------
# Update / Delete
# -----------------------------
@app.route('/api/requests/<request_id>', methods=['PUT'])
def update_request_api(request_id):
    data = request.get_json() or {}
    update_data = data.copy()
    update_data['requestID'] = request_id
    update_data['id'] = request_id
    result = update_request_page.updateInfo(update_data)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 400
    if isinstance(result, dict):
        return jsonify({'success': True, 'request': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

@app.route('/api/requests/<request_id>/status', methods=['PUT'])
def update_request_status(request_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    if not new_status:
        return jsonify({'success': False, 'message': 'Status is required.'}), 400
    update_data = {
        'requestID': request_id,
        'id': request_id,
        'status': new_status,
        'requestStatus': new_status
    }
    result = update_request_page.updateInfo(update_data)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    if isinstance(result, dict):
        return jsonify({'success': True, 'message': f'Request status updated to {new_status}', 'request': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

@app.route('/api/requests/<request_id>', methods=['DELETE'])
def delete_request(request_id):
    result = delete_request_page.deleteRequest(request_id)
    if isinstance(result, str) and result.startswith('Error:'):
        return jsonify({'success': False, 'message': result}), 404
    if isinstance(result, str) and 'deleted successfully' in result:
        return jsonify({'success': True, 'message': result})
    return jsonify({'success': False, 'message': 'Unknown error occurred.'}), 500

# -----------------------------
# Legacy WTForms demo page
# -----------------------------
@app.route('/create-request', methods=['GET', 'POST'])
def create_request_form():
    form = CreateRequestForm()
    if form.validate_on_submit():
        _in_memory_form_requests.append({
            'title': form.service_title.data,
            'category': form.category.data,
            'description': form.description.data,
            'location': form.location.data,
            'date_time': form.date_time.data
        })
        flash('successful submit', 'success')
        return redirect(url_for('create_request_form'))
    return render_template('create-request.html', form=form)

# -----------------------------
# Boot
# -----------------------------
if __name__ == '__main__':
    # Ensure files exist; NO default users are created automatically.
    init_users_file()
    init_requests_file()
    _ensure_shortlists_file()   # per-CSR shortlist store
    app.run(debug=True)
