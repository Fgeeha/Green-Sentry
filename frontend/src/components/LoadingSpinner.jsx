import React from 'react'
import { Loader2, Brain, FlaskConical } from 'lucide-react'

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-gray-700">
      {/* Иконка загрузки */}
      <Loader2 className="w-10 h-10 text-green-600 animate-spin mb-4" />

      {/* Заголовок */}
      <h2 className="text-lg font-semibold mb-6">
        Анализируем изображение...
      </h2>

      {/* Шаги анализа */}
      <div className="space-y-3 text-sm text-gray-600">
        {/* 1. CV-модель */}
        <div className="flex items-center gap-2">
          <FlaskConical className="w-4 h-4 text-green-600" />
          <span className="font-medium">CV-модель</span>
          <span className="text-gray-400">→</span>
          <span>Обработка изображения</span>
          <span className="text-green-600 ml-2">✓</span>
        </div>

        {/* 2. Классификация */}
        <div className="flex items-center gap-2">
          <FlaskConical className="w-4 h-4 text-green-600" />
          <span className="font-medium">Классификация заболевания</span>
        </div>

        {/* 3. Reasoning */}
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-indigo-600" />
          <span className="font-medium">Reasoning-анализ</span>
          <span className="text-gray-400 ml-2 animate-pulse">⋯</span>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
