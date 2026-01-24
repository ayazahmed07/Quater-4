import React, { useState, useEffect } from 'react';
import { customerApi } from '../../api';
import { Customer } from '../../types';

export const Profile: React.FC = () => {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await customerApi.getProfile();
      setCustomer(data);
      setFormData({
        name: data.name,
        phone: data.phone,
        address: data.address || '',
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await customerApi.updateProfile(formData);
      setIsEditing(false);
      loadProfile();
      alert('Profile updated successfully');
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>My Profile</h2>
        {!isEditing && (
          <button onClick={() => setIsEditing(true)} className="btn-primary">
            Edit Profile
          </button>
        )}
      </div>

      {customer && (
        <div className="profile-container">
          {isEditing ? (
            <div className="form-container">
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
                  <label>Phone</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Credit Limit</label>
                  <input type="text" value={`$${customer.credit_limit.toFixed(2)}`} disabled />
                </div>
                <div className="form-actions">
                  <button type="submit" className="btn-primary">Save</button>
                  <button type="button" onClick={() => setIsEditing(false)} className="btn-secondary">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="profile-view">
              <div className="profile-field">
                <label>Name:</label>
                <span>{customer.name}</span>
              </div>
              <div className="profile-field">
                <label>Phone:</label>
                <span>{customer.phone}</span>
              </div>
              <div className="profile-field">
                <label>Address:</label>
                <span>{customer.address || 'N/A'}</span>
              </div>
              <div className="profile-field">
                <label>Credit Limit:</label>
                <span>${customer.credit_limit.toFixed(2)}</span>
              </div>
              <div className="profile-field">
                <label>Status:</label>
                <span>{customer.status}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
