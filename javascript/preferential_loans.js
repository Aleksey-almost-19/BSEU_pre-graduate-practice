const tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        const API_URL = 'http://localhost:8000';

        document.addEventListener('DOMContentLoaded', async () => {
            await loadPreferentialLoans();  // ← ИЗМЕНЕНО
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

        async function loadPreferentialLoans() {  // ← ИЗМЕНЕНО
            const container = document.getElementById('loans-container');
            
            try {
                const response = await fetch(`${API_URL}/api/preferential-loans`);  // ← ИЗМЕНЕНО
                
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
                const response = await fetch(`${API_URL}/api/preferential-loans/${loanId}`);  // ← ИЗМЕНЕНО
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
                    
                    <button class="tg-button" onclick="applyForLoan(${loan.id})">
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

        function closeModal() {
            document.getElementById('loanModal').style.display = 'none';
        }

        function applyForLoan(loanId) {
            tg.showPopup({
                title: 'Оформление заявки',
                message: 'Хотите оставить заявку на этот кредит? Менеджер свяжется с вами.',
                buttons: [
                    { type: 'default', text: 'Да, оставить заявку' },
                    { type: 'cancel', text: 'Отмена' }
                ]
            }, function(buttonId) {
                if (buttonId === 'Да, оставить заявку') {
                    tg.showAlert('Спасибо! Менеджер свяжется с вами в ближайшее время.');
                }
            });
        }

        window.onclick = function(event) {
            const modal = document.getElementById('loanModal');
            if (event.target === modal) closeModal();
        }