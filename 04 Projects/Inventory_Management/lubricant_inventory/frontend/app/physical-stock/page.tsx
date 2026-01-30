'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sidebar } from '@/components/sidebar';
import { apiPhysicalStock, apiItems } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus } from 'lucide-react';

export default function PhysicalStockPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    item_id: 0,
    physical_quantity: 0,
  });

  const { data: entries, isLoading } = useQuery({
    queryKey: ['physical-stock'],
    queryFn: apiPhysicalStock.getAll,
  });

  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  const createMutation = useMutation({
    mutationFn: apiPhysicalStock.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['physical-stock'] });
      setShowForm(false);
      resetForm();
    },
  });

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      item_id: 0,
      physical_quantity: 0,
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
            <h1 className="text-3xl font-bold text-gray-900">Physical Stock</h1>
            <Button onClick={() => setShowForm(!showForm)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Physical Count
            </Button>
          </div>

          {showForm && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Record Physical Count</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Count Date *</Label>
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                      required
                    />
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
                          {item.item_name} ({item.pack_size}L)
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="physical_quantity">Physical Quantity Counted *</Label>
                    <Input
                      id="physical_quantity"
                      type="number"
                      step="0.01"
                      value={formData.physical_quantity}
                      onChange={(e) => setFormData({ ...formData, physical_quantity: parseFloat(e.target.value) })}
                      required
                    />
                  </div>
                  <div className="col-span-2 flex gap-3">
                    <Button type="submit">Record Physical Count</Button>
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
              <CardTitle>Physical Count History ({entries?.length || 0})</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Item Name</TableHead>
                    <TableHead className="text-right">Physical Quantity</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entries?.map((entry) => (
                    <TableRow key={entry.entry_id}>
                      <TableCell>{entry.date}</TableCell>
                      <TableCell>{entry.item_name}</TableCell>
                      <TableCell className="text-right">{entry.physical_quantity}</TableCell>
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
