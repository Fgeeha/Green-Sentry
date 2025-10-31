import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const diagnosePlant = async (imageFile, context) => {
  const formData = new FormData();
  formData.append('image', imageFile);

  if (context.region) formData.append('region', context.region);
  if (context.climate) formData.append('climate', context.climate);
  if (context.plant_age) formData.append('plant_age', context.plant_age);
  if (context.additional_context) formData.append('additional_context', context.additional_context);
  formData.append('use_reasoning', context.use_reasoning);

  try {
    const response = await api.post('/diagnosis/', formData);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail ||
      'Не удалось выполнить диагностику. Попробуйте позже.'
    );
  }
};

export const getDiseases = async () => {
  try {
    const response = await api.get('/diagnosis/diseases');
    return response.data;
  } catch (error) {
    throw new Error('Не удалось загрузить список заболеваний');
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health/');
    return response.data;
  } catch (error) {
    throw new Error('API недоступен');
  }
};