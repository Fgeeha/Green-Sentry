import React from 'react'
import {
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Pill,
  Shield,
  MapPin,
  Clock,
  Target,
} from 'lucide-react'

const DiagnosisResult = ({ result }) => {
  if (!result) return null

  const { cv_result, reasoning_analysis, pipeline_version } = result
  const reasoning = reasoning_analysis?.reasoning_analysis || {}

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
            {(cv_result?.confidence * 100).toFixed(1)}%
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

      {/* --- Reasoning Analysis --- */}
      {reasoning_analysis?.success && reasoning.parsed && (
        <section className="p-4 border rounded-lg bg-white shadow-sm space-y-4">
          {/* Disease Stage */}
          <div>
            <h4 className="font-semibold flex items-center gap-2 mb-1">
              <AlertTriangle className="text-yellow-600" size={16} />
              Стадия заболевания
            </h4>
            <span
              className={`inline-block px-3 py-1 rounded-md text-sm font-medium ${getStageColor(
                reasoning.disease_stage
              )}`}
            >
              {reasoning.disease_stage?.toUpperCase() || 'НЕ ОПРЕДЕЛЕНА'}
            </span>
            {reasoning.diagnosis_confirmation && (
              <p className="mt-1 text-gray-500">
                {reasoning.diagnosis_confirmation}
              </p>
            )}
          </div>

          {/* Causes */}
          {reasoning.causes?.length > 0 && (
            <div>
              <h4 className="font-semibold mb-1">Причины возникновения</h4>
              <ul className="list-disc list-inside">
                {reasoning.causes.map((cause, idx) => (
                  <li key={idx}>{cause}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Risk Factors */}
          {reasoning.risk_factors?.length > 0 && (
            <div>
              <h4 className="font-semibold mb-1">Факторы риска</h4>
              <ul className="list-disc list-inside">
                {reasoning.risk_factors.map((factor, idx) => (
                  <li key={idx}>{factor}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Spread Forecast */}
          {reasoning.spread_forecast && (
            <div>
              <h4 className="font-semibold mb-1">Прогноз распространения</h4>
              <p className="text-gray-700">
                {reasoning.spread_forecast.toUpperCase()}
              </p>
            </div>
          )}

          {/* Treatment Plan */}
          {reasoning.treatment_plan && (
            <div>
              <h4 className="font-semibold mb-1">План лечения</h4>
              <p className="text-gray-700 whitespace-pre-line">
                {reasoning.treatment_plan}
              </p>
            </div>
          )}

          {/* Prevention */}
          {reasoning.prevention && (
            <div>
              <h4 className="font-semibold mb-1">Профилактика</h4>
              <p className="text-gray-700 whitespace-pre-line">
                {reasoning.prevention}
              </p>
            </div>
          )}

          {/* Regional Recommendations */}
          {reasoning.regional_recommendations && (
            <div>
              <h4 className="font-semibold mb-1">
                Региональные рекомендации
              </h4>
              <p className="text-gray-700 whitespace-pre-line">
                {reasoning.regional_recommendations}
              </p>
            </div>
          )}

          {/* Timeline */}
          {reasoning.timeline && (
            <div>
              <h4 className="font-semibold flex items-center gap-1 mb-1">
                <Clock size={14} /> Временные рамки
              </h4>
              <p>{reasoning.timeline}</p>
            </div>
          )}

          {/* Success Probability */}
          {reasoning.success_probability && (
            <div>
              <h4 className="font-semibold flex items-center gap-1 mb-1">
                <Target size={14} /> Вероятность успеха
              </h4>
              <p
                className={`${getRiskColor(
                  reasoning.success_probability
                )} font-medium`}
              >
                {reasoning.success_probability}%
              </p>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

export default DiagnosisResult
