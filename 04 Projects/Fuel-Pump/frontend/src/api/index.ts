import api from './client';
import { User, LoginCredentials, Token, Customer, Product, FuelingTransaction, Invoice } from '../types';

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<Token> => {
    const response = await api.post<Token>('/auth/login', credentials);
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<Token> => {
    const response = await api.post<Token>('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Admin API
export const adminApi = {
  // Users
  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/admin/users');
    return response.data;
  },

  createUser: async (userData: { email: string; password: string; role: string }): Promise<User> => {
    const response = await api.post<User>('/admin/users', userData);
    return response.data;
  },

  updateUser: async (userId: number, userData: Partial<User>): Promise<User> => {
    const response = await api.put<User>(`/admin/users/${userId}`, userData);
    return response.data;
  },

  // Customers
  getCustomers: async (): Promise<Customer[]> => {
    const response = await api.get<Customer[]>('/admin/customers');
    return response.data;
  },

  createCustomer: async (customerData: any): Promise<Customer> => {
    const response = await api.post<Customer>('/admin/customers', customerData);
    return response.data;
  },

  updateCustomer: async (customerId: number, customerData: Partial<Customer>): Promise<Customer> => {
    const response = await api.put<Customer>(`/admin/customers/${customerId}`, customerData);
    return response.data;
  },

  // Products
  getProducts: async (): Promise<Product[]> => {
    const response = await api.get<Product[]>('/admin/products');
    // Convert numeric strings to numbers
    return response.data.map((p: any) => ({
      ...p,
      current_price: parseFloat(p.current_price),
      quantity: p.quantity ? parseFloat(p.quantity) : undefined,
      low_stock_threshold: p.low_stock_threshold ? parseFloat(p.low_stock_threshold) : undefined,
    }));
  },

  createProduct: async (productData: any): Promise<Product> => {
    const response = await api.post<Product>('/admin/products', productData);
    return response.data;
  },

  updateProductPrice: async (productId: number, priceData: { new_price: number }): Promise<Product> => {
    const response = await api.put<Product>(`/admin/products/${productId}/update-price`, priceData);
    return response.data;
  },

  getPriceHistory: async (productId: number): Promise<any[]> => {
    const response = await api.get<any[]>(`/admin/products/${productId}/price-history`);
    return response.data;
  },

  // Transactions
  getPendingTransactions: async (): Promise<FuelingTransaction[]> => {
    const response = await api.get<FuelingTransaction[]>('/admin/transactions/pending');
    return response.data;
  },

  confirmTransaction: async (transactionId: number): Promise<FuelingTransaction> => {
    const response = await api.put<FuelingTransaction>(`/admin/transactions/${transactionId}/confirm`);
    return response.data;
  },

  rejectTransaction: async (transactionId: number, reason: string): Promise<FuelingTransaction> => {
    const response = await api.put<FuelingTransaction>(`/admin/transactions/${transactionId}/reject`, { reason });
    return response.data;
  },

  // Invoices
  getInvoices: async (statusFilter?: string): Promise<Invoice[]> => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const response = await api.get<Invoice[]>('/admin/invoices', { params });
    return response.data;
  },

  generateInvoices: async (): Promise<any> => {
    const response = await api.post('/admin/invoices/generate');
    return response.data;
  },
};

// Cashier API
export const cashierApi = {
  createTransaction: async (transactionData: any): Promise<FuelingTransaction> => {
    const response = await api.post<FuelingTransaction>('/cashier/transactions', transactionData);
    return response.data;
  },

  getMyPendingTransactions: async (): Promise<FuelingTransaction[]> => {
    const response = await api.get<FuelingTransaction[]>('/cashier/transactions/my-pending');
    return response.data;
  },

  createMeterReading: async (readingData: any): Promise<any> => {
    const response = await api.post('/cashier/meter-readings', readingData);
    return response.data;
  },

  closeMeterReading: async (readingId: number, closingReading: number): Promise<any> => {
    const response = await api.put(`/cashier/meter-readings/${readingId}/close?closing_reading=${closingReading}`);
    return response.data;
  },

  getMeterReadings: async (limit: number = 50): Promise<any[]> => {
    const response = await api.get<any[]>('/cashier/meter-readings', { params: { limit } });
    return response.data;
  },
};

// Customer API
export const customerApi = {
  getProfile: async (): Promise<Customer> => {
    const response = await api.get<Customer>('/customer/profile');
    return response.data;
  },

  updateProfile: async (profileData: Partial<Customer>): Promise<Customer> => {
    const response = await api.put<Customer>('/customer/profile', profileData);
    return response.data;
  },

  getStatements: async (startDate?: string, endDate?: string): Promise<FuelingTransaction[]> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get<FuelingTransaction[]>('/customer/statements', { params });
    return response.data;
  },

  getInvoices: async (): Promise<Invoice[]> => {
    const response = await api.get<Invoice[]>('/customer/invoices');
    return response.data;
  },

  getInvoice: async (invoiceId: number): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/customer/invoices/${invoiceId}`);
    return response.data;
  },
};
