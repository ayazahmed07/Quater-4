import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cashierApi, adminApi } from '../../api';
import { Product, Customer, TransactionMode, PaymentType, FuelType } from '../../types';

export const NewTransaction: React.FC = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [mode, setMode] = useState<TransactionMode>(TransactionMode.LITER_BASED);
  const [paymentType, setPaymentType] = useState<PaymentType>(PaymentType.CASH);
  const [formData, setFormData] = useState({
    product_id: 0,
    customer_id: 0,
    quantity: 0,
    amount: 0,
    meter_reading: 0,
    cash_amount: 0,
    credit_amount: 0,
  });
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [productsData, customersData] = await Promise.all([
        adminApi.getProducts(),
        adminApi.getCustomers(),
      ]);
      setProducts(productsData || []);
      setCustomers(customersData || []);
    } catch (error: any) {
      console.error('Failed to load data:', error);
      alert('Failed to load data. Please try again.');
      setProducts([]);
      setCustomers([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const product = products.find((p) => p.id === formData.product_id);
    setSelectedProduct(product || null);
  }, [formData.product_id, products]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      product_id: formData.product_id,
      customer_id: paymentType === PaymentType.CASH ? null : formData.customer_id || null,
      mode,
      payment_type: paymentType,
      quantity: mode === TransactionMode.LITER_BASED ? formData.quantity : null,
      amount: mode === TransactionMode.AMOUNT_BASED ? formData.amount : null,
      meter_reading: formData.meter_reading || null,
      cash_amount: paymentType === PaymentType.MIXED ? formData.cash_amount : undefined,
      credit_amount: paymentType === PaymentType.MIXED ? formData.credit_amount : undefined,
    };

    try {
      await cashierApi.createTransaction(payload);
      alert('Transaction created successfully!');
      navigate('/dashboard');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create transaction');
    }
  };

  const calculateAmount = () => {
    if (mode === TransactionMode.LITER_BASED && selectedProduct) {
      return formData.quantity * Number(selectedProduct.current_price);
    }
    return formData.amount;
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>New Fueling Transaction</h2>
      </div>

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="form-container">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Mode</label>
                <select value={mode} onChange={(e) => setMode(e.target.value as TransactionMode)}>
                  <option value={TransactionMode.LITER_BASED}>Liter Based</option>
                  <option value={TransactionMode.AMOUNT_BASED}>Amount Based</option>
                </select>
              </div>

              <div className="form-group">
                <label>Payment Type</label>
                <select value={paymentType} onChange={(e) => setPaymentType(e.target.value as PaymentType)}>
                  <option value={PaymentType.CASH}>Cash</option>
                  <option value={PaymentType.CREDIT}>Credit</option>
                  <option value={PaymentType.MIXED}>Mixed</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Product</label>
              <select
                value={formData.product_id}
                onChange={(e) => setFormData({ ...formData, product_id: parseInt(e.target.value) })}
                required
              >
                <option value="">Select Product</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} - Rs. {Number(p.current_price || 0).toFixed(2)}/L
                  </option>
                ))}
              </select>
            </div>

            {paymentType !== PaymentType.CASH && (
              <div className="form-group">
                <label>Customer</label>
                <select
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: parseInt(e.target.value) })}
                  required={paymentType === PaymentType.CREDIT}
                >
                  <option value="">Select Customer</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {mode === TransactionMode.LITER_BASED ? (
              <div className="form-group">
                <label>Quantity (Liters)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                  required
                />
                {selectedProduct && (
                  <small>Estimated: Rs. {Number(calculateAmount() || 0).toFixed(2)}</small>
                )}
              </div>
            ) : (
              <div className="form-group">
                <label>Amount (Rs.)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
                  required
                />
                {selectedProduct && Number(selectedProduct.current_price) > 0 && (
                  <small>Estimated: {(formData.amount / Number(selectedProduct.current_price)).toFixed(2)} L</small>
                )}
              </div>
            )}

            {paymentType === PaymentType.MIXED && (
              <div className="form-row">
                <div className="form-group">
                  <label>Cash Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.cash_amount}
                    onChange={(e) => setFormData({ ...formData, cash_amount: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Credit Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.credit_amount}
                    onChange={(e) => setFormData({ ...formData, credit_amount: parseFloat(e.target.value) })}
                    required
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label>Meter Reading (Optional)</label>
              <input
                type="number"
                step="0.01"
                value={formData.meter_reading}
                onChange={(e) => setFormData({ ...formData, meter_reading: parseFloat(e.target.value) || 0 })}
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">Create Transaction</button>
              <button type="button" onClick={() => navigate('/dashboard')} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
