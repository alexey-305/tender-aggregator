import { FileText, MapPin, Clock, Download, ExternalLink, MessageCircle } from "lucide-react";

export default function TenderCard({ tender }) {
  if (!tender) {
    return (
      <div className="h-full flex items-center justify-center bg-[var(--bg-primary)]">
        <div className="text-center text-[var(--text-secondary)]">
          <FileText size={48} className="mx-auto mb-4 opacity-30" />
          <p className="text-lg text-white">Выберите закупку</p>
          <p className="text-sm mt-1">из списка слева</p>
        </div>
      </div>
    );
  }

  const deadline = tender.submission_deadline ? new Date(tender.submission_deadline) : null;
  const daysLeft = deadline ? Math.ceil((deadline - new Date()) / (1000 * 60 * 60 * 24)) : null;
  const price = tender.initial_price ? Number(tender.initial_price).toLocaleString("ru-RU") : "—";
  const customerName = tender.customer?.name || "—";
  const customerInn = tender.customer?.inn || "";

  let deadlineColor = "";
  if (daysLeft !== null) {
    if (daysLeft <= 3) deadlineColor = "text-[var(--danger)]";
    else if (daysLeft <= 7) deadlineColor = "text-[var(--warning)]";
  }

  const methodLabels = {
    electronic_auction: "Электронный аукцион",
    open_tender: "Открытый конкурс",
    request_for_quotations: "Запрос котировок",
    request_for_proposals: "Запрос предложений",
    single_supplier: "Единственный поставщик",
    two_stage_tender: "Двухэтапный конкурс",
    open_tender_limited: "Конкурс с огр. участием",
    commercial_other: "Коммерческая закупка",
  };

  return (
    <div className="h-full bg-[var(--bg-primary)] overflow-y-auto">
      <div className="p-6">
        {/* Заголовок */}
        <h2 className="text-lg font-bold text-white leading-snug mb-1">{tender.title}</h2>
        <div className="flex items-center gap-2 mb-4">
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/20 text-blue-400">{tender.law}</span>
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[var(--bg-tertiary)] text-[var(--text-secondary)]">
            {methodLabels[tender.procurement_method] || tender.procurement_method}
          </span>
          {daysLeft !== null && (
            <span className={"text-[10px] font-medium " + (daysLeft <= 3 ? "text-[var(--danger)]" : daysLeft <= 7 ? "text-[var(--warning)]" : "text-green-400")}>
              Осталось {daysLeft} дн.
            </span>
          )}
        </div>

        {/* Цена и обеспечения */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div>
            <div className="text-xs text-[var(--text-secondary)] mb-1">Цена контракта</div>
            <div className="text-2xl font-bold text-white">{price} RUB</div>
          </div>
          <div>
            <div className="text-xs text-[var(--text-secondary)] mb-1">Обеспечение заявки</div>
            <div className="text-sm text-green-400">не требуется</div>
          </div>
          <div>
            <div className="text-xs text-[var(--text-secondary)] mb-1">Обеспечение контракта</div>
            <div className="text-sm text-[var(--text-secondary)]">указано в документации</div>
          </div>
        </div>

        {/* Заказчик и место */}
        <div className="mb-4">
          <table className="w-full text-sm">
            <tbody>
              <tr className="border-b border-[var(--border)]">
                <td className="py-2 text-[var(--text-secondary)] w-40">Заказчик</td>
                <td className="py-2 text-white">
                  {customerName}
                  {customerInn && <span className="text-[var(--text-secondary)] ml-2">ИНН {customerInn}</span>}
                </td>
              </tr>
              {tender.region && (
                <tr className="border-b border-[var(--border)]">
                  <td className="py-2 text-[var(--text-secondary)]">Место поставки</td>
                  <td className="py-2 text-white">{tender.region}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* ОКПД2 */}
        {tender.okpd2_codes && tender.okpd2_codes.length > 0 && (
          <div className="mb-6">
            <div className="text-sm font-semibold text-white mb-2">Информация об объекте закупки</div>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-[var(--text-secondary)] border-b border-[var(--border)]">
                  <th className="py-2 text-left font-medium">ОКПД2</th>
                  <th className="py-2 text-left font-medium">Количество</th>
                  <th className="py-2 text-right font-medium">Цена</th>
                </tr>
              </thead>
              <tbody>
                {tender.okpd2_codes.map((code, i) => (
                  <tr key={i} className="border-b border-[var(--border)]">
                    <td className="py-2 text-white">{code}</td>
                    <td className="py-2 text-[var(--text-secondary)]">1.0 усл ед</td>
                    <td className="py-2 text-white text-right">{price} RUB</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="text-right text-sm font-semibold text-white mt-2">Итого: {price} RUB</div>
          </div>
        )}

        {/* Таймлайн */}
        <div className="mb-6">
          <div className="text-sm font-semibold text-white mb-3">Порядок размещения заказа</div>
          <table className="w-full text-sm">
            <tbody>
              <tr className="border-b border-[var(--border)]">
                <td className="py-2 text-[var(--text-secondary)] w-56">Дата и время начала подачи заявок</td>
                <td className="py-2 text-white">{tender.published_at ? new Date(tender.published_at).toLocaleString("ru-RU") : "—"}</td>
              </tr>
              <tr className="border-b border-[var(--border)]">
                <td className="py-2 text-[var(--text-secondary)]">Дата и время окончания подачи</td>
                <td className={"py-2 font-semibold " + deadlineColor}>
                  {deadline ? deadline.toLocaleString("ru-RU") : "—"}
                  {daysLeft !== null && (
                    <span className="ml-2 text-xs">({daysLeft > 0 ? daysLeft + " дн." : daysLeft === 0 ? "Сегодня" : "Просрочено"})</span>
                  )}
                </td>
              </tr>
              <tr className="border-b border-[var(--border)]">
                <td className="py-2 text-[var(--text-secondary)]">Дата подведения итогов</td>
                <td className="py-2 text-white">{tender.summarizing_date ? new Date(tender.summarizing_date).toLocaleDateString("ru-RU") : "—"}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Документы */}
        <div className="mb-6">
          <div className="text-sm font-semibold text-white mb-3">Документы закупки</div>
          <div className="text-sm text-[var(--text-secondary)]">
            Документы не загружены
          </div>
          <button className="mt-2 flex items-center gap-2 text-sm text-[var(--accent)] hover:text-white transition-colors">
            <Download size={14} /> Скачать одним архивом
          </button>
        </div>

        {/* Нижняя панель */}
        <div className="flex items-center justify-between pt-4 border-t border-[var(--border)] text-xs text-[var(--text-secondary)]">
          <span>Извещение № {tender.external_id || "—"}</span>
          <a href={tender.source_url || "#"} target="_blank" className="flex items-center gap-1 text-[var(--accent)] hover:text-white transition-colors">
            <ExternalLink size={12} /> {tender.source || "источник"}
          </a>
        </div>

        {/* Кнопки действий */}
        <div className="flex items-center gap-3 mt-4">
          <button className="flex-1 py-2.5 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-hover)] transition-colors">
            Подготовить заявку
          </button>
          <button className="px-4 py-2.5 rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-sm hover:text-white transition-colors">
            <MessageCircle size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
