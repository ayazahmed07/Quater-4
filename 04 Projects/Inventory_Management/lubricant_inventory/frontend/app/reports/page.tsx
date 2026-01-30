'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Sidebar } from '@/components/sidebar';
import { apiReports } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { FileDown } from 'lucide-react';
import * as XLSX from 'xlsx';

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState('stock-comparison');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: stockComparison } = useQuery({
    queryKey: ['stock-comparison'],
    queryFn: apiReports.getStockComparison,
    enabled: activeTab === 'stock-comparison',
  });

  const { data: currentStock } = useQuery({
    queryKey: ['current-stock-report'],
    queryFn: apiReports.getCurrentStock,
    enabled: activeTab === 'current-stock',
  });

  const { data: salesReport } = useQuery({
    queryKey: ['sales-report', startDate, endDate],
    queryFn: () => apiReports.getSales(startDate, endDate),
    enabled: activeTab === 'sales',
  });

  const { data: purchaseReport } = useQuery({
    queryKey: ['purchase-report', startDate, endDate],
    queryFn: () => apiReports.getPurchases(startDate, endDate),
    enabled: activeTab === 'purchases',
  });

  const exportToExcel = (data: any[], filename: string) => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Report');
    XLSX.writeFile(wb, filename);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Reports</h1>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <Button
              variant={activeTab === 'stock-comparison' ? 'default' : 'outline'}
              onClick={() => setActiveTab('stock-comparison')}
            >
              Stock Comparison
            </Button>
            <Button
              variant={activeTab === 'current-stock' ? 'default' : 'outline'}
              onClick={() => setActiveTab('current-stock')}
            >
              Current Stock
            </Button>
            <Button
              variant={activeTab === 'sales' ? 'default' : 'outline'}
              onClick={() => setActiveTab('sales')}
            >
              Sales Report
            </Button>
            <Button
              variant={activeTab === 'purchases' ? 'default' : 'outline'}
              onClick={() => setActiveTab('purchases')}
            >
              Purchase Report
            </Button>
          </div>

          {/* Stock Comparison Report */}
          {activeTab === 'stock-comparison' && stockComparison && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">Total Items</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stockComparison.summary.total_items}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">Shortage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">{stockComparison.summary.items_with_shortage}</div>
                    <p className="text-xs text-gray-500">Rs. {stockComparison.summary.total_shortage_value.toFixed(2)}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">Excess</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">{stockComparison.summary.items_with_excess}</div>
                    <p className="text-xs text-gray-500">Rs. {stockComparison.summary.total_excess_value.toFixed(2)}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">Matching</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stockComparison.summary.items_matching}</div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Stock Comparison Details</CardTitle>
                  <Button size="sm" onClick={() => exportToExcel(stockComparison.items, `stock-comparison-${Date.now()}.xlsx`)}>
                    <FileDown className="w-4 h-4 mr-2" />
                    Export Excel
                  </Button>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Item Name</TableHead>
                        <TableHead>System Stock</TableHead>
                        <TableHead>Physical Stock</TableHead>
                        <TableHead>Difference</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Value Impact</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {stockComparison.items.map((item) => (
                        <TableRow key={item.item_id}>
                          <TableCell className="font-medium">{item.item_name}</TableCell>
                          <TableCell>{item.system_stock.toFixed(2)}</TableCell>
                          <TableCell>{item.physical_stock ?? '-'}</TableCell>
                          <TableCell>{item.difference?.toFixed(2) ?? '-'}</TableCell>
                          <TableCell>
                            <span className={`px-2 py-1 rounded text-xs ${
                              item.status === 'SHORTAGE' ? 'bg-red-100 text-red-800' :
                              item.status === 'EXCESS' ? 'bg-green-100 text-green-800' :
                              item.status === 'MATCH' ? 'bg-blue-100 text-blue-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {item.status}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            {item.value_impact ? `Rs. ${item.value_impact.toFixed(2)}` : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </>
          )}

          {/* Current Stock Report */}
          {activeTab === 'current-stock' && currentStock && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Current Stock Report</CardTitle>
                <Button size="sm" onClick={() => exportToExcel(currentStock, `current-stock-${Date.now()}.xlsx`)}>
                  <FileDown className="w-4 h-4 mr-2" />
                  Export Excel
                </Button>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Item Name</TableHead>
                      <TableHead>Grade</TableHead>
                      <TableHead>Size (L)</TableHead>
                      <TableHead className="text-right">Stock</TableHead>
                      <TableHead className="text-right">Purchase Price</TableHead>
                      <TableHead className="text-right">Sale Price</TableHead>
                      <TableHead className="text-right">Stock Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentStock.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{item.item_name}</TableCell>
                        <TableCell>{item.grade || '-'}</TableCell>
                        <TableCell>{item.pack_size}</TableCell>
                        <TableCell className="text-right">{item.system_stock}</TableCell>
                        <TableCell className="text-right">Rs. {item.purchase_price}</TableCell>
                        <TableCell className="text-right">Rs. {item.sale_price}</TableCell>
                        <TableCell className="text-right">Rs. {item.stock_value.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {/* Sales Report */}
          {activeTab === 'sales' && (
            <>
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle>Filter by Date Range</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 items-end">
                    <div>
                      <Label htmlFor="sales-start">Start Date</Label>
                      <Input
                        id="sales-start"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="sales-end">End Date</Label>
                      <Input
                        id="sales-end"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {salesReport && salesReport.length > 0 && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Sales Report ({salesReport.length} records)</CardTitle>
                    <Button size="sm" onClick={() => exportToExcel(salesReport, `sales-report-${Date.now()}.xlsx`)}>
                      <FileDown className="w-4 h-4 mr-2" />
                      Export Excel
                    </Button>
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
                        {salesReport.map((sale, index) => (
                          <TableRow key={index}>
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
              )}
            </>
          )}

          {/* Purchase Report */}
          {activeTab === 'purchases' && (
            <>
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle>Filter by Date Range</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 items-end">
                    <div>
                      <Label htmlFor="purchase-start">Start Date</Label>
                      <Input
                        id="purchase-start"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="purchase-end">End Date</Label>
                      <Input
                        id="purchase-end"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {purchaseReport && purchaseReport.length > 0 && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Purchase Report ({purchaseReport.length} records)</CardTitle>
                    <Button size="sm" onClick={() => exportToExcel(purchaseReport, `purchase-report-${Date.now()}.xlsx`)}>
                      <FileDown className="w-4 h-4 mr-2" />
                      Export Excel
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead>Invoice No</TableHead>
                          <TableHead>Item Name</TableHead>
                          <TableHead className="text-right">Quantity</TableHead>
                          <TableHead className="text-right">Rate</TableHead>
                          <TableHead className="text-right">Total Value</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {purchaseReport.map((purchase, index) => (
                          <TableRow key={index}>
                            <TableCell>{purchase.date}</TableCell>
                            <TableCell>{purchase.invoice_no}</TableCell>
                            <TableCell>{purchase.item_name}</TableCell>
                            <TableCell className="text-right">{purchase.quantity}</TableCell>
                            <TableCell className="text-right">Rs. {purchase.rate}</TableCell>
                            <TableCell className="text-right">Rs. {purchase.total_value.toFixed(2)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
