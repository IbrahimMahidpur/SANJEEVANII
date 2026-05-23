import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { CalendarIcon, MapPinIcon, BeakerIcon } from '@heroicons/react/24/outline';

const VaccineSection = () => {
  const [pincode, setPincode] = useState('');
  const [centers, setCenters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);

  const getTodayDate = () => {
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const yyyy = today.getFullYear();
    return `${dd}-${mm}-${yyyy}`;
  };

  const fetchCenters = async (showLoading = true) => {
    if (!pincode || pincode.length !== 6) return;

    if (showLoading) setLoading(true);
    setError('');

    try {
      const date = getTodayDate();
      const data = await apiClient.getVaccineCenters(pincode, date);
      setCenters(data.centers || []);
      if (data.centers.length === 0 && showLoading) {
        setError('No vaccine centers found for this pincode');
      }
    } catch (err) {
      console.error(err);
      if (showLoading) setError('Failed to fetch vaccine centers');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  // Auto-refresh logic
  useEffect(() => {
    let interval;
    if (autoRefresh && pincode.length === 6) {
      interval = setInterval(() => fetchCenters(false), 30000); // Refresh every 30s
    }
    return () => clearInterval(interval);
  }, [autoRefresh, pincode]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchCenters(true);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span className="text-3xl">💉</span> Vaccine Availability
          </h2>
          <p className="text-gray-500 mt-1">Real-time slot availability from CoWIN</p>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            Auto-refresh (30s)
          </label>
        </div>
      </div>

      <form onSubmit={handleSearch} className="flex gap-4 mb-8">
        <div className="relative flex-1 max-w-md">
          <MapPinIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Enter 6-digit Pincode"
            value={pincode}
            onChange={(e) => setPincode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        <button
          type="submit"
          disabled={loading || pincode.length !== 6}
          className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-primary-500/30"
        >
          {loading ? 'Searching...' : 'Check Availability'}
        </button>
      </form>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 flex items-center gap-2"
        >
          <span>⚠️</span> {error}
        </motion.div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {loading ? (
            // Skeleton Loading
            [...Array(3)].map((_, i) => (
              <motion.div
                key={`skeleton-${i}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="bg-gray-50 rounded-xl p-6 border border-gray-100 animate-pulse"
              >
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4" />
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/3" />
              </motion.div>
            ))
          ) : (
            centers.map((center) => (
              <motion.div
                key={center.center_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow group"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {center.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">{center.address}</p>
                  </div>
                  <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-md font-mono">
                    {center.pincode}
                  </span>
                </div>

                <div className="space-y-3">
                  {center.sessions.map((session, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-3 text-sm">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-700 flex items-center gap-1">
                          <CalendarIcon className="w-4 h-4" />
                          {session.date}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${session.available_capacity > 0
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                          }`}>
                          {session.available_capacity > 0 ? 'Available' : 'Booked'}
                        </span>
                      </div>

                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <BeakerIcon className="w-3 h-3" />
                          {session.vaccine}
                        </span>
                        <span>Age: {session.min_age_limit}+</span>
                      </div>

                      {session.available_capacity > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-200 flex justify-between text-xs">
                          <span className="text-green-600 font-medium">
                            {session.available_capacity} doses left
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default VaccineSection;
