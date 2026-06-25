// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
let currentIndex = 0;
let availableUsers = [];
let currentChatUser = null;

// ========== ИНИЦИАЛИЗАЦИЯ ==========
function initApp() {
    loadFeed();
    loadMatches();
    loadChats();
}

// ========== ЗАГРУЗКА ЛЕНТЫ ==========
function loadFeed() {
    const currentUser = getCurrentUser();
    if (!currentUser) return;

    const allUsers = getUsers();
    
    // Фильтруем: только противоположный пол и не себя
    let filtered = allUsers.filter(user => {
        if (currentUser.gender === 'male') {
            return user.gender === 'female' && user.id !== currentUser.id;
        } else {
            return user.gender === 'male' && user.id !== currentUser.id;
        }
    });

    // Убираем тех, кого уже лайкнули
    const matches = getMatches();
    const likedIds = matches
        .filter(m => m.from === currentUser.id)
        .map(m => m.to);
    
    filtered = filtered.filter(user => !likedIds.includes(user.id));

    // Перемешиваем
    availableUsers = shuffleArray(filtered);
    currentIndex = 0;
    renderCard();
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// ========== ОТРИСОВКА КАРТОЧКИ ==========
function renderCard() {
    const container = document.getElementById('cardsContainer');

    if (availableUsers.length === 0 || currentIndex >= availableUsers.length) {
        container.innerHTML = `
            <div class="empty-state">
                <h2>🌟 Все анкеты просмотрены!</h2>
                <p>Загляните позже — здесь появятся новые люди.</p>
            </div>
        `;
        return;
    }

    const user = availableUsers[currentIndex];
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <div class="card-image" style="background-image: url('${user.photo}');"></div>
        <div class="card-info">
            <h2>${user.username}, <span>${user.age}</span></h2>
            <p>📍 ${user.city} • ${user.bio}</p>
        </div>
    `;

    container.innerHTML = '';
    container.appendChild(card);
}

// ========== ЛАЙК ==========
function handleLike() {
    if (availableUsers.length === 0 || currentIndex >= availableUsers.length) return;

    const likedUser = availableUsers[currentIndex];
    const currentUser = getCurrentUser();

    // Сохраняем лайк
    const matches = getMatches();
    matches.push({
        from: currentUser.id,
        to: likedUser.id,
        timestamp: Date.now()
    });
    saveMatches(matches);

    // Проверяем взаимность: лайкнул ли этот человек нас?
    const isMutual = matches.some(m => m.from === likedUser.id && m.to === currentUser.id);

    // Анимация
    const card = document.querySelector('.card');
    if (card) {
        card.classList.add('swipe-right');
        setTimeout(() => card.remove(), 500);
    }

    currentIndex++;

    if (isMutual) {
        showMatchModal(likedUser);
    }

    setTimeout(renderCard, 300);
}

// ========== ДИЗЛАЙК ==========
function handleDislike() {
    if (availableUsers.length === 0 || currentIndex >= availableUsers.length) return;

    const card = document.querySelector('.card');
    if (card) {
        card.classList.add('swipe-left');
        setTimeout(() => card.remove(), 500);
    }

    currentIndex++;
    setTimeout(renderCard, 300);
}

// ========== МОДАЛКА ВЗАИМНОСТИ ==========
function showMatchModal(user) {
    document.getElementById('matchMessage').textContent = 
        `Вы и ${user.username} понравились друг другу! 💞`;
    document.getElementById('matchModal').classList.add('show');
}

function closeMatchModal() {
    document.getElementById('matchModal').classList.remove('show');
    switchTab('matches');
}

// ========== ЗАГРУЗКА СОВПАДЕНИЙ ==========
function loadMatches() {
    const currentUser = getCurrentUser();
    if (!currentUser) return;

    const matches = getMatches();
    const allUsers = getUsers();

    // Находим взаимные симпатии
    const mutualIds = [];
    matches.forEach(m => {
        if (m.from === currentUser.id) {
            if (matches.some(m2 => m2.from === m.to && m2.to === currentUser.id)) {
                mutualIds.push(m.to);
            }
        }
    });

    const uniqueIds = [...new Set(mutualIds)];
    const mutualUsers = allUsers.filter(u => uniqueIds.includes(u.id));

    const container = document.getElementById('matchesList');
    
    if (mutualUsers.length === 0) {
        container.innerHTML = `
            <p style="text-align:center;color:#888;padding:40px;">
                У вас пока нет взаимных симпатий. <br>Продолжайте ставить лайки!
            </p>
        `;
        return;
    }

    container.innerHTML = mutualUsers.map(user => `
        <div class="match-item" onclick="openChat(${user.id})">
            <img src="${user.photo}" alt="${user.username}">
            <div class="info">
                <h4>${user.username}, ${user.age}</h4>
                <p>${user.city}</p>
            </div>
            <span style="font-size:24px;">💞</span>
        </div>
    `).join('');
}

// ========== ЧАТЫ ==========
function loadChats() {
    const currentUser = getCurrentUser();
    if (!currentUser) return;

    const matches = getMatches();
    const allUsers = getUsers();

    // Находим всех, с кем есть взаимность
    const mutualIds = [];
    matches.forEach(m => {
        if (m.from === currentUser.id) {
            if (matches.some(m2 => m2.from === m.to && m2.to === currentUser.id)) {
                mutualIds.push(m.to);
            }
        }
    });

    const uniqueIds = [...new Set(mutualIds)];
    const chatUsers = allUsers.filter(u => uniqueIds.includes(u.id));

    const container = document.getElementById('chatList');
    
    if (chatUsers.length === 0) {
        container.innerHTML = `
            <p style="text-align:center;color:#888;padding:40px;">
                Нет чатов. Начните с лайков!
            </p>
        `;
        return;
    }

    container.innerHTML = chatUsers.map(user => `
        <div class="chat-item" onclick="openChat(${user.id})">
            <img src="${user.photo}" alt="${user.username}">
            <div class="info">
                <h4>${user.username}</h4>
                <p>${user.city}</p>
            </div>
        </div>
    `).join('');
}

// ========== ОТКРЫТЬ ЧАТ ==========
function openChat(userId) {
    const allUsers = getUsers();
    const user = allUsers.find(u => u.id === userId);
    if (!user) return;

    currentChatUser = user;
    document.getElementById('chatWindow').style.display = 'flex';
    document.getElementById('chatHeader').textContent = `💬 ${user.username}`;
    loadMessages(userId);
}

// ========== ЗАГРУЗКА СООБЩЕНИЙ ==========
function loadMessages(userId) {
    const currentUser = getCurrentUser();
    const messages = getMessages();
    const chatId = getChatId(currentUser.id, userId);
    const chatMessages = messages[chatId] || [];

    const container = document.getElementById('chatMessages');
    container.innerHTML = chatMessages.map(msg => `
        <div class="message ${msg.from === currentUser.id ? 'self' : 'other'}">
            ${msg.text}
            <div style="font-size:11px;opacity:0.6;margin-top:4px;">
                ${new Date(msg.timestamp).toLocaleTimeString()}
            </div>
        </div>
    `).join('');

    container.scrollTop = container.scrollHeight;
}

function getChatId(user1, user2) {
    return [user1, user2].sort().join('_');
}

// ========== ОТПРАВИТЬ СООБЩЕНИЕ ==========
function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();
    if (!text || !currentChatUser) return;

    const currentUser = getCurrentUser();
    const messages = getMessages();
    const chatId = getChatId(currentUser.id, currentChatUser.id);

    if (!messages[chatId]) messages[chatId] = [];

    messages[chatId].push({
        from: currentUser.id,
        text: text,
        timestamp: Date.now()
    });

    saveMessages(messages);
    input.value = '';
    loadMessages(currentChatUser.id);
}

// ========== ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК ==========
function switchTab(tab) {
    // Скрываем все
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    // Показываем нужную
    if (tab === 'feed') {
        document.getElementById('feedTab').style.display = 'block';
        document.querySelector('[data-tab="feed"]').classList.add('active');
        loadFeed();
    } else if (tab === 'matches') {
        document.getElementById('matchesTab').style.display = 'block';
        document.querySelector('[data-tab="matches"]').classList.add('active');
        loadMatches();
    } else if (tab === 'messages') {
        document.getElementById('messagesTab').style.display = 'flex';
        document.querySelector('[data-tab="messages"]').classList.add('active');
        loadChats();
    }
}

// ========== ПРОФИЛЬ (редактирование) ==========
function showProfile() {
    const user = getCurrentUser();
    if (!user) return;

    document.getElementById('editCity').value = user.city || '';
    document.getElementById('editAge').value = user.age || '';
    document.getElementById('editBio').value = user.bio || '';
    document.getElementById('editPhoto').value = user.photo || '';
    document.getElementById('profileModal').classList.add('show');
}

function saveProfile() {
    const user = getCurrentUser();
    if (!user) return;

    const city = document.getElementById('editCity').value.trim();
    const age = parseInt(document.getElementById('editAge').value);
    const bio = document.getElementById('editBio').value.trim();
    const photo = document.getElementById('editPhoto').value.trim();

    if (!city || !age) {
        alert('Город и возраст обязательны!');
        return;
    }

    // Обновляем в localStorage
    const users = getUsers();
    const index = users.findIndex(u => u.id === user.id);
    if (index !== -1) {
        users[index].city = city;
        users[index].age = age;
        users[index].bio = bio || 'Люблю знакомиться!';
        if (photo) users[index].photo = photo;
        saveUsers(users);
        saveCurrentUser(users[index]);
        document.getElementById('userNameDisplay').textContent = `${users[index].username}, ${users[index].age}`;
    }

    closeProfileModal();
    loadFeed();
}

function closeProfileModal() {
    document.getElementById('profileModal').classList.remove('show');
}

// ========== ПОДПИСКА НА КНОПКИ ==========
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('likeBtn').addEventListener('click', handleLike);
    document.getElementById('dislikeBtn').addEventListener('click', handleDislike);
    
    // Отправка сообщения по Enter
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    // Закрытие модалок по клику на фон
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    });
});