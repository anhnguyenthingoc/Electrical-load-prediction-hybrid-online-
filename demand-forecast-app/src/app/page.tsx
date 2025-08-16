'use client';

import React, { useState } from 'react';
import { BarChart3, TrendingUp, Calendar, Settings } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ModeToggle } from '@/components/mode-toggle';
import { FileUpload } from '@/components/file-upload';
import { ForecastChart } from '@/components/forecast-chart';
import { ForecastTable } from '@/components/forecast-table';
import { DataRow, convertToForecastSeries, ForecastSeries } from '@/lib/data-utils';
import { ForecastRequest, ForecastResponse } from '@/app/api/forecast/route';

interface UploadedData {
  data: DataRow[];
  columns: string[];
  dateColumns: string[];
  numericColumns: string[];
}

interface ForecastState {
  isLoading: boolean;
  error: string | null;
  results: ForecastResponse | null;
  actualData: ForecastSeries[];
}

export default function Home() {
  const [uploadedData, setUploadedData] = useState<UploadedData | null>(null);
  const [selectedDateColumn, setSelectedDateColumn] = useState<string>('');
  const [selectedDemandColumn, setSelectedDemandColumn] = useState<string>('');
  const [forecastHorizon, setForecastHorizon] = useState<number>(6);
  const [forecastState, setForecastState] = useState<ForecastState>({
    isLoading: false,
    error: null,
    results: null,
    actualData: []
  });

  const handleDataLoaded = (data: UploadedData) => {
    setUploadedData(data);
    // Auto-select first date and numeric columns
    if (data.dateColumns.length > 0) {
      setSelectedDateColumn(data.dateColumns[0]);
    }
    if (data.numericColumns.length > 0) {
      setSelectedDemandColumn(data.numericColumns[0]);
    }
    // Reset forecast state
    setForecastState({
      isLoading: false,
      error: null,
      results: null,
      actualData: []
    });
  };

  const handleGenerateForecast = async () => {
    if (!uploadedData || !selectedDateColumn || !selectedDemandColumn) {
      return;
    }

    setForecastState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Convert data to forecast series
      const series = convertToForecastSeries(
        uploadedData.data,
        selectedDateColumn,
        selectedDemandColumn
      );

      if (series.length === 0) {
        throw new Error('No valid data points found for the selected columns');
      }

      // Call forecast API
      const requestBody: ForecastRequest = {
        series,
        horizon: forecastHorizon,
        demandColumn: selectedDemandColumn
      };

      const response = await fetch('/api/forecast', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate forecast');
      }

      const results: ForecastResponse = await response.json();

      setForecastState({
        isLoading: false,
        error: null,
        results,
        actualData: series
      });
    } catch (error) {
      setForecastState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'An unexpected error occurred'
      }));
    }
  };

  const canGenerateForecast = uploadedData && selectedDateColumn && selectedDemandColumn && !forecastState.isLoading;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
              <TrendingUp className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Demand Forecasting</h1>
              <p className="text-sm text-muted-foreground">AI-powered demand prediction</p>
            </div>
          </div>
          <ModeToggle />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Upload Section */}
        <FileUpload onDataLoaded={handleDataLoaded} />

        {/* Configuration Section */}
        {uploadedData && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Forecast Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure your forecast parameters and select the columns to analyze
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Date Column</label>
                  <Select value={selectedDateColumn} onValueChange={setSelectedDateColumn}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select date column" />
                    </SelectTrigger>
                    <SelectContent>
                      {uploadedData.dateColumns.map(column => (
                        <SelectItem key={column} value={column}>
                          {column}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Demand Column</label>
                  <Select value={selectedDemandColumn} onValueChange={setSelectedDemandColumn}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select demand column" />
                    </SelectTrigger>
                    <SelectContent>
                      {uploadedData.numericColumns.map(column => (
                        <SelectItem key={column} value={column}>
                          {column}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Forecast Periods (months)</label>
                  <Input
                    type="number"
                    min="1"
                    max="24"
                    value={forecastHorizon}
                    onChange={(e) => setForecastHorizon(Number(e.target.value))}
                    placeholder="6"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t">
                <div className="text-sm text-muted-foreground">
                  Ready to forecast {selectedDemandColumn || 'demand'} for the next {forecastHorizon} months
                </div>
                <Button
                  onClick={handleGenerateForecast}
                  disabled={!canGenerateForecast}
                  className="flex items-center space-x-2"
                >
                  {forecastState.isLoading ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <BarChart3 className="h-4 w-4" />
                      <span>Generate Forecast</span>
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {forecastState.error && (
          <Card className="border-red-200 bg-red-50 dark:bg-red-950">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2 text-red-700 dark:text-red-300">
                <div className="w-4 h-4 bg-red-500 rounded-full flex-shrink-0" />
                <p className="font-medium">Forecast Error</p>
              </div>
              <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                {forecastState.error}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Results Section */}
        {forecastState.results && forecastState.actualData.length > 0 && (
          <div className="space-y-8">
            <ForecastChart
              actualData={forecastState.actualData}
              forecastData={forecastState.results.forecast}
              demandColumn={selectedDemandColumn}
            />
            
            <ForecastTable
              forecastData={forecastState.results.forecast}
              demandColumn={selectedDemandColumn}
            />
          </div>
        )}

        {/* Getting Started Guide */}
        {!uploadedData && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Getting Started</span>
              </CardTitle>
              <CardDescription>
                Follow these steps to generate your demand forecast
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-lg font-bold text-primary">1</span>
                  </div>
                  <h3 className="font-medium">Upload Your Data</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload a CSV or Excel file with historical demand data and dates
                  </p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-lg font-bold text-primary">2</span>
                  </div>
                  <h3 className="font-medium">Configure Settings</h3>
                  <p className="text-sm text-muted-foreground">
                    Select your date and demand columns, set forecast periods
                  </p>
                </div>
                
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <span className="text-lg font-bold text-primary">3</span>
                  </div>
                  <h3 className="font-medium">Generate Forecast</h3>
                  <p className="text-sm text-muted-foreground">
                    View interactive charts and export your forecast results
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t mt-16">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          Built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui
        </div>
      </footer>
    </div>
  );
}
