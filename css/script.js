/* Regras centralizadas: altere valores somente após validação de negócio. */
const CONFIG = { diasPorMes:30 };
const $ = (id) => document.getElementById(id);
const money = new Intl.NumberFormat('pt-BR', {style:'currency', currency:'BRL'});
const formatMoney = (value) => money.format(value || 0);
const HISTORY_KEY = 'simulap-history-v1';

// Aceita 1234,56, 1.234,56 e 1234.56.
function numberFrom(value) {
  const text = String(value || '').replace(/R\$\s?|\s/g, '');
  return Number(text.includes(',') ? text.replace(/\./g, '').replace(',', '.') : text);
}
function message(element, text = '') { element.textContent = text; element.classList.toggle('is-visible', Boolean(text)); }
function results(element, title, rows) {
  element.innerHTML = `<h3>${title}</h3>${rows.map(([label, value, important]) => `<div class="result-row ${important ? 'is-emphasis':''}"><span>${label}</span><strong>${value}</strong></div>`).join('')}`;
  element.hidden = false;
}
function getHistory() { try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch { return []; } }
function renderHistory() {
  const history = getHistory(), list = $('historyList');
  list.innerHTML = history.length ? history.map((item) => `<article class="history-item"><strong>${item.title}</strong><span>${item.summary}</span><small>${item.date}</small></article>`).join('') : '<p class="empty-history">Ainda não há simulações salvas.</p>';
  $('clearHistoryButton').hidden = !history.length;
}
// Guarda somente um resumo e limita o histórico a cinco registros no aparelho do usuário.
function saveHistory(title, summary) {
  const history = getHistory();
  history.unshift({ title, summary, date:new Date().toLocaleString('pt-BR') });
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 5)));
}
// inputmode pede teclado numérico em celulares; a formatação acontece ao sair do campo.
document.querySelectorAll('[data-currency]').forEach((input) => input.addEventListener('blur', () => {
  const value = numberFrom(input.value); input.value = value > 0 ? value.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}) : '';
}));

// Mantém o rótulo da tarifa coerente com a forma de locação escolhida.
function updateRentalLabel() {
  const daily = $('modoAluguel').value === 'diario';
  $('aluguelLabel').textContent = daily ? 'Valor da diária de locação' : 'Valor mensal da locação';
  $('valorAluguel').placeholder = daily ? 'Ex.: 120,00' : 'Ex.: 1.900,00';
}
$('modoAluguel').addEventListener('change', updateRentalLabel);

$('vehicleForm').addEventListener('submit', (event) => {
  event.preventDefault();
  const error = $('vehicleMessage'), output = $('vehicleResults');
  const value = numberFrom($('valorVeiculo').value), downPayment = numberFrom($('valorEntrada').value), installments = Number($('parcelas').value), ratePercent = numberFrom($('taxaFinanciamento').value), ownership = numberFrom($('custoPropriedade').value), rentalValue = numberFrom($('valorAluguel').value), rentalMode = $('modoAluguel').value;
  if (!(value > 0) || !Number.isInteger(installments) || installments < 1 || ratePercent < 0 || rentalValue <= 0 || ownership < 0) { output.hidden=true; return message(error,'Preencha preço, prazo, juros e valor da locação com valores válidos.'); }
  if (downPayment < 0 || downPayment > value) { output.hidden=true; return message(error,'A entrada deve ficar entre R$ 0,00 e o valor do veículo.'); }
  const financed = value-downPayment, rate = ratePercent / 100;
  const installment = !financed ? 0 : rate === 0 ? financed / installments : financed * rate * (1+rate)**installments / ((1+rate)**installments-1);
  const purchaseTotal = downPayment + installment * installments + ownership * installments;
  const rentalTotal = rentalMode === 'mensal' ? rentalValue * installments : rentalValue * installments * CONFIG.diasPorMes;
  const purchaseLabel = purchaseTotal <= rentalTotal ? 'Compra é a alternativa de menor custo' : 'Locação é a alternativa de menor custo';
  const vehicleName = $('nomeVeiculo').value.trim() || 'Veículo analisado';
  message(error); results(output,vehicleName, [['Valor financiado',formatMoney(financed)],['Parcela do financiamento',formatMoney(installment)],['Custos de propriedade no período',formatMoney(ownership * installments)],['Total estimado da compra',formatMoney(purchaseTotal),true],[rentalMode === 'mensal' ? 'Total estimado da locação mensal' : 'Total estimado da locação diária',formatMoney(rentalTotal),true],[purchaseLabel,formatMoney(Math.abs(purchaseTotal-rentalTotal)),true]]);
  saveHistory('Compra x locação', `${vehicleName} · economia estimada: ${formatMoney(Math.abs(purchaseTotal-rentalTotal))}`);
});
const picker=$('themePicker'); $('themeButton').addEventListener('click',() => { picker.hidden=!picker.hidden; });
function setTheme(theme) { document.documentElement.dataset.theme=theme; localStorage.setItem('simulap-theme',theme); picker.hidden=true; }
document.querySelectorAll('[data-theme-choice]').forEach((button) => button.addEventListener('click',() => setTheme(button.dataset.themeChoice)));
setTheme(localStorage.getItem('simulap-theme') || 'brand');

const historyDialog = $('historyDialog');
$('historyButton').addEventListener('click', () => { renderHistory(); historyDialog.showModal(); });
$('closeHistoryButton').addEventListener('click', () => historyDialog.close());
$('clearHistoryButton').addEventListener('click', () => { localStorage.removeItem(HISTORY_KEY); renderHistory(); });
