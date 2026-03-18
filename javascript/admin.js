const API_URL = 'https://bseu-pre-graduate-practice.onrender.com';
        
        // Функция переключения вкладок
        function switchTab(tabName, element) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            element.classList.add('active');
        }
        
        // Функция добавления поля для преимущества (для кредитов)
        function addAdvantage(type) {
            const container = document.getElementById(`${type}_advantages`);
            const newItem = document.createElement('div');
            newItem.className = 'advantage-item';
            newItem.innerHTML = `
                <input type="text" class="${type}_adv" placeholder="Преимущество ${container.children.length + 1}" required>
                <button type="button" class="remove-advantage" onclick="this.parentElement.remove()">×</button>
            `;
            container.appendChild(newItem);
        }
        
        // Функция добавления поля для преимущества вклада
        function addDepositAdvantage() {
            const container = document.getElementById('deposit_advantages');
            const newItem = document.createElement('div');
            newItem.className = 'advantage-item';
            newItem.innerHTML = `
                <input type="text" class="deposit_adv" placeholder="Преимущество ${container.children.length + 1}" required>
                <button type="button" class="remove-advantage" onclick="this.parentElement.remove()">×</button>
            `;
            container.appendChild(newItem);
        }
        
        function showMessage(type, text) {
            const successEl = document.getElementById('successMessage');
            const errorEl = document.getElementById('errorMessage');
            
            if (type === 'success') {
                successEl.textContent = text;
                successEl.style.display = 'block';
                errorEl.style.display = 'none';
                setTimeout(() => successEl.style.display = 'none', 3000);
            } else {
                errorEl.textContent = text;
                errorEl.style.display = 'block';
                successEl.style.display = 'none';
                setTimeout(() => errorEl.style.display = 'none', 3000);
            }
        }
        
        // Универсальная функция загрузки кредитов
        async function loadLoans(type, listId) {
            try {
                const res = await fetch(`${API_URL}/api/${type}-loans`);
                const loans = await res.json();
                
                if (loans.length === 0) {
                    document.getElementById(listId).innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Нет кредитов</p>';
                    return;
                }
                
                document.getElementById(listId).innerHTML = loans.map(loan => `
                    <div class="loan-card">
                        <h3>${loan.name}</h3>
                        <div class="loan-details">
                            <div>💰 ${loan.amount}</div>
                            <div>📊 ${loan.rate}</div>
                            <div>⏱️ ${loan.term}</div>
                        </div>
                        <div class="loan-advantages">
                            ${Array.isArray(loan.advantage) ? loan.advantage.map(adv => 
                                `<span class="advantage-badge">✨ ${adv}</span>`
                            ).join('') : `<span class="advantage-badge">✨ ${loan.advantage}</span>`}
                        </div>
                        <div class="loan-actions">
                            <button onclick="deleteLoan('${type}', ${loan.id})" class="btn btn-delete">🗑️ Удалить</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById(listId).innerHTML = '<p style="color: #ff6b6b; text-align: center;">Ошибка загрузки</p>';
                console.error(error);
            }
        }
        
        // Функция загрузки вкладов
        async function loadDeposits() {
            try {
                const res = await fetch(`${API_URL}/api/deposits`);
                const deposits = await res.json();
                
                if (deposits.length === 0) {
                    document.getElementById('depositsList').innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Нет вкладов</p>';
                    return;
                }
                
                document.getElementById('depositsList').innerHTML = deposits.map(deposit => `
                    <div class="loan-card">
                        <h3>💰 ${deposit.name}</h3>
                        <div class="deposit-details">
                            <div>📊 Ставка: <strong>${deposit.rate}</strong></div>
                            <div>⏱️ Срок: <strong>${deposit.term}</strong></div>
                            <div>📉 Мин: <strong>${deposit.min_amount}</strong></div>
                            <div>📈 Макс: <strong>${deposit.max_amount}</strong></div>
                        </div>
                        <div style="margin: 10px 0; color: #ccc;">
                            <span style="color: #4caf50;">Капитализация:</span> ${deposit.capitalization || 'Ежемесячно'}
                        </div>
                        <div class="loan-advantages">
                            ${Array.isArray(deposit.advantage) ? deposit.advantage.map(adv => 
                                `<span class="advantage-badge">✨ ${adv}</span>`
                            ).join('') : `<span class="advantage-badge">✨ ${deposit.advantage}</span>`}
                        </div>
                        <div class="loan-actions">
                            <button onclick="deleteDeposit(${deposit.id})" class="btn btn-delete">🗑️ Удалить</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('depositsList').innerHTML = '<p style="color: #ff6b6b; text-align: center;">Ошибка загрузки</p>';
                console.error(error);
            }
        }
        
        // Универсальная функция добавления кредита
        async function addLoan(type, event) {
            event.preventDefault();
            
            // Собираем преимущества
            const advantages = [];
            document.querySelectorAll(`.${type}_adv`).forEach(input => {
                if (input.value.trim()) advantages.push(input.value.trim());
            });
            
            const data = {
                name: document.getElementById(`${type}_name`).value,
                rate: document.getElementById(`${type}_rate`).value,
                term: document.getElementById(`${type}_term`).value,
                amount: document.getElementById(`${type}_amount`).value,
                advantage: advantages,
                details: document.getElementById(`${type}_details`).value
            };
            
            const res = await fetch(`${API_URL}/api/${type}-loans`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            showMessage(result.status, result.message);
            
            if (result.status === 'success') {
                // Очищаем форму
                document.getElementById(`${type}_name`).value = '';
                document.getElementById(`${type}_rate`).value = '';
                document.getElementById(`${type}_term`).value = '';
                document.getElementById(`${type}_amount`).value = '';
                document.getElementById(`${type}_details`).value = '';
                
                // Очищаем преимущества (оставляем одно пустое)
                const container = document.getElementById(`${type}_advantages`);
                container.innerHTML = `
                    <div class="advantage-item">
                        <input type="text" class="${type}_adv" placeholder="Преимущество 1" required>
                    </div>
                `;
                
                // Перезагружаем список
                loadLoans(type, `${type}List`);
            }
        }
        
        // Функция добавления вклада
        async function addDeposit(event) {
            event.preventDefault();
            
            // Собираем преимущества
            const advantages = [];
            document.querySelectorAll('.deposit_adv').forEach(input => {
                if (input.value.trim()) advantages.push(input.value.trim());
            });
            
            const data = {
                name: document.getElementById('deposit_name').value,
                rate: document.getElementById('deposit_rate').value,
                term: document.getElementById('deposit_term').value,
                min_amount: document.getElementById('deposit_min_amount').value,
                max_amount: document.getElementById('deposit_max_amount').value,
                capitalization: document.getElementById('deposit_capitalization').value,
                advantage: advantages,
                details: document.getElementById('deposit_details').value
            };
            
            const res = await fetch(`${API_URL}/api/deposits`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            showMessage(result.status, result.message);
            
            if (result.status === 'success') {
                // Очищаем форму
                document.getElementById('deposit_name').value = '';
                document.getElementById('deposit_rate').value = '';
                document.getElementById('deposit_term').value = '';
                document.getElementById('deposit_min_amount').value = '';
                document.getElementById('deposit_max_amount').value = '';
                document.getElementById('deposit_capitalization').value = 'Ежемесячно';
                document.getElementById('deposit_details').value = '';
                
                // Очищаем преимущества (оставляем одно пустое)
                const container = document.getElementById('deposit_advantages');
                container.innerHTML = `
                    <div class="advantage-item">
                        <input type="text" class="deposit_adv" placeholder="Преимущество 1" required>
                    </div>
                `;
                
                // Перезагружаем список
                loadDeposits();
            }
        }
        
        // Универсальная функция удаления кредита
        async function deleteLoan(type, id) {
            if (!confirm('Удалить кредит?')) return;
            const res = await fetch(`${API_URL}/api/${type}-loans/${id}`, {method: 'DELETE'});
            const result = await res.json();
            showMessage(result.status, result.message);
            loadLoans(type, `${type}List`);
        }
        
        // Функция удаления вклада
        async function deleteDeposit(id) {
            if (!confirm('Удалить вклад?')) return;
            const res = await fetch(`${API_URL}/api/deposits/${id}`, {method: 'DELETE'});
            const result = await res.json();
            showMessage(result.status, result.message);
            loadDeposits();
        }
        
        // Загрузка заявок
        async function loadContactRequests() {
            try {
                const res = await fetch(`${API_URL}/api/contact-requests`);
                const requests = await res.json();
                
                if (requests.length === 0) {
                    document.getElementById('contactsList').innerHTML = '<p style="color: #999; text-align: center;">Нет заявок</p>';
                    return;
                }
                
                document.getElementById('contactsList').innerHTML = requests.map(req => `
                    <div class="loan-card">
                        <h3>📞 Заявка #${req.id}</h3>
                        <div class="loan-details">
                            <div>🆔 Telegram ID: <strong>${req.telegram_id}</strong></div>
                            <div>👤 Имя: ${req.first_name || ''} ${req.last_name || ''}</div>
                            <div>📱 Username: ${req.username ? '@' + req.username : 'нет'}</div>
                            <div>📅 Дата: ${new Date(req.created_at).toLocaleString('ru-RU')}</div>
                            <div>📊 Статус: <span style="color: #4caf50;">${req.status}</span></div>
                        </div>
                        ${req.username ? `
                        <div style="margin-top: 10px;">
                            <a href="https://t.me/${req.username}" target="_blank" style="color: #4caf50; text-decoration: none;">
                                📨 Написать в Telegram
                            </a>
                        </div>
                        ` : ''}
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('contactsList').innerHTML = '<p style="color: #ff6b6b;">Ошибка загрузки</p>';
                console.error(error);
            }
        }
        
        // Назначаем обработчики форм
        document.getElementById('addConsumerForm').onsubmit = (e) => addLoan('consumer', e);
        document.getElementById('addMortgageForm').onsubmit = (e) => addLoan('mortgage', e);
        document.getElementById('addPreferentialForm').onsubmit = (e) => addLoan('preferential', e);
        document.getElementById('addDepositForm').onsubmit = (e) => addDeposit(e);
        
        // Инициализация
        loadLoans('consumer', 'consumerList');
        loadLoans('mortgage', 'mortgageList');
        loadLoans('preferential', 'preferentialList');
        loadDeposits();
        loadContactRequests();