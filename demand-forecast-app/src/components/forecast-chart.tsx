'use client';

import React, { useRef } from 'react';
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ForecastSeries } from '@/lib/data-utils';
import { toPng } from 'html-to-image';

interface ForecastChartProps {
  actualData: ForecastSeries[];
  forecastData: Array<{
    ds: string;
    yhat: number;
    yhat_lower: number;
    yhat_upper: number;
  }>;
  demandColumn: string;
}

interface ChartDataPoint {
  date: string;
  formattedDate: string;
  actual?: number;
  forecast?: number;
  lower?: number;
  upper?: number;
  isForecast: boolean;
}

export function ForecastChart({ actualData, forecastData, demandColumn }: ForecastChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  // Combine actual and forecast data
  const chartData: ChartDataPoint[] = [
    ...actualData.map(point => ({
      date: point.ds,
      formattedDate: format(parseISO(point.ds), 'MMM yyyy'),
      actual: point.y,
      isForecast: false
    })),
    ...forecastData.map(point => ({
      date: point.ds,
      formattedDate: format(parseISO(point.ds), 'MMM yyyy'),
      forecast: point.yhat,
      lower: point.yhat_lower,
      upper: point.yhat_upper,
      isForecast: true
    }))
  ].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const forecastStartDate = forecastData.length > 0 ? forecastData[0].ds : null;

  const handleDownloadPNG = async () => {
    if (!chartRef.current) return;

    try {
      const dataUrl = await toPng(chartRef.current, {
        quality: 1.0,
        backgroundColor: 'white',
        width: chartRef.current.offsetWidth,
        height: chartRef.current.offsetHeight,
      });

      const link = document.createElement('a');
      link.download = `demand-forecast-${new Date().toISOString().split('T')[0]}.png`;
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('Error generating PNG:', error);
    }
  };

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[]; label?: string }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="font-medium">{data.formattedDate}</p>
          {data.actual !== undefined && (
            <p className="text-blue-600 dark:text-blue-400">
              <span className="inline-block w-3 h-3 bg-blue-600 rounded-full mr-2"></span>
              Actual: {data.actual.toLocaleString()}
            </p>
          )}
          {data.forecast !== undefined && (
            <>
              <p className="text-orange-600 dark:text-orange-400">
                <span className="inline-block w-3 h-3 bg-orange-600 rounded-full mr-2"></span>
                Forecast: {data.forecast.toLocaleString()}
              </p>
              {data.lower !== undefined && data.upper !== undefined && (
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  95% CI: {data.lower.toLocaleString()} - {data.upper.toLocaleString()}
                </p>
              )}
            </>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Demand Forecast</CardTitle>
          <CardDescription>
            Historical data vs forecast for {demandColumn}
          </CardDescription>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleDownloadPNG}
          className="flex items-center space-x-2"
        >
          <Download className="h-4 w-4" />
          <span>Download PNG</span>
        </Button>
      </CardHeader>
      <CardContent>
        <div ref={chartRef} className="w-full bg-background">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="formattedDate" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => value.toLocaleString()}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Confidence interval area */}
              <Area
                type="monotone"
                dataKey="upper"
                stackId="ci"
                stroke="transparent"
                fill="url(#confidenceGradient)"
                fillOpacity={0.2}
              />
              <Area
                type="monotone"
                dataKey="lower"
                stackId="ci"
                stroke="transparent"
                fill="url(#confidenceGradient)"
                fillOpacity={0.2}
              />
              
              {/* Actual data line */}
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#2563eb"
                strokeWidth={2}
                dot={{ r: 3, fill: '#2563eb' }}
                connectNulls={false}
                name="Actual"
              />
              
              {/* Forecast data line */}
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#ea580c"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ r: 3, fill: '#ea580c' }}
                connectNulls={false}
                name="Forecast"
              />
              
              {/* Reference line to separate actual from forecast */}
              {forecastStartDate && (
                <ReferenceLine
                  x={format(parseISO(forecastStartDate), 'MMM yyyy')}
                  stroke="#64748b"
                  strokeDasharray="2 2"
                  strokeOpacity={0.5}
                />
              )}
              
              {/* Gradient definitions */}
              <defs>
                <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ea580c" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#ea580c" stopOpacity={0.05} />
                </linearGradient>
              </defs>
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 text-sm text-muted-foreground space-y-1">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-blue-600"></div>
              <span>Historical Data</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-orange-600 border-dashed border-t-2 border-orange-600"></div>
              <span>Forecast</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-2 bg-orange-600 opacity-20"></div>
              <span>95% Confidence Interval</span>
            </div>
          </div>
          <p>
            Showing {actualData.length} historical data points and {forecastData.length} forecast periods
          </p>
        </div>
      </CardContent>
    </Card>
  );
}