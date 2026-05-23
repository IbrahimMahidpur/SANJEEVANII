import React, { useState } from 'react';
import { Menu, Upload, FileText, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function PrescriptionAnalysis() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResult(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a prescription image first');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('prescription_image', selectedFile);

      // Call Flask backend (running on port 5001)
      const response = await fetch('http://localhost:5001/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        let errorMsg = 'Failed to analyze prescription';
        try {
          const errorData = await response.json();
          if (errorData.error) {
            errorMsg = errorData.error;
            if (errorData.details) {
              errorMsg += `: ${errorData.details}`;
            }
          }
        } catch (e) {
          // Fallback if response is not JSON
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();

      // Step 2: Refine with LLM if text was extracted
      if (data.raw_text) {
        try {
          const refineResponse = await fetch('http://localhost:5000/api/prescription/refine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: data.raw_text })
          });

          if (refineResponse.ok) {
            const refinedData = await refineResponse.json();
            // Merge refined data with OCR results
            setResult({ ...data, refined: refinedData });
          } else {
            setResult(data); // Fallback to basic OCR
          }
        } catch (e) {
          console.error("Refinement failed:", e);
          setResult(data);
        }
      } else {
        setResult(data);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze prescription');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Link to="/">
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <Menu className="w-6 h-6 text-gray-700" />
                </button>
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">Prescription Analysis</h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>AI-Powered OCR</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-blue-500 rounded-xl">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Upload Prescription</h2>
                  <p className="text-sm text-gray-600">Supports JPG, PNG, PDF formats</p>
                </div>
              </div>

              {/* File Upload */}
              <div className="relative">
                <input
                  type="file"
                  accept="image/*,.pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-blue-300 rounded-xl cursor-pointer bg-white hover:bg-blue-50 transition-colors"
                >
                  {preview ? (
                    <img src={preview} alt="Preview" className="max-h-full max-w-full object-contain rounded-lg" />
                  ) : (
                    <div className="text-center">
                      <Upload className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                      <p className="text-sm font-medium text-gray-700">Click to upload prescription</p>
                      <p className="text-xs text-gray-500 mt-2">or drag and drop</p>
                    </div>
                  )}
                </label>
              </div>

              {selectedFile && (
                <div className="mt-4 p-4 bg-white rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-gray-700">Selected: {selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              )}

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!selectedFile || isAnalyzing}
                className="w-full mt-6 px-6 py-4 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    Analyze Prescription
                  </>
                )}
              </button>
            </div>

            {/* Info Card */}
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">How it works</h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Upload a clear image of your prescription</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>AI extracts medicine names, dosages, and instructions</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Get structured data for easy reference</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">Error</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            )}

            {result && (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5" />
                    Analysis Complete
                  </h3>
                </div>

                <div className="p-6 space-y-6">
                  {/* Refined Data Display */}
                  {result.refined ? (
                    <>
                      {/* Patient & Doctor Info */}
                      <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100 mb-6">
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Patient</p>
                          <p className="font-medium text-gray-900">{result.refined.patient_name || 'Not detected'}</p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Doctor</p>
                          <p className="font-medium text-gray-900">{result.refined.doctor_name || 'Not detected'}</p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Date</p>
                          <p className="font-medium text-gray-900">{result.refined.date || 'Not detected'}</p>
                        </div>
                      </div>

                      {/* Medicines List - Enhanced */}
                      <div className="mb-8">
                        <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                          <div className="w-1 h-5 bg-blue-500 rounded-full"></div>
                          Prescribed Medicines
                        </h4>
                        <div className="space-y-4">
                          {result.refined.medicines && result.refined.medicines.length > 0 ? (
                            result.refined.medicines.map((med: any, idx: number) => (
                              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                                  <div>
                                    <h5 className="font-bold text-xl text-gray-900">{med.name}</h5>
                                    <p className="text-sm text-gray-500 mt-1">
                                      {med.type || 'Medicine'}
                                    </p>
                                  </div>
                                  <div className="flex flex-wrap gap-2">
                                    {med.dosage && (
                                      <span className="px-3 py-1 bg-blue-50 text-blue-700 text-sm font-medium rounded-full border border-blue-100 flex items-center gap-1">
                                        💊 Dosage: {med.dosage}
                                      </span>
                                    )}
                                    {med.duration && (
                                      <span className="px-3 py-1 bg-orange-50 text-orange-700 text-sm font-medium rounded-full border border-orange-100 flex items-center gap-1">
                                        ⏱️ Duration: {med.duration}
                                      </span>
                                    )}
                                  </div>
                                </div>

                                <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div>
                                    <p className="text-xs font-semibold text-gray-500 uppercase mb-1">When to take</p>
                                    <p className="text-gray-900 font-medium flex items-center gap-2">
                                      <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                                      {med.frequency || 'As directed'}
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-xs font-semibold text-gray-500 uppercase mb-1">How to take</p>
                                    <p className="text-gray-900 font-medium flex items-center gap-2">
                                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                                      {med.instructions || 'Follow doctor\'s advice'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="text-center py-8 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                              <p className="text-gray-500">No specific medicines detected in structured format.</p>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* General Instructions / Usage Guide */}
                      {result.refined.usage_guide && (
                        <div className="mb-6">
                          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <div className="w-1 h-5 bg-green-500 rounded-full"></div>
                            Simple Usage Guide
                          </h4>
                          <div className="bg-green-50 p-5 rounded-xl border border-green-100 text-green-900 leading-relaxed">
                            {result.refined.usage_guide}
                          </div>
                        </div>
                      )}

                      {/* Additional Notes */}
                      {result.refined.instructions && result.refined.instructions.length > 0 && (
                        <div className="mb-6">
                          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <div className="w-1 h-5 bg-gray-500 rounded-full"></div>
                            Doctor's Notes
                          </h4>
                          <ul className="list-disc list-inside space-y-2 text-gray-700 bg-gray-50 p-5 rounded-xl border border-gray-100">
                            {result.refined.instructions.map((inst: string, idx: number) => (
                              <li key={idx}>{inst}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Raw Text Toggle */}
                      <div className="mt-8 pt-6 border-t border-gray-200">
                        <details className="group">
                          <summary className="flex items-center gap-2 cursor-pointer text-sm text-gray-500 hover:text-gray-700 font-medium">
                            <span className="group-open:rotate-90 transition-transform">▶</span>
                            Show Original Extracted Text (Debug)
                          </summary>
                          <div className="mt-4 bg-gray-900 rounded-xl p-4 text-xs text-gray-300 font-mono whitespace-pre-wrap overflow-x-auto">
                            {result.raw_text}
                          </div>
                        </details>
                      </div>
                    </>
                  ) : (
                    // Fallback if refinement fails - still try to look nice
                    <div className="space-y-6">
                      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-yellow-800">
                        <p className="font-medium">AI Refinement Unavailable</p>
                        <p className="text-sm mt-1">We couldn't structure the data, but here is the text we found:</p>
                      </div>

                      {result.raw_text && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Extracted Text:</h4>
                          <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap font-mono">
                            {result.raw_text}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {!result && !error && (
              <div className="bg-gray-50 rounded-xl p-12 text-center border border-gray-200">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Upload and analyze a prescription to see results here</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
