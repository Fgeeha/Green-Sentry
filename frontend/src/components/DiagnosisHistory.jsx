import React, { useState } from 'react'
import { History, Trash2, Leaf, X, Image as ImageIcon } from 'lucide-react'

const formatDateTime = (value) => {
  try {
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) {
      return 'Неизвестно'
    }
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (error) {
    return 'Неизвестно'
  }
}

const formatConfidence = (confidence) => {
  if (typeof confidence !== 'number') {
    return '—'
  }

  return `${(confidence * 100).toFixed(1)}%`
}

const truncateText = (text, length = 180) => {
  if (!text) {
    return null
  }

  if (text.length <= length) {
    return text
  }

  return `${text.slice(0, length)}…`
}

function DiagnosisHistory({ history, onClear }) {
  const [selectedEntry, setSelectedEntry] = useState(null)

  const handleOpenEntry = (entry) => {
    setSelectedEntry(entry)
  }

  const handleCloseModal = () => {
    setSelectedEntry(null)
  }

  return (
    <section className="relative p-4 border rounded-md bg-white shadow-sm">
      <header className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-gray-700">
          <History size={20} />
          <h3 className="text-lg font-semibold">История запросов</h3>
        </div>
        {history.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="flex items-center gap-1 text-sm text-red-500 hover:text-red-600 transition"
          >
            <Trash2 size={16} /> Очистить
          </button>
        )}
      </header>

      {history.length === 0 ? (
        <p className="text-sm text-gray-500">
          Здесь будут отображаться последние запросы диагностики.
        </p>
      ) : (
        <ul className="space-y-3">
          {history.map((entry) => (
            <li key={entry.id}>
              <button
                type="button"
                onClick={() => handleOpenEntry(entry)}
                className="w-full text-left border rounded-md p-3 transition hover:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                  <div className="flex items-center gap-2 font-medium text-gray-800">
                    <Leaf size={16} />
                    <span>{entry.disease || 'Растение не обнаружено'}</span>
                  </div>
                  <span className="text-gray-500">{formatDateTime(entry.timestamp)}</span>
                </div>

                {entry.report && (
                  <p className="mt-2 text-sm text-gray-600 whitespace-pre-line">
                    {truncateText(entry.report)}
                  </p>
                )}

                <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
                  <span>
                    Уверенность: <strong>{formatConfidence(entry.confidence)}</strong>
                  </span>
                  {entry.useReasoning !== undefined && (
                    <span>
                      Reasoning: <strong>{entry.useReasoning ? 'включен' : 'выключен'}</strong>
                    </span>
                  )}
                  {entry.region && (
                    <span>
                      Регион: <strong>{entry.region}</strong>
                    </span>
                  )}
                  {entry.pipelineVersion && (
                    <span>
                      Pipeline: <strong>{entry.pipelineVersion}</strong>
                    </span>
                  )}
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selectedEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6 shadow-2xl">
            <header className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-xl font-semibold text-gray-800">
                  {selectedEntry.disease || 'Растение не обнаружено'}
                </h4>
                <p className="mt-1 text-sm text-gray-500">{formatDateTime(selectedEntry.timestamp)}</p>
              </div>
              <button
                type="button"
                onClick={handleCloseModal}
                className="rounded-full p-1 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
                aria-label="Закрыть"
              >
                <X size={20} />
              </button>
            </header>

            {selectedEntry.report && (
              <section className="mt-4">
                <h5 className="text-sm font-semibold text-gray-700">Отчёт</h5>
                <p className="mt-2 whitespace-pre-line text-sm text-gray-600">
                  {selectedEntry.report}
                </p>
              </section>
            )}

            <section className="mt-6 grid gap-2 text-sm text-gray-600">
              <p>
                Уверенность: <strong>{formatConfidence(selectedEntry.confidence)}</strong>
              </p>
              {selectedEntry.useReasoning !== undefined && (
                <p>
                  Reasoning: <strong>{selectedEntry.useReasoning ? 'включен' : 'выключен'}</strong>
                </p>
              )}
              {selectedEntry.region && (
                <p>
                  Регион: <strong>{selectedEntry.region}</strong>
                </p>
              )}
              {selectedEntry.pipelineVersion && (
                <p>
                  Pipeline: <strong>{selectedEntry.pipelineVersion}</strong>
                </p>
              )}
            </section>

            {selectedEntry.imagePreview && (
              <section className="mt-6">
                <h5 className="text-sm font-semibold text-gray-700">Загруженное изображение</h5>
                <div className="mt-3 overflow-hidden rounded-md border border-gray-200 bg-gray-50">
                  <img
                    src={selectedEntry.imagePreview}
                    alt={selectedEntry.imageName || 'Загруженное изображение пользователя'}
                    className="max-h-[320px] w-full object-contain"
                  />
                </div>
                <div className="mt-2 flex items-center justify-center gap-2 text-xs text-gray-500">
                  <ImageIcon size={14} />
                  <span>{selectedEntry.imageName || 'Файл изображения'}</span>
                </div>
              </section>
            )}
          </div>
        </div>
      )}
    </section>
  )
}

export default DiagnosisHistory