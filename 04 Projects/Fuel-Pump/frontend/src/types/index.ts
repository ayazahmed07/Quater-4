// Enums
export enum Role {
  ADMIN = 'ADMIN',
  CASHIER = 'CASHIER',
  CUSTOMER = 'CUSTOMER',
}

export enum ProductType {
  FUEL = 'FUEL',
  LUBRICANT = 'LUBRICANT',
}

export enum FuelType {
  PETROL = 'PETROL',
  HSD = 'HSD',
  HOBC = 'HOBC',
}

export enum ProductUnit {
  LITER = 'LITER',
  UNIT = 'UNIT',
}

export enum TransactionMode {
  LITER_BASED = 'LITER_BASED',
  AMOUNT_BASED = 'AMOUNT_BASED',
}

export enum TransactionStatus {
  PENDING = 'PENDING',
  POSTED = 'POSTED',
  REJECTED = 'REJECTED',
}

export enum PaymentType {
  CASH = 'CASH',
  CREDIT = 'CREDIT',
  MIXED = 'MIXED',
}

export enum InvoiceStatus {
  GENERATED = 'GENERATED',
  PARTIAL_PAID = 'PARTIAL_PAID',
  PAID = 'PAID',
  OVERDUE = 'OVERDUE',
}

export enum CustomerStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED',
}

// Types
export interface User {
  id: number;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Customer {
  id: number;
  user_id: number;
  name: string;
  phone: string;
  address?: string;
  credit_limit: number;
  status: CustomerStatus;
  created_at: string;
  email?: string;
}

export interface Product {
  id: number;
  name: string;
  type: ProductType;
  fuel_type?: FuelType;
  current_price: number;
  unit: ProductUnit;
  created_at: string;
  quantity?: number;
  low_stock_threshold?: number;
}

export interface FuelingTransaction {
  id: number;
  customer_id?: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_amount: number;
  mode: TransactionMode;
  status: TransactionStatus;
  payment_type: PaymentType;
  cash_amount: number;
  credit_amount: number;
  transaction_date: string;
  meter_reading?: number;
  created_by: number;
  confirmed_by?: number;
  confirmed_at?: string;
  rejection_reason?: string;
  customer_name?: string;
  product_name?: string;
  creator_name?: string;
  confirmer_name?: string;
}

export interface Invoice {
  id: number;
  customer_id: number;
  invoice_number: string;
  billing_period_start: string;
  billing_period_end: string;
  total_amount: number;
  paid_amount: number;
  balance_due: number;
  status: InvoiceStatus;
  generated_at: string;
  due_date: string;
  customer_name?: string;
  items?: InvoiceItem[];
}

export interface InvoiceItem {
  id: number;
  transaction_id: number;
  quantity: number;
  unit_price: number;
  total_amount: number;
}

export interface MeterReading {
  id: number;
  pump_id: string;
  product_id: number;
  opening_reading: number;
  closing_reading?: number;
  date: string;
  recorded_by: number;
  product_name?: string;
  recorded_by_name?: string;
}
