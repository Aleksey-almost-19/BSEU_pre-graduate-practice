const tg = window.Telegram.WebApp;
tg.expand();
tg.ready();

// Автоматическое определение API URL
const API_URL = window.location.origin;
console.log('API URL:', API_URL); // для отладки

document.addEventListener('DOMContentLoaded', async () => {
    await loadPreferentialLoans();
    initMobileLogoScroll();
    initLogoClick();
});

function initMobileLogoScroll() {
    let lastScrollTop = 0;
    const scrollThreshold = 50;
    const mobileLogo = document.querySelector('.mobile-logo');
    
    if (!mobileLogo) return;
    
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

function initLogoClick() {
    const logos = document.querySelectorAll('.logo-placeholder');
    logos.forEach(logo => {
        logo.style.cursor = 'pointer';
        logo.addEventListener('click', function() {
            tg.showAlert('Аурумбанк - Ваш надежный финансовый партнер');
        });
    });
}

async function loadPreferentialLoans() {
    const container = document.getElementById('loans-container');
    
    try {
        const response = await fetch(`${API_URL}/api/preferential-loans`);
        
        if (!response.ok) throw new Error('Ошибка загрузки данных');
        
        const loans = await response.json();
        
        if (loans.length === 0) {
            container.innerHTML = '<div class="error-message">Кредиты временно недоступны</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="loans-grid">
                ${loans.map(loan => createLoanCard(loan)).join('')}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `
            <div class="error-message">
                ❌ Не удалось загрузить кредиты<br>
                <small>${error.message}</small>
            </div>
        `;
    }
}

function createLoanCard(loan) {
    return `
        <div class="loan-card">
            <div class="loan-header">
                <h3 class="loan-title">${loan.name}</h3>
                <span class="loan-badge">${loan.rate}</span>
            </div>
            
            <div class="loan-details">
                <div class="detail-item">
                    <span class="detail-label">Сумма</span>
                    <span class="detail-value">${loan.amount}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Срок</span>
                    <span class="detail-value">${loan.term}</span>
                </div>
            </div>
            
            <div class="loan-advantage">
                <p>✨ ${loan.advantage}</p>
            </div>
            
            <button class="loan-more" onclick="showLoanDetails(${loan.id})">
                Подробнее о кредите
            </button>
        </div>
    `;
}

async function showLoanDetails(loanId) {
    const modal = document.getElementById('loanModal');
    const modalContent = document.getElementById('modalContent');
    
    try {
        const response = await fetch(`${API_URL}/api/preferential-loans/${loanId}`);
        if (!response.ok) throw new Error('Кредит не найден');
        
        const loan = await response.json();
        
        modalContent.innerHTML = `
            <h2 style="color: #ffffff; margin-bottom: 20px;">${loan.name}</h2>
            
            <div style="background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>Процентная ставка</span>
                    <span style="font-size: 28px; font-weight: 700;">${loan.rate}</span>
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <h3 style="color: #ffffff; margin-bottom: 12px;">Условия кредита</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div style="background: #222222; padding: 16px; border-radius: 12px;">
                        <div style="font-size: 14px; color: #999999;">Максимальная сумма</div>
                        <div style="font-size: 20px; font-weight: 700; color: #4caf50;">${loan.amount}</div>
                    </div>
                    <div style="background: #222222; padding: 16px; border-radius: 12px;">
                        <div style="font-size: 14px; color: #999999;">Срок кредита</div>
                        <div style="font-size: 20px; font-weight: 700; color: #4caf50;">${loan.term}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <h3 style="color: #ffffff; margin-bottom: 12px;">Подробное описание</h3>
                <p style="color: #cccccc; line-height: 1.6; font-size: 16px;">${loan.details}</p>
            </div>
            
            <div style="background: #222222; padding: 16px; border-radius: 12px; margin-bottom: 24px;">
                <span style="color: #4caf50; font-weight: 600;">✓ Преимущество:</span>
                <p style="color: #cccccc; margin-top: 8px;">${loan.advantage}</p>
            </div>
            
            <button class="tg-button" onclick="showApplicationForm(${loan.id})">
                📝 Оформить заявку
            </button>
            
            <button class="modal-close" onclick="closeModal()">
                Закрыть
            </button>
        `;
        
        modal.style.display = 'flex';
    } catch (error) {
        tg.showAlert('Не удалось загрузить информацию о кредите');
    }
}

// Функция для отображения формы с ФИО и телефоном
function showApplicationForm(loanId) {
    // Получаем данные пользователя из Telegram
    const user = tg.initDataUnsafe?.user;
    
    // Закрываем предыдущее модальное окно
    closeModal();
    
    // Создаем HTML для формы заявки
    const formHtml = `
        <div style="padding: 20px;">
            <h3 style="color: #4caf50; margin-bottom: 20px; text-align: center; font-size: 22px;">Оформление заявки</h3>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; color: #ccc; font-size: 14px;">Ваше ФИО</label>
                <input type="text" id="fullname" placeholder="Иванов Иван Иванович" 
                    style="width: 100%; padding: 14px; border-radius: 10px; border: 1px solid #333; background: #222; color: white; font-size: 16px;">
            </div>
            
            <div style="margin-bottom: 25px;">
                <label style="display: block; margin-bottom: 8px; color: #ccc; font-size: 14px;">Номер телефона</label>
                <input type="tel" id="phone" placeholder="+375 (29) 123-45-67" 
                    style="width: 100%; padding: 14px; border-radius: 10px; border: 1px solid #333; background: #222; color: white; font-size: 16px;">
            </div>
            
            <div style="display: flex; gap: 12px;">
                <button onclick="submitApplication(${loanId})" 
                    style="flex: 2; background: #4caf50; color: white; border: none; padding: 16px; border-radius: 10px; font-weight: 600; font-size: 16px; cursor: pointer; transition: all 0.2s;">
                    ✅ Отправить заявку
                </button>
                <button onclick="closeFormModal()" 
                    style="flex: 1; background: #333; color: white; border: none; padding: 16px; border-radius: 10px; font-size: 16px; cursor: pointer; transition: all 0.2s;">
                    ❌ Отмена
                </button>
            </div>
        </div>
    `;
    
    // Создаем новое модальное окно для формы
    const formModal = document.createElement('div');
    formModal.id = 'formModal';
    formModal.style.cssText = `
        display: flex;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.9);
        z-index: 1001;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.2s ease;
    `;
    
    const formContent = document.createElement('div');
    formContent.style.cssText = `
        background: #1a1a1a;
        border-radius: 20px;
        padding: 24px;
        max-width: 400px;
        width: 90%;
        margin: 20px;
        border: 1px solid #333;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    `;
    formContent.innerHTML = formHtml;
    
    formModal.appendChild(formContent);
    document.body.appendChild(formModal);
}

// Функция отправки заявки
async function submitApplication(loanId) {
    const fullname = document.getElementById('fullname').value.trim();
    const phone = document.getElementById('phone').value.trim();
    
    // Валидация
    if (!fullname) {
        tg.showAlert('Пожалуйста, введите ваше ФИО');
        return;
    }
    
    if (!phone) {
        tg.showAlert('Пожалуйста, введите номер телефона');
        return;
    }
    
    if (phone.length < 5) {
        tg.showAlert('Пожалуйста, введите корректный номер телефона');
        return;
    }
    
    // Получаем данные пользователя из Telegram
    const user = tg.initDataUnsafe?.user;
    
    try {
        // Показываем индикатор загрузки
        tg.showPopup({
            title: '⏳ Отправка',
            message: 'Отправляем вашу заявку...',
            buttons: []
        });
        
        // Отправляем данные на сервер
        const response = await fetch(`${API_URL}/api/contact-request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: user?.id || 0,
                username: user?.username || '',
                first_name: user?.first_name || '',
                last_name: user?.last_name || '',
                fullname: fullname,
                phone: phone,
                loan_id: loanId
            })
        });
        
        const result = await response.json();
        
        // Закрываем форму
        closeFormModal();
        
        // Показываем результат
        if (result.status === 'success') {
            tg.showPopup({
                title: '✅ Заявка отправлена',
                message: 'Спасибо! Менеджер свяжется с вами в течение 10 минут.',
                buttons: [{
                    type: 'ok',
                    text: 'Хорошо'
                }]
            });
        } else {
            tg.showAlert('❌ Ошибка при отправке заявки. Попробуйте позже.');
        }
        
    } catch (error) {
        console.error('Ошибка:', error);
        closeFormModal();
        tg.showAlert('❌ Ошибка соединения с сервером');
    }
}

// Функция закрытия формы
function closeFormModal() {
    const formModal = document.getElementById('formModal');
    if (formModal) {
        formModal.remove();
    }
}

function closeModal() {
    document.getElementById('loanModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('loanModal');
    if (event.target === modal) closeModal();
    
    const formModal = document.getElementById('formModal');
    if (event.target === formModal) closeFormModal();
}