// Geolocation Hook for Pharmacy Support
import { useState, useEffect } from 'react';

interface Location {
  lat: number;
  lng: number;
}

const DEFAULT_LOCATION: Location = { lat: 22.7196, lng: 75.8577 }; // Indore fallback

export function useGeolocation() {
  const [location, setLocation] = useState<Location | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('🌍 Detecting your exact location...');

    if (!navigator.geolocation) {
      setError('Geolocation not supported');
      setLocation(DEFAULT_LOCATION);
      setLoading(false);
      return;
    }

    const successHandler = (position: GeolocationPosition) => {
      const userLoc = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      console.log('✅ Your location:', userLoc);
      console.log(`📍 Accuracy: ${position.coords.accuracy}m`);
      setLocation(userLoc);
      setLoading(false);
      setError('');
    };

    const errorHandler = (err: GeolocationPositionError) => {
      console.warn('⚠️ Location error:', err.message);
      setError(`Location access denied. Using default location (Indore).`);
      setLocation(DEFAULT_LOCATION);
      setLoading(false);
    };

    navigator.geolocation.getCurrentPosition(
      successHandler,
      errorHandler,
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }, []);

  const refreshLocation = () => {
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
        setLoading(false);
      },
      () => {
        setLoading(false);
      }
    );
  };

  return { location, loading, error, refreshLocation };
}

export default useGeolocation;
