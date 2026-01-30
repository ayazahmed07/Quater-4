'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sidebar } from '@/components/sidebar';
import { apiSales, apiItems, type User } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus } from 'lucide-react';

export default function SalesPage() {
  const queryClient = useQueryClient();
  const user = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('user') || '{}') : null;
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    cashier_name: user?.full_name || '',
    shift: 'Morning',
    item_id: 0,
    quantity: 0,
  });

  const { data: sales, isLoading } = useQuery({
    queryKey: ['sales'],
    queryFn: () => apiSales.getAll(),
  });

  const { data: summary } = useQuery({
    queryKey: ['sales-summary'],
    queryFn: apiSales.getSummary,
  });

  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  const createMutation = useMutation({
    mutationFn: apiSales.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales', 'dashboard-stats'] });
      setShowForm(false);
      resetForm();
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Error creating sale');
    },
  });

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      cashier_name: user?.full_name || '',
      shift: 'Morning',
      item_id: 0,
      quantity: 0,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  if (isLoading) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Sales</h1>
            <Button onClick={() => setShowForm(!showForm)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Sale
            </Button>
          </div>

          {/* Cashier Performance Summary */}
          {summary && summary.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {summary.map((s) => (
                <Card key={s.cashier_name}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">{s.cashier_name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{s.total_quantity}</div>
                    <p className="text-xs text-gray-500">{s.total_transactions} transactions</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {showForm && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Record New Sale</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Date *</Label>
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="shift">Shift *</Label>
                    <select
                      id="shift"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={formData.shift}
                      onChange={(e) => setFormData({ ...formData, shift: e.target.value })}
                      required
                    >
                      <option value="Morning">Morning</option>
                      <option value="Evening">Evening</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="item_id">Item *</Label>
                    <select
                      id="item_id"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={formData.item_id}
                      onChange={(e) => setFormData({ ...formData, item_id: parseInt(e.target.value) })}
                      required
                    >
                      <option value="">Select Item</option>
                      {items?.map((item) => (
                        <option key={item.item_id} value={item.item_id}>
                          {item.item_name} ({item.pack_size}L) - Rs. {item.sale_price}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="quantity">Quantity *</Label>
                    <Input
                      id="quantity"
                      type="number"
                      step="0.01"
                      value={formData.quantity}
                      onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                      required
                    />
                  </div>
                  <div className="col-span-2 flex gap-3">
                    <Button type="submit">Record Sale</Button>
                    <Button type="button" variant="outline" onClick={() => { setShowForm(false); resetForm(); }}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Sales History ({sales?.length || 0})</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Cashier</TableHead>
                    <TableHead>Shift</TableHead>
                    <TableHead>Item Name</TableHead>
                    <TableHead className="text-right">Quantity</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sales?.map((sale) => (
                    <TableRow key={sale.sale_id}>
                      <TableCell>{sale.date}</TableCell>
                      <TableCell>{sale.cashier_name}</TableCell>
                      <TableCell>{sale.shift}</TableCell>
                      <TableCell>{sale.item_name}</TableCell>
                      <TableCell className="text-right">{sale.quantity}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
