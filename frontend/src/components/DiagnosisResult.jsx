import React from 'react'
import { CheckCircle, AlertTriangle, Clock, Target, Brain, Leaf, Info } from 'lucide-react'

const hasContent = (value) => {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (typeof value === 'number' || typeof value === 'boolean') return true
  if (Array.isArray(value)) return value.some((item) => hasContent(item))
  if (typeof value === 'object')
    return Object.values(value).some((item) => hasContent(item))
  return false
}

const toDisplayLines = (value) => {
  if (!hasContent(value)) return []
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean')
    return [String(value)]
  if (Array.isArray(value))
    return value.flatMap((item) => toDisplayLines(item))
  if (typeof value === 'object') {
    return Object.entries(value).map(([key, val]) => {
      const nested = toDisplayLines(val)
      if (nested.length === 0) return key
      if (nested.length === 1) return `${key}: ${nested[0]}`
      return `${key}: ${nested.join(', ')}`
    })
  }
  return []
}

const formatMultiline = (value) => toDisplayLines(value).join('\n')

const renderList = (value) => {
  const items = toDisplayLines(value)
  if (items.length === 0) return null
  return (
    <ul className="list-disc list-inside text-gray-600">
      {items.map((item, idx) => (
        <li key={idx}>{item}</li>
      ))}
    </ul>
  )
}

const getStageColor = (stage) => {
  const colors = {
    начальная: 'text-green-600 bg-green-50',
    средняя: 'text-yellow-600 bg-yellow-50',
    критическая: 'text-red-600 bg-red-50',
  }
  return colors[stage?.toLowerCase()] || 'text-gray-600 bg-gray-50'
}

const getRiskColor = (risk) => {
  const colors = {
    низкий: 'text-green-600',
    средний: 'text-yellow-600',
    высокий: 'text-red-600',
  }
  return colors[risk?.toLowerCase()] || 'text-gray-600'
}

const DiagnosisResult = ({ result }) => {
  if (!result) return null

  const { cv_result, reasoning_analysis, pipeline_version, image_analysis } = result
  const isPlantImage = image_analysis?.is_plant !== false

  if (!isPlantImage) {
    return (
      <div className="space-y-6 text-sm text-gray-800">
        <section className="p-4 border rounded-lg bg-red-50 border-red-200 shadow-sm">
          <h3 className="font-semibold flex items-center gap-2 text-red-700 mb-2">
            <AlertTriangle size={18} /> На изображении не обнаружено растения
          </h3>
          <p className="text-gray-700">
            Пожалуйста, загрузите фотографию растения крупным планом с минимальным количеством посторонних объектов.
          </p>
        </section>

        {image_analysis && (
          <section className="p-4 border rounded-lg bg-white shadow-sm">
            <h4 className="font-semibold flex items-center gap-2 mb-2 text-green-700">
              <Leaf size={16} /> Анализ изображения
            </h4>
            <ul className="text-gray-700 space-y-1">
              <li>
                <span className="font-medium">Доля растительной области:</span>{' '}
                {(image_analysis.green_pixel_ratio * 100).toFixed(1)}%
              </li>
              <li>
                <span className="font-medium">Порог обнаружения:</span>{' '}
                {(image_analysis.green_threshold * 100).toFixed(1)}%
              </li>
              <li className="text-gray-500 text-xs">
                Средняя насыщенность: {(image_analysis.mean_saturation * 100).toFixed(1)}%, яркость: {' '}
                {(image_analysis.mean_value * 100).toFixed(1)}%
              </li>
            </ul>
            <p className="mt-3 text-gray-600 flex items-start gap-2">
              <Info size={14} className="mt-0.5" />
              Повторите попытку при лучшем освещении или измените ракурс, чтобы растение занимало основную часть кадра.
            </p>
          </section>
        )}
      </div>
    )
  }
  const reasoning = reasoning_analysis?.reasoning_analysis
  const structuredReasoning =
    reasoning && typeof reasoning === 'object' && !Array.isArray(reasoning) ? reasoning : null
  const structuredKeys = structuredReasoning
    ? Object.keys(structuredReasoning).filter((key) =>
        !['parsed', 'raw_response', 'error'].includes(key)
      )
    : []
  const reasoningDataAvailable =
    reasoning_analysis?.success &&
    structuredReasoning &&
    structuredReasoning.parsed !== false &&
    structuredKeys.length > 0

  const stageValue = structuredReasoning?.disease_stage
  const stageText =
    typeof stageValue === 'string'
      ? stageValue
      : stageValue?.stage || stageValue?.name || stageValue?.стадия || formatMultiline(stageValue)
  const stageColorKey =
    typeof stageValue === 'string'
      ? stageValue
      : stageValue?.stage || stageValue?.name || stageValue?.стадия || ''

  const confirmationText = formatMultiline(structuredReasoning?.diagnosis_confirmation)

  const spreadForecastValue = structuredReasoning?.spread_forecast
  const spreadForecastText =
    typeof spreadForecastValue === 'string'
      ? spreadForecastValue.toUpperCase()
      : formatMultiline(spreadForecastValue)

  const successProbabilityValue = structuredReasoning?.success_probability
  const successProbabilityColorSource =
    typeof successProbabilityValue === 'string'
      ? successProbabilityValue
      : successProbabilityValue?.level ||
        successProbabilityValue?.category ||
        successProbabilityValue?.уровень ||
        successProbabilityValue?.риск ||
        null
  const successProbabilityClass = successProbabilityColorSource
    ? getRiskColor(successProbabilityColorSource)
    : 'text-gray-600'
  const successProbabilityText =
    typeof successProbabilityValue === 'number'
      ? `${successProbabilityValue}%`
      : formatMultiline(successProbabilityValue)

  const formatConfidence = (confidence) => {
    if (typeof confidence === 'number') return `${(confidence * 100).toFixed(1)}%`
    if (typeof confidence === 'string') return confidence
    return '—'
  }

  return (
    <div className="space-y-6 text-sm text-gray-800">
      {/* --- CV Results --- */}
      <section className="p-4 border rounded-lg bg-gray-50 shadow-sm">
        <h3 className="text-lg font-semibold flex items-center gap-2 mb-2">
          <CheckCircle className="text-green-600" size={18} />
          Результаты CV-модели
        </h3>
        <p className="text-xs text-gray-500 mb-3">
          Версия пайплайна: {pipeline_version}
        </p>

        <div className="space-y-2">
          <p>
            <span className="font-medium">Диагноз:</span>{' '}
            {cv_result?.disease_name}
          </p>
          <p>
            <span className="font-medium">Уверенность:</span>{' '}
            {formatConfidence(cv_result?.confidence)}%
          </p>
        </div>

        {cv_result?.top3_predictions?.length > 1 && (
          <div className="mt-3">
            <p className="font-medium mb-1">Альтернативные диагнозы:</p>
            <ul className="list-disc list-inside text-gray-600">
              {cv_result.top3_predictions.slice(1).map((pred, idx) => (
                <li key={idx}>
                  {pred.name_ru} — {(pred.confidence * 100).toFixed(1)}%
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
        {image_analysis && (
        <section className="p-4 border rounded-lg bg-white shadow-sm">
          <h4 className="font-semibold flex items-center gap-2 mb-2 text-green-700">
            <Leaf size={16} /> Анализ изображения
          </h4>
          <p className="text-gray-700">
            Доля растительной области: {(image_analysis.green_pixel_ratio * 100).toFixed(1)}%
          </p>
        </section>
      )}

      {/* --- Reasoning Analysis --- */}
      {reasoningDataAvailable && (
        <section className="p-4 border rounded-lg bg-white shadow-sm space-y-4">
          {/* Disease Stage */}
          <div>
            <h4 className="font-semibold flex items-center gap-2 mb-1">
              <AlertTriangle className="text-yellow-600" size={16} />
              Стадия заболевания
            </h4>
            <span
              className={`inline-block px-3 py-1 rounded-md text-sm font-medium ${getStageColor(
                 stageColorKey
              )}`}
            >
              {stageText ? stageText.toString().toUpperCase() : 'НЕ ОПРЕДЕЛЕНА'}
            </span>
            {hasContent(structuredReasoning?.diagnosis_confirmation) && (
              <p className="mt-1 text-gray-500 whitespace-pre-line">{confirmationText}</p>
            )}
          </div>

          {/* Causes */}
          {hasContent(structuredReasoning?.causes) && (
            <div>
              <h4 className="font-semibold mb-1">Причины возникновения</h4>
              {renderList(structuredReasoning.causes)}
            </div>
          )}

          {/* Risk Factors */}
          {hasContent(structuredReasoning?.risk_factors) && (
            <div>
              <h4 className="font-semibold mb-1">Факторы риска</h4>
              {renderList(structuredReasoning.risk_factors)}
            </div>
          )}

          {/* Spread Forecast */}
          {hasContent(spreadForecastValue) && (
            <div>
              <h4 className="font-semibold mb-1">Прогноз распространения</h4>
              <p className="text-gray-700 whitespace-pre-line">{spreadForecastText}</p>
            </div>
          )}

          {/* Treatment Plan */}
          {hasContent(structuredReasoning?.treatment_plan) && (
            <div>
              <h4 className="font-semibold mb-1">План лечения</h4>
              <p className="text-gray-700 whitespace-pre-line">
                {formatMultiline(structuredReasoning.treatment_plan)}
              </p>
            </div>
          )}

          {/* Prevention */}
          {hasContent(structuredReasoning?.prevention) && (
            <div>
              <h4 className="font-semibold mb-1">Профилактика</h4>
              <p className="text-gray-700 whitespace-pre-line">
                {formatMultiline(structuredReasoning.prevention)}
              </p>
            </div>
          )}

          {/* Regional Recommendations */}
          {hasContent(structuredReasoning?.regional_recommendations) && (
            <div>
              <h4 className="font-semibold mb-1">
                Региональные рекомендации
              </h4>
              <p className="text-gray-700 whitespace-pre-line">
                {formatMultiline(structuredReasoning.regional_recommendations)}
              </p>
            </div>
          )}

          {/* Timeline */}
          {hasContent(structuredReasoning?.timeline) && (
            <div>
              <h4 className="font-semibold flex items-center gap-1 mb-1">
                <Clock size={14} /> Временные рамки
              </h4>
              <p className="text-gray-700 whitespace-pre-line">
                {formatMultiline(structuredReasoning.timeline)}
              </p>
            </div>
          )}

          {/* Success Probability */}
          {hasContent(successProbabilityValue) && (
            <div>
              <h4 className="font-semibold flex items-center gap-1 mb-1">
                <Target size={14} /> Вероятность успеха
              </h4>
              <p className={`${successProbabilityClass} font-medium whitespace-pre-line`}>
                {successProbabilityText}
              </p>
            </div>
          )}
        </section>
      )}

      {reasoning_analysis?.success && !reasoningDataAvailable && (
        <section className="p-4 border rounded-lg bg-white shadow-sm space-y-2">
          <h4 className="font-semibold flex items-center gap-2 mb-1">
            <Brain size={16} className="text-green-600" />
            GigaChat-анализ
          </h4>
          <p className="text-gray-700 whitespace-pre-line">
            {hasContent(reasoning)
              ? formatMultiline(reasoning)
              : 'Reasoning-агент вернул результат, но не удалось распарсить структурированные данные.'}
          </p>
        </section>
      )}

      {reasoning_analysis && !reasoning_analysis.success && (
        <section className="p-4 border rounded-lg bg-white shadow-sm space-y-2">
          <h4 className="font-semibold flex items-center gap-2 mb-1 text-red-600">
            <AlertTriangle size={16} /> Ошибка Reasoning-анализа
          </h4>
          <p className="text-gray-700">
            {reasoning_analysis.error || 'Не удалось получить ответ от reasoning-агента.'}
          </p>
        </section>
      )}

      {!reasoning_analysis && (
        <section className="p-4 border rounded-lg bg-white shadow-sm">
          <p className="text-gray-600">
            Reasoning-анализ отключен для этого запроса. Включите переключатель «Reasoning-анализ» перед отправкой, чтобы получить расширенный ответ от GigaChat.
          </p>
        </section>
      )}
    </div>
  )
}

export default DiagnosisResult
