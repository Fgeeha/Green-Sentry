import React from 'react'
import { MapPin, CloudRain, Calendar, MessageSquare, Brain } from 'lucide-react'

const ContextForm = ({ context, onChange }) => {
  const handleChange = (field, value) => {
    onChange({ ...context, [field]: value })
  }

  return (
    <div className="space-y-6">
      {/* Регион */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <MapPin size={16} /> Регион выращивания
        </label>
        <input
          type="text"
          value={context.region}
          onChange={(e) => handleChange('region', e.target.value)}
          placeholder="Москва"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>

      {/* Климат */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <CloudRain size={16} /> Климатическая зона
        </label>
        <select
          value={context.climate}
          onChange={(e) => handleChange('climate', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
        >
          <option value="умеренно-континентальный">Умеренно-континентальный</option>
          <option value="континентальный">Континентальный</option>
          <option value="субтропический">Субтропический</option>
          <option value="морской">Морской</option>
        </select>
      </div>

      {/* Возраст */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <Calendar size={16} /> Возраст растения (дни)
        </label>
        <input
          type="number"
          value={context.plant_age}
          onChange={(e) => handleChange('plant_age', e.target.value)}
          placeholder="45"
          min="0"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>

      {/* Доп. информация */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <MessageSquare size={16} /> Дополнительная информация
        </label>
        <textarea
          value={context.additional_context}
          onChange={(e) => handleChange('additional_context', e.target.value)}
          placeholder="Например: растение в теплице, недавно была жара..."
          rows="3"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
        />
      </div>

      {/* Reasoning */}
      <div className="flex items-center justify-between p-3 border rounded-lg bg-gray-50">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-green-600" />
          <span className="font-medium text-gray-700">Reasoning-анализ</span>
          <span className="text-sm text-gray-500">Глубокий анализ с GigaChat</span>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={context.use_reasoning}
            onChange={(e) => handleChange('use_reasoning', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-10 h-5 bg-gray-300 peer-focus:ring-2 peer-focus:ring-green-500 rounded-full peer-checked:bg-green-500 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-5" />
        </label>
      </div>
    </div>
  )
}

export default ContextForm
