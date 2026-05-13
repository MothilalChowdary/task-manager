const API = 'http://127.0.0.1:8000/api';
let auth = JSON.parse(localStorage.getItem('auth')) || null;
let user = null;
let users = [];
let activeProject = null;

// UI Elements
const views = { auth: document.getElementById('view-auth'), dashboard: document.getElementById('view-dashboard') };
const sections = { projects: document.getElementById('section-projects'), tasks: document.getElementById('section-tasks') };
const forms = { login: document.getElementById('form-login'), register: document.getElementById('form-register'), project: document.getElementById('form-project'), task: document.getElementById('form-task') };
const modals = { project: document.getElementById('modal-project'), task: document.getElementById('modal-task'), password: document.getElementById('modal-password') };
const loader = document.getElementById('global-loader');
const toast = document.getElementById('toast');
const progressBar = document.getElementById('progress-bar');

// --- Utils ---
function showToast(msg, type = 'success') {
    toast.innerText = msg;
    toast.style.borderLeftColor = type === 'error' ? 'var(--danger)' : 'var(--primary)';
    toast.classList.add('active');
    setTimeout(() => toast.classList.remove('active'), 3000);
}

function toggleLoader(show) {
    if (show) {
        progressBar.style.width = '30%';
        // Only show full loader if taking too long
        setTimeout(() => { if (progressBar.style.width === '30%') loader.classList.remove('hidden'); }, 500);
    } else {
        progressBar.style.width = '100%';
        setTimeout(() => { 
            progressBar.style.width = '0%';
            loader.classList.add('hidden');
        }, 300);
    }
}

async function req(path, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (auth) options.headers['Authorization'] = `Bearer ${auth.access}`;
    if (body) options.body = JSON.stringify(body);

    let res = await fetch(`${API}${path}`, options);
    
    // Automatic Token Refresh Logic
    if (res.status === 401 && auth && auth.refresh) {
        try {
            const refreshRes = await fetch(`${API}/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: auth.refresh })
            });
            
            if (refreshRes.ok) {
                const newData = await refreshRes.json();
                auth.access = newData.access;
                localStorage.setItem('auth', JSON.stringify(auth));
                
                // Retry the original request with new token
                options.headers['Authorization'] = `Bearer ${auth.access}`;
                res = await fetch(`${API}${path}`, options);
            } else {
                logout();
                throw new Error('Session expired');
            }
        } catch (err) {
            logout();
            throw new Error('Session expired');
        }
    }

    if (res.status === 204) return null;
    
    const data = await res.json();
    if (!res.ok) {
        if (typeof data === 'object' && !data.detail) {
            const first = Object.entries(data)[0];
            throw new Error(`${first[0]}: ${first[1][0]}`);
        }
        throw new Error(data.detail || 'Request failed');
    }
    return data;
}

// --- Auth ---
forms.login.onsubmit = async (e) => {
    e.preventDefault();
    toggleLoader(true);
    try {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        auth = await req('/token/', 'POST', { username, password });
        localStorage.setItem('auth', JSON.stringify(auth));
        localStorage.setItem('username', username);
        init();
    } catch (err) { showToast(err.message, 'error'); }
    finally { toggleLoader(false); }
};

forms.register.onsubmit = async (e) => {
    e.preventDefault();
    toggleLoader(true);
    try {
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        await req('/users/', 'POST', { username, email, password });
        showToast('Account created! Please login.');
        toggleAuthMode(true);
    } catch (err) { showToast(err.message, 'error'); }
    finally { toggleLoader(false); }
};

function logout() {
    auth = null;
    localStorage.removeItem('auth');
    localStorage.removeItem('username');
    views.auth.classList.remove('hidden');
    views.dashboard.classList.add('hidden');
}

function toggleAuthMode(isLogin) {
    forms.login.classList.toggle('hidden', !isLogin);
    forms.register.classList.toggle('hidden', isLogin);
    document.getElementById('auth-title').innerText = isLogin ? 'Sign In' : 'Create Account';
    document.getElementById('btn-toggle-auth').innerText = isLogin ? "Don't have an account? Register" : "Have an account? Login";
}

document.getElementById('btn-toggle-auth').onclick = (e) => {
    e.preventDefault();
    toggleAuthMode(forms.login.classList.contains('hidden'));
};

document.getElementById('btn-logout').onclick = logout;

// --- Projects ---
async function loadProjects() {
    // Show skeletons
    document.getElementById('project-list').innerHTML = Array(3).fill(0).map(() => `
        <div class="card skeleton" style="height: 180px;"></div>
    `).join('');
    
    toggleLoader(true);
    try {
        const projects = await req('/projects/');
        const isAdmin = user && user.role === 'admin';
        document.getElementById('btn-new-project').classList.toggle('hidden', !isAdmin);
        
        document.getElementById('project-list').innerHTML = projects.map((p, i) => `
            <div class="card animate-in" onclick="viewProject(${p.id})" style="animation-delay: ${i * 0.1}s">
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                    <span class="badge badge-active">${p.status}</span>
                    <span style="font-size:0.8rem; color:var(--text-muted)">${p.deadline}</span>
                </div>
                <h3>${p.title}</h3>
                <p style="color:var(--text-muted); font-size:0.9rem; margin:0.5rem 0;">${p.description}</p>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
                    <span style="font-size:0.8rem;">👥 ${p.members.length} Members</span>
                    ${isAdmin ? `<button class="btn btn-danger" onclick="deleteProject(${p.id}, event)" style="padding:0.4rem;">Delete</button>` : ''}
                </div>
            </div>
        `).join('');
    } catch (err) { showToast(err.message, 'error'); }
    finally { toggleLoader(false); }
}

async function viewProject(id) {
    toggleLoader(true);
    try {
        activeProject = await req(`/projects/${id}/`);
        sections.projects.classList.add('hidden');
        sections.tasks.classList.remove('hidden');
        document.getElementById('current-project-name').innerText = activeProject.title;
        
        // Strictly check for admin role
        const isAdmin = user && user.role === 'admin';
        const editBtn = document.getElementById('btn-edit-project');
        const newTaskBtn = document.getElementById('btn-new-task');
        
        if (isAdmin) {
            editBtn.classList.remove('hidden');
            newTaskBtn.classList.remove('hidden');
        } else {
            editBtn.classList.add('hidden');
            newTaskBtn.classList.add('hidden');
        }
        
        loadTasks();
    } catch (err) { showToast(err.message, 'error'); }
    finally { toggleLoader(false); }
}

async function deleteProject(id, e) {
    e.stopPropagation();
    if (!confirm('Delete project?')) return;
    try {
        await req(`/projects/${id}/`, 'DELETE');
        showToast('Project deleted');
        loadProjects();
    } catch (err) { showToast(err.message, 'error'); }
}

forms.project.onsubmit = async (e) => {
    e.preventDefault();
    const id = document.getElementById('project-id-field').value;
    const selectedMembers = Array.from(document.querySelectorAll('.member-item.selected')).map(el => parseInt(el.dataset.id));
    
    const body = {
        title: document.getElementById('project-title').value,
        description: document.getElementById('project-desc').value,
        deadline: document.getElementById('project-deadline').value,
        members: selectedMembers,
        status: 'active'
    };

    try {
        if (id) await req(`/projects/${id}/`, 'PUT', body);
        else await req('/projects/', 'POST', body);
        
        showToast(id ? 'Project updated' : 'Project created');
        modals.project.classList.remove('active');
        id ? viewProject(id) : loadProjects();
    } catch (err) { showToast(err.message, 'error'); }
};

// --- Tasks ---
async function loadTasks() {
    // Show skeletons
    document.getElementById('task-list').innerHTML = Array(3).fill(0).map(() => `
        <div class="card skeleton" style="height: 200px;"></div>
    `).join('');

    try {
        const tasks = await req(`/tasks/?project=${activeProject.id}`);
        const isAdmin = user && user.role === 'admin';
        
        document.getElementById('task-list').innerHTML = tasks.map((t, i) => `
            <div class="card animate-in" style="animation-delay: ${i * 0.1}s; border-left: 4px solid ${t.priority === 'high' ? 'var(--danger)' : t.priority === 'medium' ? 'var(--warning)' : 'var(--success)'};">
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                    <span class="badge badge-pending">${t.status.replace('_',' ')}</span>
                    <span style="font-size:0.8rem;">Priority: ${t.priority}</span>
                </div>
                <h3>${t.title}</h3>
                <p style="color:var(--text-muted); font-size:0.9rem;">${t.description}</p>
                <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
                    <select onchange="updateTaskStatus(${t.id}, this.value)" style="width:auto; padding:0.3rem;">
                        <option value="pending" ${t.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="in_progress" ${t.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${t.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                    ${isAdmin ? `
                        <div style="display:flex; gap:0.5rem;">
                            <button onclick="editTask(${JSON.stringify(t).replace(/"/g, '&quot;')})" class="btn btn-outline" style="padding:0.4rem;">Edit</button>
                            <button onclick="deleteTask(${t.id})" class="btn btn-danger" style="padding:0.4rem;">Delete</button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    } catch (err) { showToast(err.message, 'error'); }
}

async function updateTaskStatus(id, status) {
    try {
        await req(`/tasks/${id}/`, 'PATCH', { status });
        showToast('Status updated');
        loadTasks();
    } catch (err) { showToast(err.message, 'error'); }
}

async function deleteTask(id) {
    if (!confirm('Delete task?')) return;
    try {
        await req(`/tasks/${id}/`, 'DELETE');
        showToast('Task deleted');
        loadTasks();
    } catch (err) { showToast(err.message, 'error'); }
}

forms.task.onsubmit = async (e) => {
    e.preventDefault();
    const id = document.getElementById('task-id-field').value;
    const body = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-desc').value,
        priority: document.getElementById('task-priority').value,
        deadline: document.getElementById('task-deadline').value,
        assigned_to: parseInt(document.getElementById('task-assignee').value),
        project: activeProject.id,
        status: document.getElementById('task-status').value
    };

    try {
        if (id) await req(`/tasks/${id}/`, 'PUT', body);
        else await req('/tasks/', 'POST', body);
        
        showToast('Task saved');
        modals.task.classList.remove('active');
        loadTasks();
    } catch (err) { showToast(err.message, 'error'); }
};

// --- Modal Helpers ---
document.getElementById('btn-new-project').onclick = () => {
    forms.project.reset();
    document.getElementById('project-id-field').value = '';
    document.getElementById('modal-project-title').innerText = 'Create Project';
    renderMemberSelection();
    modals.project.classList.add('active');
};

document.getElementById('btn-edit-project').onclick = () => {
    document.getElementById('project-id-field').value = activeProject.id;
    document.getElementById('project-title').value = activeProject.title;
    document.getElementById('project-desc').value = activeProject.description;
    document.getElementById('project-deadline').value = activeProject.deadline;
    document.getElementById('modal-project-title').innerText = 'Edit Project';
    renderMemberSelection(activeProject.members);
    modals.project.classList.add('active');
};

document.getElementById('btn-new-task').onclick = () => {
    forms.task.reset();
    document.getElementById('task-id-field').value = '';
    document.getElementById('modal-task-title').innerText = 'Add Task';
    document.getElementById('task-status-group').classList.add('hidden');
    renderAssigneeSelect();
    modals.task.classList.add('active');
};

window.editTask = (task) => {
    document.getElementById('task-id-field').value = task.id;
    document.getElementById('task-title').value = task.title;
    document.getElementById('task-desc').value = task.description;
    document.getElementById('task-priority').value = task.priority;
    document.getElementById('task-deadline').value = task.deadline;
    document.getElementById('task-status').value = task.status;
    document.getElementById('task-status-group').classList.remove('hidden');
    document.getElementById('modal-task-title').innerText = 'Edit Task';
    renderAssigneeSelect(task.assigned_to);
    modals.task.classList.add('active');
};

function renderMemberSelection(selectedIds = []) {
    document.getElementById('member-select-list').innerHTML = users.map(u => `
        <div class="member-item ${selectedIds.includes(u.id) ? 'selected' : ''}" 
             onclick="this.classList.toggle('selected')" 
             data-id="${u.id}">
            <span>${u.username} <small style="color:var(--text-muted)">(${u.role})</small></span>
        </div>
    `).join('');
}

function renderAssigneeSelect(selectedId = null) {
    const projectMembers = users.filter(u => activeProject.members.includes(u.id));
    document.getElementById('task-assignee').innerHTML = projectMembers.map(u => `
        <option value="${u.id}" ${selectedId === u.id ? 'selected' : ''}>${u.username}</option>
    `).join('');
}

document.querySelectorAll('.btn-close-modal').forEach(btn => {
    btn.onclick = () => { 
        modals.project.classList.remove('active'); 
        modals.task.classList.remove('active'); 
        modals.password.classList.remove('active');
    };
});

document.getElementById('btn-back-projects').onclick = () => {
    sections.projects.classList.remove('hidden');
    sections.tasks.classList.add('hidden');
    loadProjects();
};

// --- Change Password ---
document.getElementById('btn-change-password-trigger').onclick = () => {
    document.getElementById('form-change-password').reset();
    modals.password.classList.add('active');
};

document.getElementById('form-change-password').onsubmit = async (e) => {
    e.preventDefault();
    toggleLoader(true);
    try {
        const body = {
            old_password: document.getElementById('change-old-password').value,
            new_password: document.getElementById('change-new-password').value,
            confirm_password: document.getElementById('change-confirm-password').value
        };
        await req('/users/change-password/', 'POST', body);
        showToast('Password updated successfully');
        modals.password.classList.remove('active');
    } catch (err) { showToast(err.message, 'error'); }
    finally { toggleLoader(false); }
};

// --- Init ---
async function init() {
    if (!auth) return;
    toggleLoader(true);
    try {
        users = await req('/users/');
        user = users.find(u => u.username === localStorage.getItem('username'));
        document.getElementById('display-user').innerText = `${user.username} (${user.role})`;
        views.auth.classList.add('hidden');
        views.dashboard.classList.remove('hidden');
        
        // Ensure we always start at the projects list
        sections.projects.classList.remove('hidden');
        sections.tasks.classList.add('hidden');
        
        loadProjects();
    } catch (err) { showToast(err.message, 'error'); logout(); }
    finally { toggleLoader(false); }
}

init();
