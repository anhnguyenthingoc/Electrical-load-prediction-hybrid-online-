'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle } from 'lucide-react';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DataRow, detectColumnTypes } from '@/lib/data-utils';

interface FileUploadProps {
  onDataLoaded: (data: {
    data: DataRow[];
    columns: string[];
    dateColumns: string[];
    numericColumns: string[];
  }) => void;
}

interface FileStatus {
  status: 'idle' | 'processing' | 'success' | 'error';
  message?: string;
  fileName?: string;
}

export function FileUpload({ onDataLoaded }: FileUploadProps) {
  const [fileStatus, setFileStatus] = useState<FileStatus>({ status: 'idle' });

  const processCSV = (file: File): Promise<DataRow[]> => {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
        transform: (value) => value.trim() || null,
        complete: (results) => {
          if (results.errors.length > 0) {
            reject(new Error(`CSV parsing error: ${results.errors[0].message}`));
            return;
          }
          resolve(results.data as DataRow[]);
        },
        error: (error) => reject(error)
      });
    });
  };

  const processExcel = (file: File): Promise<DataRow[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target?.result;
          const workbook = XLSX.read(data, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { 
            header: 1,
            blankrows: false
          });

          if (jsonData.length < 2) {
            reject(new Error('File must contain at least a header row and one data row'));
            return;
          }

          const headers = (jsonData[0] as string[]).map(h => String(h).trim());
          const rows = jsonData.slice(1) as unknown[][];
          
          const parsedData: DataRow[] = rows.map(row => {
            const obj: DataRow = {};
            headers.forEach((header, index) => {
              obj[header] = row[index] !== undefined && row[index] !== null ? 
                String(row[index]).trim() || null : null;
            });
            return obj;
          }).filter(row => Object.values(row).some(val => val !== null && val !== ''));

          resolve(parsedData);
        } catch (error) {
          reject(new Error(`Excel parsing error: ${error instanceof Error ? error.message : 'Unknown error'}`));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
  };

  const processFile = useCallback(async (file: File) => {
    setFileStatus({ status: 'processing', fileName: file.name });

    try {
      let data: DataRow[];
      
      if (file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')) {
        data = await processCSV(file);
      } else if (
        file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.type === 'application/vnd.ms-excel' ||
        file.name.toLowerCase().endsWith('.xlsx') ||
        file.name.toLowerCase().endsWith('.xls')
      ) {
        data = await processExcel(file);
      } else {
        throw new Error('Unsupported file format. Please upload a CSV or Excel file.');
      }

      if (data.length === 0) {
        throw new Error('No data found in the file');
      }

      const columns = Object.keys(data[0]);
      if (columns.length === 0) {
        throw new Error('No columns found in the file');
      }

      const { dateColumns, numericColumns } = detectColumnTypes(data);

      if (dateColumns.length === 0) {
        throw new Error('No date columns detected. Please ensure your file has a date column in DD/MM/YYYY, MM/YYYY, or YYYY format.');
      }

      if (numericColumns.length === 0) {
        throw new Error('No numeric columns detected. Please ensure your file has at least one numeric column for demand data.');
      }

      setFileStatus({ 
        status: 'success', 
        fileName: file.name,
        message: `Successfully loaded ${data.length} rows with ${columns.length} columns`
      });

      onDataLoaded({
        data,
        columns,
        dateColumns,
        numericColumns
      });

    } catch (error) {
      setFileStatus({
        status: 'error',
        fileName: file.name,
        message: error instanceof Error ? error.message : 'Failed to process file'
      });
    }
  }, [onDataLoaded]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      processFile(acceptedFiles[0]);
    }
  }, [processFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const getStatusIcon = () => {
    switch (fileStatus.status) {
      case 'processing':
        return <div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Upload className="h-8 w-8 text-muted-foreground" />;
    }
  };

  const getStatusColor = () => {
    switch (fileStatus.status) {
      case 'success':
        return 'border-green-200 bg-green-50 dark:bg-green-950';
      case 'error':
        return 'border-red-200 bg-red-50 dark:bg-red-950';
      case 'processing':
        return 'border-blue-200 bg-blue-50 dark:bg-blue-950';
      default:
        return isDragActive ? 'border-primary bg-primary/5' : 'border-border';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Data File</CardTitle>
        <CardDescription>
          Upload a CSV or Excel file with date and demand data. 
          Supported date formats: DD/MM/YYYY, MM/YYYY, YYYY
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
            transition-colors duration-200 ${getStatusColor()}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            {getStatusIcon()}
            
            {fileStatus.status === 'idle' && (
              <>
                <div className="space-y-2">
                  <p className="text-lg font-medium">
                    {isDragActive ? 'Drop your file here' : 'Drag & drop your file here'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    or click to browse files
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <FileSpreadsheet className="h-4 w-4" />
                  <span>CSV, XLSX, XLS files (max 10MB)</span>
                </div>
              </>
            )}

            {fileStatus.status === 'processing' && (
              <div className="space-y-2">
                <p className="text-lg font-medium">Processing {fileStatus.fileName}...</p>
                <p className="text-sm text-muted-foreground">
                  Analyzing columns and data types
                </p>
              </div>
            )}

            {fileStatus.status === 'success' && (
              <div className="space-y-2">
                <p className="text-lg font-medium text-green-700 dark:text-green-300">
                  ✓ {fileStatus.fileName}
                </p>
                <p className="text-sm text-muted-foreground">
                  {fileStatus.message}
                </p>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setFileStatus({ status: 'idle' });
                  }}
                >
                  Upload Different File
                </Button>
              </div>
            )}

            {fileStatus.status === 'error' && (
              <div className="space-y-2">
                <p className="text-lg font-medium text-red-700 dark:text-red-300">
                  ✗ {fileStatus.fileName}
                </p>
                <p className="text-sm text-red-600 dark:text-red-400">
                  {fileStatus.message}
                </p>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setFileStatus({ status: 'idle' });
                  }}
                >
                  Try Again
                </Button>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}