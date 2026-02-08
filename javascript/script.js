 // Инициализация Telegram Web App
        const tg = window.Telegram.WebApp;
        
        // Расширяем Web App на весь экран
        tg.expand();
        
        // Скрываем кнопку "Назад" на главной странице
        tg.MainButton.hide();
        
        // Устанавливаем цвета для темной темы
        tg.setHeaderColor('#2e7d32');
        tg.setBackgroundColor('#000000');
        
        // Функция перехода на страницу кредитов
        function goToCredits() {
            // Анимация кнопки
            const button = event.currentTarget;
            button.style.transform = 'scale(0.95)';
            button.style.opacity = '0.8';
            
            setTimeout(() => {
                button.style.transform = '';
                button.style.opacity = '';
            }, 150);
            
            // Открываем файл loans.html в этом же Web App
            window.location.href = 'loans.html';
        }
        
        // Инициализация при загрузке
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Аурумбанк - Главная страница загружена');
            
            // Проверяем загрузку логотипа
            const logo = document.querySelector('.logo-placeholder');
            
            const logoImg = new Image();
            logoImg.src = 'logo-removebg-preview.png';
            
            logoImg.onload = function() {
                console.log('Логотип logo-removebg-preview.png загружен успешно');
            };
            
            logoImg.onerror = function() {
                console.log('Ошибка загрузки логотипа logo-removebg-preview.png, используем fallback');
                logo.style.background = 'linear-gradient(135deg, #2e7d32, #4caf50)';
                logo.style.display = 'flex';
                logo.style.alignItems = 'center';
                logo.style.justifyContent = 'center';
                logo.innerHTML = 'A';
                logo.style.color = 'white';
                logo.style.fontSize = '28px';
                logo.style.fontWeight = 'bold';
            };
            
            // Добавляем задержку для анимаций
            const fadeElements = document.querySelectorAll('.fade-in');
            fadeElements.forEach((el, index) => {
                el.style.opacity = '0';
                el.style.animationDelay = `${index * 0.2}s`;
            });
            
            // Делаем логотип кликабельным
            logo.style.cursor = 'pointer';
            logo.addEventListener('click', function() {
                tg.showAlert('Аурумбанк - Ваш надежный финансовый партнер');
            });
        });