// ========== РАБОТА С LOCALSTORAGE (хранилище браузера) ==========

function getUsers() {
    return JSON.parse(localStorage.getItem('dating_users')) || [];
}

function saveUsers(users) {
    localStorage.setItem('dating_users', JSON.stringify(users));
}

function getCurrentUser() {
    return JSON.parse(localStorage.getItem('dating_current_user'));
}

function saveCurrentUser(user) {
    localStorage.setItem('dating_current_user', JSON.stringify(user));
}

function getMatches() {
    return JSON.parse(localStorage.getItem('dating_matches')) || [];
}

function saveMatches(matches) {
    localStorage.setItem('dating_matches', JSON.stringify(matches));
}

function getMessages() {
    return JSON.parse(localStorage.getItem('dating_messages')) || {};
}

function saveMessages(messages) {
    localStorage.setItem('dating_messages', JSON.stringify(messages));
}

// ========== РЕГИСТРАЦИЯ ==========
function register() {
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const gender = document.getElementById('regGender').value;
    const age = parseInt(document.getElementById('regAge').value);
    const city = document.getElementById('regCity').value.trim();
    const bio = document.getElementById('regBio').value.trim();
    const photo = document.getElementById('regPhoto').value.trim() || 'https://i.pravatar.cc/400?img=' + Math.floor(Math.random() * 70);

    if (!username || !password || !age || !city) {
        alert('Заполните все обязательные поля!');
        return;
    }

    let users = getUsers();

    if (users.find(u => u.username === username)) {
        alert('Пользователь с таким именем уже существует!');
        return;
    }

    const newUser = {
        id: Date.now(),
        username,
        password,
        gender,
        age,
        city,
        bio: bio || 'Люблю знакомиться!',
        photo: photo
    };

    users.push(newUser);
    saveUsers(users);

    alert('Регистрация успешна! Теперь войдите.');
    showLogin();
}

// ========== ВХОД ==========
function login() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        alert('Введите имя и пароль!');
        return;
    }

    const users = getUsers();
    const user = users.find(u => u.username === username && u.password === password);

    if (!user) {
        alert('Неверное имя пользователя или пароль!');
        return;
    }

    saveCurrentUser(user);
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';
    document.getElementById('userNameDisplay').textContent = `${user.username}, ${user.age}`;

    // Инициализируем приложение
    if (typeof initApp === 'function') {
        initApp();
    }
}

// ========== ВЫХОД ==========
function logout() {
    localStorage.removeItem('dating_current_user');
    document.getElementById('appContainer').style.display = 'none';
    document.getElementById('authContainer').style.display = 'flex';
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';
}

// ========== ПЕРЕКЛЮЧЕНИЕ ФОРМ ==========
function showRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

function showLogin() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
}

// ========== ПРОВЕРКА АВТОРИЗАЦИИ ПРИ ЗАГРУЗКЕ ==========
window.onload = function() {
    const user = getCurrentUser();
    if (user) {
        document.getElementById('authContainer').style.display = 'none';
        document.getElementById('appContainer').style.display = 'block';
        document.getElementById('userNameDisplay').textContent = `${user.username}, ${user.age}`;
        if (typeof initApp === 'function') {
            initApp();
        }
    } else {
        document.getElementById('authContainer').style.display = 'flex';
        document.getElementById('appContainer').style.display = 'none';
    }
};