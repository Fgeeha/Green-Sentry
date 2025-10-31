import { useState } from 'react';
import { diagnosePlant } from '../services/api';

export const useDiagnosis = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const diagnose = async (image, context) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await diagnosePlant(image, context);
      setResult(response);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return {
    loading,
    error,
    result,
    diagnose,
    reset,
  };
};