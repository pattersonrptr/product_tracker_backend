import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const getAds = async (search, page) => {
  return axios.get(`${API_URL}/api/ads`, {
    params: { search, skip: (page - 1) * 10, limit: 10 }
  });
};
