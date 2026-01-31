/**
 * API Client
 * ==========
 * Axios instance with base URL and JWT token injection.
 */

import axios, { AxiosError } from 'axios';

// Dynamic API URL construction for GitHub Codespaces compatibility
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;

    // For GitHub Codespaces or similar forwarding services
    // Replace port 3000 with 8000 in the URL
    if (hostname.includes('github.dev') || hostname.includes('githubpreview')) {
      // GitHub Codespaces uses URLs like https://xxx-3000.github.dev
      // We need to change -3000 to -8000
      const apiHostname = hostname.replace('-3000', '-8000');
      return `${protocol}//${apiHostname}`;
    }

    // For local development with explicit ports
    const port = window.location.port;
    if (port) {
      // If accessing on port 3000 or 3002, switch to 8000 (backend port)
      const apiPort = (port === '3000' || port === '3002') ? '8000' : port;
      return `${protocol}//${hostname}:${apiPort}`;
    }

    // Default fallback
    return `${protocol}//${hostname}:8000`;
  }

  // Fallback for server-side rendering
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Log API URL for debugging (only in development)
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('API Base URL:', API_BASE_URL);
}

// Request interceptor - add JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  user_id: number;
  username: string;
  full_name: string;
  role: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Item {
  item_id: number;
  item_name: string;
  grade: string | null;
  pack_size: number;
  purchase_price: number;
  sale_price: number;
  opening_stock: number;
}

export interface Purchase {
  purchase_id: number;
  date: string;
  invoice_no: string;
  item_id: number;
  quantity: number;
  rate: number;
  item_name: string;
}

export interface Sale {
  sale_id: number;
  date: string;
  cashier_name: string;
  shift: string;
  item_id: number;
  quantity: number;
  item_name: string;
}

export interface PhysicalStock {
  entry_id: number;
  date: string;
  item_id: number;
  physical_quantity: number;
  item_name: string;
}

export interface DashboardStats {
  total_items: number;
  total_purchases: number;
  total_sales: number;
  current_stock: number;
}

export interface StockComparisonItem {
  item_id: number;
  item_name: string;
  grade: string | null;
  pack_size: number;
  opening_stock: number;
  total_purchases: number;
  total_sales: number;
  system_stock: number;
  physical_stock: number | null;
  difference: number | null;
  status: string;
  rate: number;
  value_impact: number | null;
}

export interface StockComparisonSummary {
  total_items: number;
  items_with_shortage: number;
  items_with_excess: number;
  items_matching: number;
  items_no_count: number;
  total_shortage_value: number;
  total_excess_value: number;
}

// API Functions
export const apiAuth = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/api/auth/login', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },
};

export const apiDashboard = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/api/dashboard/stats');
    return response.data;
  },
};

export const apiItems = {
  getAll: async (): Promise<Item[]> => {
    const response = await api.get<Item[]>('/api/items');
    return response.data;
  },

  getById: async (id: number): Promise<Item> => {
    const response = await api.get<Item>(`/api/items/${id}`);
    return response.data;
  },

  create: async (data: Partial<Item>): Promise<Item> => {
    const response = await api.post<Item>('/api/items', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Item>): Promise<Item> => {
    const response = await api.put<Item>(`/api/items/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/items/${id}`);
  },

  import: async (file: File): Promise<{ message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ message: string }>('/api/items/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const apiPurchases = {
  getAll: async (startDate?: string, endDate?: string): Promise<Purchase[]> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get<Purchase[]>('/api/purchases', { params });
    return response.data;
  },

  create: async (data: Omit<Purchase, 'purchase_id' | 'item_name'>): Promise<Purchase> => {
    const response = await api.post<Purchase>('/api/purchases', data);
    return response.data;
  },

  import: async (file: File): Promise<{ message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ message: string }>('/api/purchases/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const apiSales = {
  getAll: async (startDate?: string, endDate?: string): Promise<Sale[]> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get<Sale[]>('/api/sales', { params });
    return response.data;
  },

  getByCashier: async (cashierName: string): Promise<Sale[]> => {
    const response = await api.get<Sale[]>(`/api/sales/cashier/${cashierName}`);
    return response.data;
  },

  getSummary: async (): Promise<Array<{ cashier_name: string; total_quantity: number; total_transactions: number }>> => {
    const response = await api.get<Array<{ cashier_name: string; total_quantity: number; total_transactions: number }>>('/api/sales/summary');
    return response.data;
  },

  create: async (data: Omit<Sale, 'sale_id' | 'item_name'>): Promise<Sale> => {
    const response = await api.post<Sale>('/api/sales', data);
    return response.data;
  },

  import: async (file: File): Promise<{ message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ message: string }>('/api/sales/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const apiPhysicalStock = {
  getAll: async (): Promise<PhysicalStock[]> => {
    const response = await api.get<PhysicalStock[]>('/api/physical-stock');
    return response.data;
  },

  create: async (data: Omit<PhysicalStock, 'entry_id' | 'item_name'>): Promise<PhysicalStock> => {
    const response = await api.post<PhysicalStock>('/api/physical-stock', data);
    return response.data;
  },
};

export const apiReports = {
  getStockComparison: async (): Promise<{ items: StockComparisonItem[]; summary: StockComparisonSummary }> => {
    const response = await api.get<{ items: StockComparisonItem[]; summary: StockComparisonSummary }>('/api/reports/stock-comparison');
    return response.data;
  },

  getCurrentStock: async (): Promise<Array<{
    item_name: string;
    grade: string | null;
    pack_size: number;
    system_stock: number;
    purchase_price: number;
    sale_price: number;
    stock_value: number;
  }>> => {
    const response = await api.get<Array<{
      item_name: string;
      grade: string | null;
      pack_size: number;
      system_stock: number;
      purchase_price: number;
      sale_price: number;
      stock_value: number;
    }>>('/api/reports/current-stock');
    return response.data;
  },

  getSales: async (startDate?: string, endDate?: string): Promise<Array<{
    date: string;
    cashier_name: string;
    shift: string;
    item_name: string;
    quantity: number;
  }>> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get<Array<{
      date: string;
      cashier_name: string;
      shift: string;
      item_name: string;
      quantity: number;
    }>>('/api/reports/sales', { params });
    return response.data;
  },

  getPurchases: async (startDate?: string, endDate?: string): Promise<Array<{
    date: string;
    invoice_no: string;
    item_name: string;
    quantity: number;
    rate: number;
    total_value: number;
  }>> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get<Array<{
      date: string;
      invoice_no: string;
      item_name: string;
      quantity: number;
      rate: number;
      total_value: number;
    }>>('/api/reports/purchases', { params });
    return response.data;
  },
};
