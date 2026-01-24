import React, { useState, useEffect } from 'react';
import { adminApi } from '../../api';
import { Product, ProductType, FuelType } from '../../types';

export const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showPriceForm, setShowPriceForm] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: ProductType.FUEL,
    fuel_type: FuelType.PETROL,
    current_price: 0,
    unit: 'LITER',
  });
  const [priceData, setPriceData] = useState({ new_price: 0 });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setError(null);
      const data = await adminApi.getProducts();
      setProducts(data);
    } catch (error: any) {
      console.error('Failed to load products:', error);
      setError(error.response?.data?.detail || 'Failed to load products');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminApi.createProduct(formData);
      setShowAddForm(false);
      loadProducts();
    } catch (error) {
      console.error('Failed to create product:', error);
    }
  };

  const handleUpdatePrice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedProductId) {
      try {
        await adminApi.updateProductPrice(selectedProductId, priceData);
        setShowPriceForm(false);
        setSelectedProductId(null);
        setPriceData({ new_price: 0 });
        loadProducts();
      } catch (error) {
        console.error('Failed to update price:', error);
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Products Management</h2>
        <button onClick={() => setShowAddForm(true)} className="btn-primary">
          Add Product
        </button>
      </div>

      {showAddForm && (
        <div className="form-container">
          <h3>Create New Product</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as ProductType })}
              >
                <option value={ProductType.FUEL}>Fuel</option>
                <option value={ProductType.LUBRICANT}>Lubricant</option>
              </select>
            </div>
            {formData.type === ProductType.FUEL && (
              <div className="form-group">
                <label>Fuel Type</label>
                <select
                  value={formData.fuel_type}
                  onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value as FuelType })}
                >
                  <option value={FuelType.PETROL}>Petrol</option>
                  <option value={FuelType.HSD}>HSD</option>
                  <option value={FuelType.HOBC}>HOBC</option>
                </select>
              </div>
            )}
            <div className="form-group">
              <label>Price</label>
              <input
                type="number"
                step="0.01"
                value={formData.current_price}
                onChange={(e) => setFormData({ ...formData, current_price: parseFloat(e.target.value) })}
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

      {showPriceForm && (
        <div className="form-container">
          <h3>Update Price</h3>
          <form onSubmit={handleUpdatePrice}>
            <div className="form-group">
              <label>New Price</label>
              <input
                type="number"
                step="0.01"
                value={priceData.new_price}
                onChange={(e) => setPriceData({ new_price: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">Update</button>
              <button type="button" onClick={() => { setShowPriceForm(false); setSelectedProductId(null); }} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Fuel Type</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.id}</td>
                <td>{product.name}</td>
                <td>{product.type}</td>
                <td>{product.fuel_type || '-'}</td>
                <td>${product.current_price.toFixed(2)}</td>
                <td>{product.quantity ? `${product.quantity} L` : '-'}</td>
                <td>
                  <button
                    onClick={() => { setSelectedProductId(product.id); setShowPriceForm(true); setPriceData({ new_price: product.current_price }); }}
                    className="btn-small"
                  >
                    Update Price
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
