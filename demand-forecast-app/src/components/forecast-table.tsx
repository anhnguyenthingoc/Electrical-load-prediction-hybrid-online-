'use client';

import React from 'react';
import { format, parseISO } from 'date-fns';
import { Download, FileText } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface ForecastTableProps {
  forecastData: Array<{
    ds: string;
    yhat: number;
    yhat_lower: number;
    yhat_upper: number;
  }>;
  demandColumn: string;
}

export function ForecastTable({ forecastData, demandColumn }: ForecastTableProps) {
  const handleExportCSV = () => {
    const headers = ['Date', 'Forecast', 'Lower Bound (95%)', 'Upper Bound (95%)'];
    const csvContent = [
      headers.join(','),
      ...forecastData.map(row => [
        row.ds,
        row.yhat.toFixed(2),
        row.yhat_lower.toFixed(2),
        row.yhat_upper.toFixed(2)
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `demand-forecast-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (forecastData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Forecast Results</CardTitle>
          <CardDescription>No forecast data available</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Forecast Results</CardTitle>
          <CardDescription>
            Detailed forecast values for {demandColumn} with confidence intervals
          </CardDescription>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleExportCSV}
          className="flex items-center space-x-2"
        >
          <Download className="h-4 w-4" />
          <span>Export CSV</span>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Forecast</TableHead>
                <TableHead className="text-right">Lower Bound (95%)</TableHead>
                <TableHead className="text-right">Upper Bound (95%)</TableHead>
                <TableHead className="text-right">Range</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {forecastData.map((row) => {
                const range = row.yhat_upper - row.yhat_lower;
                const rangePercent = ((range / row.yhat) * 100);
                
                return (
                  <TableRow key={row.ds}>
                    <TableCell className="font-medium">
                      {format(parseISO(row.ds), 'MMM yyyy')}
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {row.yhat.toLocaleString(undefined, { 
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0 
                      })}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {row.yhat_lower.toLocaleString(undefined, { 
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0 
                      })}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {row.yhat_upper.toLocaleString(undefined, { 
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0 
                      })}
                    </TableCell>
                    <TableCell className="text-right text-sm text-muted-foreground">
                      ±{rangePercent.toFixed(0)}%
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
        
        <div className="mt-4 space-y-2 text-sm text-muted-foreground">
          <div className="flex justify-between">
            <span>Total forecast periods:</span>
            <span className="font-medium">{forecastData.length} months</span>
          </div>
          <div className="flex justify-between">
            <span>Average forecast:</span>
            <span className="font-medium">
              {(forecastData.reduce((sum, row) => sum + row.yhat, 0) / forecastData.length).toLocaleString(undefined, { 
                minimumFractionDigits: 0,
                maximumFractionDigits: 0 
              })}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Forecast range:</span>
            <span className="font-medium">
              {Math.min(...forecastData.map(r => r.yhat)).toLocaleString()} - {Math.max(...forecastData.map(r => r.yhat)).toLocaleString()}
            </span>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-muted/30 rounded-lg">
          <div className="flex items-start space-x-2">
            <FileText className="h-4 w-4 mt-0.5 text-muted-foreground" />
            <div className="text-sm text-muted-foreground">
              <p className="font-medium mb-1">About this forecast:</p>
              <ul className="space-y-1 text-xs">
                <li>• Confidence intervals represent 95% prediction uncertainty</li>
                <li>• Forecasts are based on historical trends and patterns</li>
                <li>• External factors may affect actual results</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}