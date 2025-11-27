import axios from "axios";

// base da API vinda de variável de ambiente ou fallback
const API_BASE =
  import.meta.env.VITE_API_BASE ||
  "http://127.0.0.1:8000"; // fallback seguro no dev

const api = axios.create({
  baseURL: API_BASE,
});

export default api;
