'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sidebar } from '@/components/sidebar';
import { apiItems } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Pencil, Trash2, Upload } from 'lucide-react';

export default function ItemsPage() {
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formData, setFormData] = useState({
    item_name: '',
    grade: '',
    pack_size: 1.0,
    purchase_price: 0,
    sale_price: 0,
    opening_stock: 0,
  });

  const { data: items, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  const createMutation = useMutation({
    mutationFn: apiItems.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setShowAddForm(false);
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => apiItems.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setEditingItem(null);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: apiItems.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });

  const resetForm = () => {
    setFormData({
      item_name: '',
      grade: '',
      pack_size: 1.0,
      purchase_price: 0,
      sale_price: 0,
      opening_stock: 0,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.item_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    setFormData({
      item_name: item.item_name,
      grade: item.grade || '',
      pack_size: item.pack_size,
      purchase_price: item.purchase_price,
      sale_price: item.sale_price,
      opening_stock: item.opening_stock,
    });
    setShowAddForm(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this item?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        await apiItems.import(file);
        queryClient.invalidateQueries({ queryKey: ['items'] });
        alert('Items imported successfully!');
      } catch (err: any) {
        alert('Error importing file: ' + (err.response?.data?.detail || err.message));
      }
    }
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
            <h1 className="text-3xl font-bold text-gray-900">Items</h1>
            <div className="flex gap-3">
              <label className="cursor-pointer">
                <Input type="file" accept=".xlsx,.xls" onChange={handleFileUpload} className="hidden" />
                <Button variant="outline">
                  <Upload className="w-4 h-4 mr-2" />
                  Import Excel
                </Button>
              </label>
              <Button onClick={() => { setShowAddForm(true); setEditingItem(null); resetForm(); }}>
                <Plus className="w-4 h-4 mr-2" />
                Add Item
              </Button>
            </div>
          </div>

          {showAddForm && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>{editingItem ? 'Edit Item' : 'Add New Item'}</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="item_name">Item Name *</Label>
                    <Input
                      id="item_name"
                      value={formData.item_name}
                      onChange={(e) => setFormData({ ...formData, item_name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="grade">Grade</Label>
                    <Input
                      id="grade"
                      value={formData.grade}
                      onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="pack_size">Pack Size (Liters) *</Label>
                    <Input
                      id="pack_size"
                      type="number"
                      step="0.1"
                      value={formData.pack_size}
                      onChange={(e) => setFormData({ ...formData, pack_size: parseFloat(e.target.value) })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="purchase_price">Purchase Price *</Label>
                    <Input
                      id="purchase_price"
                      type="number"
                      step="0.01"
                      value={formData.purchase_price}
                      onChange={(e) => setFormData({ ...formData, purchase_price: parseFloat(e.target.value) })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="sale_price">Sale Price *</Label>
                    <Input
                      id="sale_price"
                      type="number"
                      step="0.01"
                      value={formData.sale_price}
                      onChange={(e) => setFormData({ ...formData, sale_price: parseFloat(e.target.value) })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="opening_stock">Opening Stock</Label>
                    <Input
                      id="opening_stock"
                      type="number"
                      step="1"
                      value={formData.opening_stock}
                      onChange={(e) => setFormData({ ...formData, opening_stock: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div className="col-span-2 flex gap-3">
                    <Button type="submit">{editingItem ? 'Update' : 'Add'} Item</Button>
                    <Button type="button" variant="outline" onClick={() => { setShowAddForm(false); setEditingItem(null); resetForm(); }}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>All Items ({items?.length || 0})</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item Name</TableHead>
                    <TableHead>Grade</TableHead>
                    <TableHead>Size (L)</TableHead>
                    <TableHead className="text-right">Purchase Price</TableHead>
                    <TableHead className="text-right">Sale Price</TableHead>
                    <TableHead className="text-right">Opening Stock</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items?.map((item) => (
                    <TableRow key={item.item_id}>
                      <TableCell className="font-medium">{item.item_name}</TableCell>
                      <TableCell>{item.grade || '-'}</TableCell>
                      <TableCell>{item.pack_size}</TableCell>
                      <TableCell className="text-right">Rs. {item.purchase_price}</TableCell>
                      <TableCell className="text-right">Rs. {item.sale_price}</TableCell>
                      <TableCell className="text-right">{item.opening_stock}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(item)}>
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(item.item_id)}>
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </TableCell>
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
