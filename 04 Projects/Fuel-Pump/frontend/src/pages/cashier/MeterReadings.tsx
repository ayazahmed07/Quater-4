import React, { useState, useEffect } from 'react';
import { cashierApi, adminApi } from '../../api';
import { MeterReading, Product } from '../../types';

export const MeterReadings: React.FC = () => {
  const [readings, setReadings] = useState<MeterReading[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    product_id: 0,
    opening_reading: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [readingsData, productsData] = await Promise.all([
        cashierApi.getMeterReadings(),
        adminApi.getProducts(),
      ]);
      setReadings(readingsData);
      setProducts(productsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await cashierApi.createMeterReading(formData);
      setShowAddForm(false);
      setFormData({ product_id: 0, opening_reading: 0 });
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create meter reading');
    }
  };

  const handleClose = async (id: number, opening: number) => {
    const closing = prompt(`Enter closing reading (current: ${opening}):`);
    if (closing) {
      try {
        await cashierApi.closeMeterReading(id, parseFloat(closing));
        loadData();
      } catch (error: any) {
        alert(error.response?.data?.detail || 'Failed to close meter reading');
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Meter Readings</h2>
        <button onClick={() => setShowAddForm(true)} className="btn-primary">
          New Reading
        </button>
      </div>

      {showAddForm && (
        <div className="form-container">
          <h3>Create New Meter Reading</h3>
          <form onSubmit={handleSubmit}>
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
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Opening Reading</label>
              <input
                type="number"
                step="0.01"
                value={formData.opening_reading}
                onChange={(e) => setFormData({ ...formData, opening_reading: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">Create</button>
              <button type="button" onClick={() => setShowAddForm(false)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product</th>
              <th>Opening</th>
              <th>Closing</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {readings.map((reading) => (
              <tr key={reading.id}>
                <td>{reading.id}</td>
                <td>{reading.product_name}</td>
                <td>{reading.opening_reading.toFixed(2)}</td>
                <td>{reading.closing_reading ? reading.closing_reading.toFixed(2) : 'Open'}</td>
                <td>{new Date(reading.date).toLocaleString()}</td>
                <td>
                  {!reading.closing_reading && (
                    <button
                      onClick={() => handleClose(reading.id, reading.opening_reading)}
                      className="btn-small"
                    >
                      Close
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
