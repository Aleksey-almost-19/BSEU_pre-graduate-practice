// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;

// Расширяем Web App на весь экран
tg.expand();

// Настраиваем кнопку "Назад"
tg.MainButton.setParams({
    text: 'НАЗАД',
    color: '#40a7e3'
});

// Показываем кнопку назад
tg.MainButton.show();
tg.MainButton.onClick(function() {
    // Возвращаемся на главную страницу
    window.location.href = 'index.html';
});

// Устанавливаем цвета для темной темы
tg.setHeaderColor('#2e7d32');
tg.setBackgroundColor('#000000');

// API URL для локальной разработки
const API_URL = 'http://localhost:8000';

// Функция выбора кредита
function selectCredit(type) {
    let title = '';
    let amount = '';
    
    switch(type) {
        case 'consumer':
            title = 'Потребительские кредиты';
            amount = 'до 50 000 BYN';
            break;
        case 'mortgage':
            title = 'Кредиты на недвижимость';
            amount = 'до 200 000 BYN';
            break;
        case 'preferential':
            title = 'Льготное кредитование';
            amount = 'от 4.5% годовых';
            break;
    }
    
    // Анимация выбора
    const card = event.currentTarget;
    card.style.transform = 'scale(0.97)';
    card.style.backgroundColor = '#2a2a2a';
    
    setTimeout(() => {
        card.style.transform = '';
        card.style.backgroundColor = '';
    }, 150);
    
    // Показываем уведомление
    tg.showAlert(`Вы выбрали: ${title}\n${amount}\n\nМенеджер свяжется с вами для уточнения деталей.`);
}

// Функция показа информации
function showInfo(type) {
    const item = event.currentTarget;
    const title = item.querySelector('strong').textContent;
    
    // Анимация
    item.style.transform = 'scale(0.98)';
    item.style.backgroundColor = '#2a2a2a';
    
    setTimeout(() => {
        item.style.transform = '';
        item.style.backgroundColor = '';
    }, 150);
    
    // Показываем всплывающее окно
    tg.showPopup({
        title: 'Информация',
        message: title + '\n\nБолее подробную информацию можно получить в отделении банка или на официальном сайте.',
        buttons: [{
            type: 'ok',
            text: 'Понятно'
        }]
    });
}

// Функция открытия формы связи (ИСПРАВЛЕННАЯ)
function openContactForm() {
    console.log('Кнопка нажата'); // Для отладки
    
    // Получаем данные пользователя из Telegram WebApp
    const user = tg.initDataUnsafe?.user;
    
    if (!user) {
        tg.showPopup({
            title: 'Ошибка',
            message: 'Не удалось получить данные пользователя. Запустите приложение через Telegram.',
            buttons: [{ type: 'ok', text: 'Понятно' }]
        });
        return;
    }
    
    tg.showPopup({
        title: '📞 Связь с менеджером',
        message: `Хотите, чтобы менеджер связался с вами?\n\nВаш ID: ${user.id}\nИмя: ${user.first_name || ''}`,
        buttons: [
            {
                type: 'default',
                text: '✅ Да, жду звонка'
            },
            {
                type: 'cancel',
                text: '❌ Отмена'
            }
        ]
    }, async function(buttonId) {
        if (buttonId === '✅ Да, жду звонка') {
            try {
                // Показываем сообщение о загрузке
                tg.showPopup({
                    title: '⏳ Отправка...',
                    message: 'Сохраняем вашу заявку',
                    buttons: []
                });
                
                // Отправляем запрос на сервер
                const response = await fetch(`${API_URL}/api/contact-request`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        telegram_id: user.id,
                        username: user.username || '',
                        first_name: user.first_name || '',
                        last_name: user.last_name || ''
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    tg.showAlert('✅ Спасибо! Менеджер свяжется с вами в ближайшее время.');
                } else {
                    tg.showAlert('❌ Ошибка: ' + (result.message || 'Неизвестная ошибка'));
                }
            } catch (error) {
                console.error('Ошибка:', error);
                tg.showAlert('❌ Ошибка соединения с сервером. Проверьте интернет.');
            }
        }
    });
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница кредитов загружена');
    
    // Проверяем загрузку логотипа
    const logos = document.querySelectorAll('.logo-placeholder');
    
    logos.forEach(logo => {
        const logoImg = new Image();
        logoImg.src = 'img/logo-removebg-preview.png';
        
        logoImg.onerror = function() {
            console.log('Ошибка загрузки логотипа, используем fallback');
            logo.style.background = 'linear-gradient(135deg, #2e7d32, #4caf50)';
            logo.style.display = 'flex';
            logo.style.alignItems = 'center';
            logo.style.justifyContent = 'center';
            logo.innerHTML = 'A';
            logo.style.color = 'white';
            logo.style.fontSize = '24px';
            logo.style.fontWeight = 'bold';
        };
        
        // Делаем логотип кликабельным
        logo.style.cursor = 'pointer';
        logo.addEventListener('click', function() {
            tg.showAlert('Аурумбанк - Ваш надежный финансовый партнер');
        });
    });
    
    // Добавляем обработчики клавиатуры для доступности
    const creditCards = document.querySelectorAll('.credit-card');
    creditCards.forEach(card => {
        card.setAttribute('tabindex', '0');
        card.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                this.click();
            }
        });
    });
    
    const infoItems = document.querySelectorAll('.info-item');
    infoItems.forEach(item => {
        item.setAttribute('tabindex', '0');
        item.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                this.click();
            }
        });
    });
    
    // Логика скрытия/показа логотипа при скролле на мобильных
    let lastScrollTop = 0;
    const mobileLogo = document.querySelector('.mobile-logo');
    const scrollThreshold = 50;
    
    if (mobileLogo) {
        window.addEventListener('scroll', function() {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > scrollThreshold) {
                if (scrollTop > lastScrollTop) {
                    mobileLogo.classList.add('hidden');
                } else if (scrollTop < lastScrollTop) {
                    mobileLogo.classList.remove('hidden');
                }
            } else {
                mobileLogo.classList.remove('hidden');
            }
            
            lastScrollTop = scrollTop;
        });
    }
});